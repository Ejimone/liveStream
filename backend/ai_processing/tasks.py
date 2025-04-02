import logging
import io
import os
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from classroom_integration.models import Material, Assignment

# Local imports
from .models import Document, Chunk, AssignmentDraft
from .text_extractor import TextExtractor
from .Rag import RAGSystem

logger = logging.getLogger(__name__)

@shared_task
def process_material_task(material_id, file_content_bytes=None):
    """
    Celery task to process a material file:
    1. Extract text from the file
    2. Create Document object with extracted text
    3. Trigger chunk and embedding generation
    
    Args:
        material_id (int): The ID of the material to process
        file_content_bytes (bytes, optional): Binary file content if already downloaded
            If None, material must have a local_path that can be read
    """
    try:
        # Get the material
        material = Material.objects.select_related('assignment').get(pk=material_id)
        
        # Update status
        material.processing_status = 'Processing'
        material.save(update_fields=['processing_status'])
        
        logger.info(f"Processing material {material_id}: {material.title}")
        
        # Get file content
        if file_content_bytes is None:
            if not material.local_path or not os.path.exists(material.local_path):
                logger.error(f"Material {material_id} has no file content and no valid local path")
                material.processing_status = 'Error'
                material.save(update_fields=['processing_status'])
                return f"Failed: No content for material {material_id}"
                
            # Read from local file
            with open(material.local_path, 'rb') as f:
                file_content_bytes = f.read()
        
        # Extract text
        file_name = material.title or f"material_{material_id}"
        extracted_text, metadata, page_count = TextExtractor.extract_text(file_content_bytes, file_name)
        
        if not extracted_text:
            logger.error(f"Failed to extract text from material {material_id}")
            material.processing_status = 'Error'
            material.save(update_fields=['processing_status'])
            return f"Failed: No text extracted from material {material_id}"
            
        logger.info(f"Successfully extracted {len(extracted_text)} characters from material {material_id}")
        
        # Create or update Document
        document, created = Document.objects.update_or_create(
            material=material,
            defaults={
                'raw_text': extracted_text,
                'page_count': page_count
            }
        )
        
        # Update material status
        material.processing_status = 'Chunking'
        material.save(update_fields=['processing_status'])
        
        # Trigger chunk and embedding task
        generate_chunks_and_embeddings_task.delay(document.id)
        
        return f"Successfully processed material {material_id}"
        
    except Material.DoesNotExist:
        logger.error(f"Material with ID {material_id} not found")
        return f"Failed: Material {material_id} not found"
    except Exception as e:
        logger.exception(f"Error processing material {material_id}: {e}")
        
        try:
            # Update material status to error
            material = Material.objects.get(pk=material_id)
            material.processing_status = 'Error'
            material.save(update_fields=['processing_status'])
        except Exception:
            pass
            
        return f"Failed to process material {material_id}: {str(e)}"


@shared_task
def generate_chunks_and_embeddings_task(document_id):
    """
    Generate text chunks and embeddings for a document.
    
    Args:
        document_id (int): The ID of the document to process
    """
    try:
        # Get document
        document = Document.objects.select_related('material__assignment').get(pk=document_id)
        material = document.material
        
        # Update status
        material.processing_status = 'Embedding'
        material.save(update_fields=['processing_status'])
        
        logger.info(f"Generating chunks and embeddings for document {document_id}")
        
        # Initialize RAG system
        rag = RAGSystem()
        
        # Process document
        success = rag.process_material_for_embedding(document)
        
        if not success:
            logger.error(f"Failed to generate chunks/embeddings for document {document_id}")
            material.processing_status = 'Error'
            material.save(update_fields=['processing_status'])
            return f"Failed to process document {document_id}"
            
        # Update material status
        material.processing_status = 'Processed'
        material.save(update_fields=['processing_status'])
        
        logger.info(f"Successfully generated chunks/embeddings for document {document_id}")
        
        # Check if all materials for this assignment are processed
        assignment = material.assignment
        unprocessed_materials = Material.objects.filter(
            assignment=assignment,
            processing_status__in=['Pending', 'Downloading', 'Downloaded', 'Processing', 'Chunking', 'Embedding']
        ).count()
        
        if unprocessed_materials == 0:
            # All materials processed, update assignment status
            if assignment.status == 'Processing':
                logger.info(f"All materials processed for assignment {assignment.id}, updating status to MaterialsReady")
                assignment.status = 'MaterialsReady'
                assignment.save(update_fields=['status'])
                
                # Trigger draft generation if configured to do so automatically
                if getattr(settings, 'AUTO_GENERATE_DRAFTS', False):
                    generate_assignment_draft_task.delay(assignment.id)
        
        return f"Successfully processed document {document_id}"
        
    except Document.DoesNotExist:
        logger.error(f"Document with ID {document_id} not found")
        return f"Failed: Document {document_id} not found"
    except Exception as e:
        logger.exception(f"Error generating chunks/embeddings for document {document_id}: {e}")
        
        try:
            # Update material status to error
            document = Document.objects.get(pk=document_id)
            document.material.processing_status = 'Error'
            document.material.save(update_fields=['processing_status'])
        except Exception:
            pass
            
        return f"Failed to process document {document_id}: {str(e)}"


