backend/
|-- backend/
|   |-- __init__.py
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   |-- wsgi.py
|   |-- celery.py  # For Celery setup
|
|-- apps/
|   |-- __init__.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |   |-- utils.py # Optional utilities
|   |
|   |-- users/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- urls.py
|   |   |-- views.py
|   |
|   |-- classroom_integration/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- services.py # For Google API logic
|   |   |-- tasks.py    # Celery tasks for background API calls
|   |   |-- urls.py
|   |   |-- views.py
|   |
|   |-- ai_processing/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |-- models.py
|   |   |-- serializers.py
|   |   |-- services.py # For AI logic (text extraction, RAG, Gemini)
|   |   |-- tasks.py    # Celery tasks for background AI processing
|   |   |-- vector_store.py # FAISS/Pinecone interaction logic
|   |   |-- urls.py
|   |   |-- views.py
|   |
|   |-- agent_services/
|   |   |-- __init__.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- migrations/
|   |   |   |-- __init__.py
|   |   |-- models.py # Maybe models to track complex job statuses
|   |   |-- serializers.py-
|   |   |-- services.py # Orchestration logic combining other apps
|   |   |-- tasks.py    # Celery tasks for end-to-end flows
|   |   |-- urls.py
|   |   |-- views.py  # API endpoints for triggering agent workflows
|
|-- manage.py
|-- requirements.txt
|-- .env.example
|-- Dockerfile
|-- docker-compose.yml