import os
from supabase.client import Client, create_client
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

PDF_PATH = "app/folder/sample_policy.pdf"

def create_and_save_vector_store():
    print(f"Loading document: {PDF_PATH}...")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # 1. Add metadata to every chunk before saving
    for doc in docs:
        doc.metadata = {"department": "HR", "doc_version": "1.0"}

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    
    print("Saving to Supabase...")
    vector_store = SupabaseVectorStore.from_documents(
        docs,
        embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents"
    )
    print("Success! Documents saved to Supabase.")

if __name__ == "__main__":
    create_and_save_vector_store()