@shared_task
def generate_assignment_draft_task(assignment_id):
    """
    Generate an AI draft for an assignment using the RAG system.
    
    Args:
        assignment_id (int): The ID of the assignment to generate a draft for
    """
    try:
        # Get assignment
        assignment = Assignment.objects.get(pk=assignment_id)
        
        # Check if materials are ready
        if assignment.status not in ['MaterialsReady', 'Error']:
            logger.error(f"Cannot generate draft for assignment {assignment_id} with status {assignment.status}")
            return f"Failed: Assignment {assignment_id} not ready for draft generation"
            
        # Update status
        assignment.status = 'GeneratingDraft'
        assignment.save(update_fields=['status'])
        
        logger.info(f"Generating draft for assignment {assignment_id}")
        
        # Initialize RAG system
        rag = RAGSystem()
        
        # Generate draft
        draft = rag.generate_draft_with_context(assignment)
        
        if not draft:
            logger.error(f"Failed to generate draft for assignment {assignment_id}")
            assignment.status = 'Error'
            assignment.save(update_fields=['status'])
            return f"Failed to generate draft for assignment {assignment_id}"
            
        logger.info(f"Successfully generated draft {draft.id} for assignment {assignment_id}")
        
        # Status is updated inside generate_draft_with_context
        
        return f"Successfully generated draft for assignment {assignment_id}"
        
    except Assignment.DoesNotExist:
        logger.error(f"Assignment with ID {assignment_id} not found")
        return f"Failed: Assignment {assignment_id} not found"
    except Exception as e:
        logger.exception(f"Error generating draft for assignment {assignment_id}: {e}")
        
        try:
            # Update assignment status to error
            assignment = Assignment.objects.get(pk=assignment_id)
            assignment.status = 'Error'
            assignment.save(update_fields=['status'])
        except Exception:
            pass
            
        return f"Failed to generate draft for assignment {assignment_id}: {str(e)}"


@shared_task
def finalize_and_submit_draft_task(draft_id):
    """
    Finalize an approved draft and submit it to Google Classroom.
    This task should only be triggered after user review and approval.
    
    Args:
        draft_id (int): The ID of the AssignmentDraft to submit
    """
    try:
        # Get draft
        draft = AssignmentDraft.objects.select_related('assignment').get(pk=draft_id)
        assignment = draft.assignment
        
        if not draft.is_final or not draft.final_content_for_submission:
            logger.error(f"Draft {draft_id} is not final or has no final content")
            return f"Failed: Draft {draft_id} is not ready for submission"
            
        # Update status
        assignment.status = 'GeneratingPDF'
        assignment.save(update_fields=['status'])
        
        logger.info(f"Generating PDF for draft {draft_id} (assignment {assignment.id})")
        
        # Generate PDF (This would be implemented in another utility)
        # pdf_file_path = generate_pdf_from_draft(draft)
        pdf_file_path = None  # Placeholder, would be implemented
        
        if not pdf_file_path:
            logger.error(f"Failed to generate PDF for draft {draft_id}")
            assignment.status = 'Error'
            assignment.save(update_fields=['status'])
            return f"Failed to generate PDF for draft {draft_id}"
            
        # Update status
        assignment.status = 'Submitting'
        assignment.save(update_fields=['status'])
        
        logger.info(f"Submitting assignment {assignment.id} to Google Classroom")
        
        # Submit to Google Classroom (This would call the classroom_integration service)
        # from classroom_integration.services import submit_assignment_work
        # success = submit_assignment_work(assignment.course.owner, assignment.course.google_id, assignment.google_id, pdf_file_path)
        success = True  # Placeholder, would call actual submission function
        
        if not success:
            logger.error(f"Failed to submit assignment {assignment.id}")
            assignment.status = 'Error'
            assignment.save(update_fields=['status'])
            return f"Failed to submit assignment {assignment.id}"
            
        # Update draft and assignment status
        draft.submitted = True
        draft.submission_timestamp = timezone.now()
        draft.save(update_fields=['submitted', 'submission_timestamp'])
        
        assignment.status = 'Submitted'
        assignment.save(update_fields=['status'])
        
        logger.info(f"Successfully submitted assignment {assignment.id}")
        
        # Clean up temporary PDF file
        # if os.path.exists(pdf_file_path):
        #     os.remove(pdf_file_path)
        
        return f"Successfully submitted assignment {assignment.id}"
        
    except AssignmentDraft.DoesNotExist:
        logger.error(f"Draft with ID {draft_id} not found")
        return f"Failed: Draft {draft_id} not found"
    except Exception as e:
        logger.exception(f"Error submitting draft {draft_id}: {e}")
        
        try:
            # Update assignment status to error
            draft = AssignmentDraft.objects.get(pk=draft_id)
            draft.assignment.status = 'Error'
            draft.assignment.save(update_fields=['status'])
        except Exception:
            pass
            
        return f"Failed to submit draft {draft_id}: {str(e)}"