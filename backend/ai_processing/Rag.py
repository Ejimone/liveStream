import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

# Import Google Generative AI for Gemini
import google.generativeai as genai
from django.conf import settings

# Import for embeddings
from sentence_transformers import SentenceTransformer

# FAISS for vector storage/search
import faiss

# Local imports
from .models import Chunk, Document, AssignmentDraft
from classroom_integration.models import Assignment

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Retrieval-Augmented Generation system using Google's Gemini API.
    Retrieves relevant context chunks from the vector database and
    generates responses using Gemini.
    """
    
    def __init__(self):
        # Initialize Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize the embedding model (using Sentence Transformers)
        # This works without an API key and runs locally
        try:
            # Can use a larger model like 'all-mpnet-base-v2' for better quality
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            self.embedding_model = None
    
    def create_embedding(self, text: str) -> np.ndarray:
        """
        Create an embedding vector for the given text.
        
        Args:
            text (str): Text to embed
            
        Returns:
            numpy.ndarray: Embedding vector
        """
        if not self.embedding_model:
            logger.error("Embedding model not initialized")
            return None
            
        try:
            # Generate embedding and normalize
            embedding = self.embedding_model.encode(text)
            # Convert to unit vector (L2 normalization)
            faiss.normalize_L2(embedding.reshape(1, -1))
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None
    
    def retrieve_relevant_chunks(self, 
                               query_text: str, 
                               assignment: Assignment,
                               top_k: int = 5) -> List[Chunk]:
        """
        Retrieve the most relevant chunks for a query from all materials
        associated with the assignment's course.
        
        Args:
            query_text (str): The query text (e.g., assignment description)
            assignment (Assignment): The assignment object
            top_k (int): Number of chunks to retrieve
            
        Returns:
            List[Chunk]: List of retrieved chunks
        """
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query_text)
            if query_embedding is None:
                return []
                
            # Get all materials for this assignment's course
            # This includes materials from all assignments in the same course
            course = assignment.course
            materials_ids = course.assignments.values_list('materials__id', flat=True)
            
            # Get all document chunks
            chunks = Chunk.objects.filter(
                document__material_id__in=materials_ids
            ).order_by('document', 'chunk_index')
            
            if not chunks:
                logger.warning(f"No chunks found for assignment {assignment.id}")
                return []
                
            # Get all embeddings as a numpy array
            embeddings = []
            chunk_objects = []
            
            for chunk in chunks:
                if chunk.embedding_vector:
                    # Convert binary field to numpy array
                    embedding = np.frombuffer(chunk.embedding_vector, dtype=np.float32)
                    embeddings.append(embedding)
                    chunk_objects.append(chunk)
            
            if not embeddings:
                logger.warning("No valid embeddings found in chunks")
                return []
                
            # Create FAISS index (in-memory)
            embeddings_matrix = np.vstack(embeddings)
            dimension = embeddings_matrix.shape[1]
            
            index = faiss.IndexFlatIP(dimension)  # Inner product = cosine similarity for normalized vectors
            index.add(embeddings_matrix)
            
            # Search index
            scores, indices = index.search(query_embedding.reshape(1, -1), min(top_k, len(embeddings)))
            
            # Return chunks sorted by relevance score
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(chunk_objects) and scores[0][i] > 0:  # Ensure positive similarity
                    results.append((chunk_objects[idx], float(scores[0][i])))
            
            # Sort by score descending
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Return only the chunks
            return [chunk for chunk, score in results]
            
        except Exception as e:
            logger.exception(f"Error retrieving chunks: {str(e)}")
            return []
    
    def generate_draft_with_context(self, 
                                  assignment: Assignment,
                                  relevant_chunks: List[Chunk] = None) -> Optional[AssignmentDraft]:
        """
        Generate a draft for an assignment using the Gemini API,
        incorporating context from relevant chunks.
        
        Args:
            assignment (Assignment): The assignment to generate a draft for
            relevant_chunks (List[Chunk], optional): Pre-retrieved relevant chunks
                                                   If None, will retrieve chunks
                                                   
        Returns:
            Optional[AssignmentDraft]: The created draft object or None if failed
        """
        try:
            # Get assignment details
            assignment_title = assignment.title
            assignment_description = assignment.description or ""
            
            # If no chunks provided, retrieve them
            if relevant_chunks is None:
                # Use title + description as the query
                query = f"{assignment_title} {assignment_description}"
                relevant_chunks = self.retrieve_relevant_chunks(query, assignment)
            
            if not relevant_chunks:
                logger.warning(f"No relevant chunks found for assignment {assignment.id}")
            
            # Construct context from chunks
            context_texts = []
            for chunk in relevant_chunks:
                context_texts.append(f"--- Start of Material Section ---\n{chunk.text}\n--- End of Section ---")
            
            context = "\n\n".join(context_texts)
            
            # Craft prompt for Gemini
            prompt = f"""You are an AI assistant helping a student complete an assignment based on their course materials. You'll provide a detailed, well-structured response that directly answers the assignment prompt.

