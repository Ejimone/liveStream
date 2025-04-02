"""
Agent implementation for handling various assistant tasks.
This module manages interactions with the Gemini API for generating
AI responses for different agent tasks.
"""

import json
import logging
import google.generativeai as genai
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import AgentTask, EmailDraft, SearchResult

logger = logging.getLogger(__name__)

# Configure the Gemini API with the key from settings
genai.configure(api_key=settings.GEMINI_API_KEY)

class Agent:
    """
    Core agent class that handles processing various types of tasks.
    """
    
    def __init__(self):
        # Gemini model configurations for different tasks
        self.default_model = "gemini-pro"
        self.models = {
            'email_draft': "gemini-pro",
            'web_search': "gemini-pro",
            'weather': "gemini-pro",
            'question': "gemini-pro",
        }
        
    def process_task(self, task_id):
        """
        Main entry point for processing an agent task.
        
        Args:
            task_id: The ID of the AgentTask to process
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Get the task from the database
            task = AgentTask.objects.get(id=task_id)
            
            # Update status to processing
            task.status = 'processing'
            task.save(update_fields=['status', 'updated_at'])
            
            # Process based on task type
            if task.task_type == 'email_draft':
                success = self.generate_email_draft(task)
            elif task.task_type == 'web_search':
                success = self.perform_web_search(task)
            elif task.task_type == 'weather':
                success = self.get_weather_info(task)
            elif task.task_type == 'question':
                success = self.answer_question(task)
            else:
                # Unhandled task type
                task.status = 'failed'
                task.response = "Unsupported task type."
                task.save(update_fields=['status', 'response', 'updated_at'])
                return False
            
            if success:
                # Mark as completed
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save(update_fields=['status', 'completed_at', 'updated_at'])
                return True
            else:
                # Mark as failed
                task.status = 'failed'
                task.save(update_fields=['status', 'updated_at'])
                return False
                
        except Exception as e:
            logger.exception(f"Error processing agent task {task_id}: {str(e)}")
            try:
                # Try to update task status
                task = AgentTask.objects.get(id=task_id)
                task.status = 'failed'
                task.response = f"Error: {str(e)}"
                task.save(update_fields=['status', 'response', 'updated_at'])
            except Exception:
                pass
            return False
    
    def answer_question(self, task):
        """
        Generate an answer to a general question using Gemini.
        
        Args:
            task: The AgentTask object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            model = genai.GenerativeModel(self.models.get('question', self.default_model))
            
            # Define the prompt for the question
            prompt = f"""
            You are acting as a helpful AI assistant for a student.
            Please answer the following question concisely and accurately:
            
            {task.prompt}
            """
            
            # Generate response from Gemini
            response = model.generate_content(prompt)
            
            # Update task with response
            task.response = response.text
            task.save(update_fields=['response', 'updated_at'])
            
            return True
        except Exception as e:
            logger.exception(f"Error answering question: {str(e)}")
            task.response = f"I'm sorry, I encountered an error while trying to answer your question: {str(e)}"
            task.save(update_fields=['response', 'updated_at'])
            return False
    
    def generate_email_draft(self, task):
        """
        Generate an email draft based on the user's prompt.
        
        Args:
            task: The AgentTask object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            model = genai.GenerativeModel(self.models.get('email_draft', self.default_model))
            
            # Extract any email context from the prompt or metadata
            to_email = None
            subject = None
            context = ""
            
            # Check if metadata contains email info
            if task.metadata:
                to_email = task.metadata.get('to_email', '')
                subject = task.metadata.get('subject', '')
                context = task.metadata.get('context', '')
            
            # Define the prompt for the email draft
            prompt = f"""
            You are an expert email writer. You need to draft a professional email based on the following request:
            
            {task.prompt}
            
            {f"RECIPIENT: {to_email}" if to_email else ""}
            {f"SUBJECT: {subject}" if subject else ""}
            {f"ADDITIONAL CONTEXT: {context}" if context else ""}
            
            Please format your response as a JSON object with the following structure:
            {{
                "subject": "The email subject line",
                "to": "The email address to send to (or 'TO_BE_FILLED_BY_USER' if not specified)",
                "content": "The complete email body with appropriate greeting and signature"
            }}
            
            The content should be professional, clear, and concise. Avoid unnecessary formality,
            but maintain a respectful tone. Include a suitable greeting and closing.
            
            DO NOT include any placeholders like [NAME] or [YOUR NAME] in the final email.
            Instead, make reasonable assumptions based on the context.
            """
            
            # Generate response from Gemini
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Parse the JSON response
            try:
                # Find JSON content (it might be wrapped in markdown code blocks)
                if '```json' in response_text:
                    json_text = response_text.split('```json')[1].split('```')[0]
                elif '```' in response_text:
                    json_text = response_text.split('```')[1].split('```')[0]
                else:
                    json_text = response_text
                
                email_data = json.loads(json_text)
                
                # Create the email draft
                email_draft = EmailDraft.objects.create(
                    agent_task=task,
                    subject=email_data.get('subject', 'No subject'),
                    to_recipients=email_data.get('to', 'TO_BE_FILLED_BY_USER'),
                    ai_generated_content=email_data.get('content', ''),
                    status='draft'
                )
                
                # Update task with a summary response
                task.response = f"Created email draft with subject: \"{email_draft.subject}\""
                task.save(update_fields=['response', 'updated_at'])
                
                return True
            except json.JSONDecodeError:
                # If JSON parsing fails, still create an email draft with the raw text
                email_draft = EmailDraft.objects.create(
                    agent_task=task,
                    subject=subject or 'Email draft',
                    to_recipients=to_email or 'TO_BE_FILLED_BY_USER',
                    ai_generated_content=response_text,
                    status='draft'
                )
                
                task.response = "Created email draft, but couldn't parse structured data."
                task.save(update_fields=['response', 'updated_at'])
                return True
                
        except Exception as e:
            logger.exception(f"Error generating email draft: {str(e)}")
            task.response = f"I'm sorry, I encountered an error while trying to draft your email: {str(e)}"
            task.save(update_fields=['response', 'updated_at'])
            return False
    
    def perform_web_search(self, task):
        """
        Perform a web search and summarize the results.
        In a real application, this would use a search API like Google Custom Search.
        For this implementation, we'll generate mock search results.
        
        Args:
            task: The AgentTask object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # In a real implementation, this would call a search API
            # For now, let's create some mock search results for demonstration
            mock_results = [
                {
                    "title": f"Search result for: {task.prompt} - 1",
                    "snippet": f"This is a snippet about {task.prompt} with some relevant information...",
                    "url": "https://example.com/result1",
                    "position": 1
                },
                {
                    "title": f"Search result for: {task.prompt} - 2",
                    "snippet": f"Another source of information about {task.prompt} with different details...",
                    "url": "https://example.com/result2", 
                    "position": 2
                },
                {
                    "title": f"Search result for: {task.prompt} - 3",
                    "snippet": f"A third perspective on {task.prompt} exploring additional aspects...",
                    "url": "https://example.com/result3",
                    "position": 3
                }
            ]
            
            # Store the mock search results
            for result in mock_results:
                SearchResult.objects.create(
                    agent_task=task,
                    title=result["title"],
                    snippet=result["snippet"],
                    url=result["url"],
                    position=result["position"]
                )
            
            # Generate a summary of search results using Gemini
            model = genai.GenerativeModel(self.models.get('web_search', self.default_model))
            
            # Create a prompt with the search results
            search_results_text = "\n\n".join([
                f"Title: {result['title']}\nSnippet: {result['snippet']}\nURL: {result['url']}"
                for result in mock_results
            ])
            
            prompt = f"""
            You are a helpful AI assistant. Based on the search query "{task.prompt}", 
            I have the following search results. Please provide a brief summary of the 
            information contained in these results, highlighting the most important points.
            
            SEARCH RESULTS:
            {search_results_text}
            """
            
            # Generate response from Gemini
            response = model.generate_content(prompt)
            
            # Update task with response
            task.response = response.text
            task.save(update_fields=['response', 'updated_at'])
            
            return True
            
        except Exception as e:
            logger.exception(f"Error performing web search: {str(e)}")
            task.response = f"I'm sorry, I encountered an error while trying to search for information: {str(e)}"
            task.save(update_fields=['response', 'updated_at'])
            return False
    
    def get_weather_info(self, task):
        """
        Get weather information based on the user's request.
        In a real application, this would use a weather API.
        
        Args:
            task: The AgentTask object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # In a real implementation, this would call a weather API
            # For now, generate a mock weather response
            
            # Try to extract location from prompt
            model = genai.GenerativeModel(self.models.get('weather', self.default_model))
            
            location_prompt = f"""
            From this weather query: "{task.prompt}"
            Extract ONLY the location name. If no specific location is mentioned, respond with "current location".
            Respond with just the location name, nothing else.
            """
            
            location_response = model.generate_content(location_prompt)
            location = location_response.text.strip()
            
            # Generate mock weather data
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            mock_weather = {
                "location": location,
                "date": current_date,
                "temperature": "72°F (22°C)",
                "condition": "Partly Cloudy",
                "humidity": "45%",
                "wind": "8 mph NW",
                "forecast": [
                    {"day": "Tomorrow", "condition": "Sunny", "high": "75°F", "low": "60°F"},
                    {"day": "Day after", "condition": "Clear", "high": "78°F", "low": "62°F"},
                ]
            }
            
            # Update task metadata with mock weather data
            task.metadata = mock_weather
            
            # Generate a nice response with the weather information
            weather_prompt = f"""
            You are a helpful AI assistant. The user asked about the weather: "{task.prompt}"
            
            Based on the following weather data, please provide a friendly and informative response:
            
            Location: {mock_weather['location']}
            Date: {mock_weather['date']}
            Current temperature: {mock_weather['temperature']}
            Condition: {mock_weather['condition']}
            Humidity: {mock_weather['humidity']}
            Wind: {mock_weather['wind']}
            
            Tomorrow's forecast: {mock_weather['forecast'][0]['condition']}, High: {mock_weather['forecast'][0]['high']}, Low: {mock_weather['forecast'][0]['low']}
            Day after: {mock_weather['forecast'][1]['condition']}, High: {mock_weather['forecast'][1]['high']}, Low: {mock_weather['forecast'][1]['low']}
            
            Keep your response conversational and concise.
            """
            
            # Generate response from Gemini
            response = model.generate_content(weather_prompt)
            
            # Update task with response
            task.response = response.text
            task.save(update_fields=['response', 'metadata', 'updated_at'])
            
            return True
            
        except Exception as e:
            logger.exception(f"Error getting weather information: {str(e)}")
            task.response = f"I'm sorry, I couldn't retrieve the weather information you requested: {str(e)}"
            task.save(update_fields=['response', 'updated_at'])
            return False
