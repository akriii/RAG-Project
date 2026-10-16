# RAG Support Agent API

A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI and LangChain. This backend service powers an intelligent customer support chatbot that answers user questions based strictly on company documents. 

It leverages Google's Gemini models for reasoning and Supabase's `pgvector` for scalable, metadata-filtered semantic search.

## Features

* **Advanced RAG Pipeline:** Uses LangChain to orchestrate document ingestion, text chunking, and contextual retrieval.
* **Cloud Vector Database:** Integrates with Supabase (`pgvector`) for persistent, cloud-hosted embedding storage.
* **Role-Based Access Control:** Implements dynamic metadata filtering at the database query level to restrict document access based on the user's department (e.g., HR vs. Engineering).
* **AI Reasoning:** Powered by `gemini-3.6-flash` for fast generation and `gemini-embedding-2-preview` for high-dimensional semantic search.
* **Conversational Memory:** Automatically tracks session history to handle multi-turn follow-up questions.
* **Full Observability:** Integrated with LangSmith to trace token usage, latency, and retrieval accuracy on every LLM call.
* **Containerized:** Fully Dockerized for seamless local development and cloud deployment.

## Tech Stack

* **Framework:** FastAPI
* **Orchestration:** LangChain
* **LLM & Embeddings:** Google Generative AI (Gemini)
* **Vector Store:** Supabase (PostgreSQL + pgvector)
* **Observability:** LangSmith
* **Containerization:** Docker & Docker Compose

## Prerequisites

* [Docker](https://www.docker.com/) installed and running.
* A [Supabase](https://supabase.com/) project with the `pgvector` extension enabled.
* API keys for Google Gemini and LangSmith.

## Environment Variables

Create a `.env` file in the root directory and add the following credentials:

```env
# Supabase Configuration
SUPABASE_URL=[https://your-project-id.supabase.co](https://your-project-id.supabase.co)
SUPABASE_SERVICE_KEY=your-service-role-key

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=[https://api.smith.langchain.com](https://api.smith.langchain.com)
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=rag-support-agent

## Local Development

**Start the server:**

```bash
docker-compose up --build
```

**Ingest your documents:**

In a separate terminal, run the ingestion script to process your PDFs, generate embeddings, attach metadata, and upload them to Supabase:

```bash
docker exec -it rag_support_agent-api-1 python app/db_utils.py
```

**Access the API Docs:**

Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to interact with the auto-generated Swagger UI and test the `/api/chat` endpoint.

### Example Request Payload

```json
POST /api/chat
{
  "session_id": "user-session-123",
  "question": "What is the timeframe for requesting a refund?",
  "department": "HR"
}
```