ASSIGNMENT DETAILS:
Title: {assignment_title}
Instructions: {assignment_description}

RELEVANT COURSE MATERIALS:
{context}

Based on the assignment prompt and the provided course materials, write a comprehensive response that:
1. Directly addresses all parts of the assignment
2. Uses information from the course materials to support your points
3. Is well-organized with clear structure
4. Includes examples or evidence from the course materials

DO NOT:
- Make up information not found in the materials
- Include personal opinions unless requested 
- Copy large sections verbatim from the materials

Your response should be in a format appropriate for the assignment (essay, report, analysis, etc.).

RESPONSE:"""

            # Generate response with Gemini
            generation_config = {
                "temperature": 0.2,  # Lower for more factual/deterministic answers
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,  # Adjust based on expected output length
            }
            
            # Log that we're making the API call
            logger.info(f"Generating draft for assignment {assignment.id} using Gemini")
            
            # Make the API call
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response or not hasattr(response, 'text'):
                logger.error(f"Failed to get valid response from Gemini for assignment {assignment.id}")
                return None
                
            generated_content = response.text
            
            # Create draft in database
            draft = AssignmentDraft.objects.create(
                assignment=assignment,
                ai_generated_content=generated_content,
                prompt_used=prompt
            )
            
            # Link the chunks used to generate the draft
            if relevant_chunks:
                draft.relevant_chunks.set(relevant_chunks)
            
            # Update assignment status
            assignment.status = 'DraftReady'
            assignment.save(update_fields=['status'])
            
            return draft
            
        except Exception as e:
            logger.exception(f"Error generating draft: {str(e)}")
            
            # Update assignment status to error
            try:
                assignment.status = 'Error'
                assignment.save(update_fields=['status'])
            except Exception:
                pass
                
            return None
    
    def process_material_for_embedding(self, document: Document) -> bool:
        """
        Process a document by chunking it and creating embeddings.
        
        Args:
            document (Document): The document to process
            
        Returns:
            bool: Success or failure
        """
        from .text_extractor import chunk_text
        
        try:
            # Delete existing chunks if any
            Chunk.objects.filter(document=document).delete()
            
            # Chunk the document text
            raw_text = document.raw_text
            chunks = chunk_text(raw_text)
            
            # Create chunks with embeddings
            for i, chunk_text in enumerate(chunks):
                # Create embedding
                embedding = self.create_embedding(chunk_text)
                
                if embedding is None:
                    logger.warning(f"Failed to create embedding for chunk {i} of document {document.id}")
                    continue
                    
                # Convert numpy array to bytes for storage
                embedding_bytes = embedding.astype(np.float32).tobytes()
                
                # Create chunk
                Chunk.objects.create(
                    document=document,
                    text=chunk_text,
                    embedding_vector=embedding_bytes,
                    chunk_index=i,
                    metadata={"page_estimate": i // 2}  # Rough estimate
                )
            
            return True
            
        except Exception as e:
            logger.exception(f"Error processing document {document.id}: {str(e)}")
            return False