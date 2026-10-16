import os
from supabase.client import Client, create_client
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
session_store = {}

def get_session_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_qa_chain():
    # 1. Initialize models
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
    
    # 2. Initialize the Supabase Vector Store
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents"
    )

    # 3. Define the dynamic retriever function
    def dynamic_retriever(input_dict):
        question = input_dict["question"]
        user_dept = input_dict["department"]
        
        # Create a temporary retriever just for this request
        temp_retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": {"department": user_dept}
            }
        )
        docs = temp_retriever.invoke(question)
        return format_docs(docs)

    # 4. Define the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful customer support agent. Use ONLY the following pieces of retrieved context to answer the user's question. If the answer is not in the context, politely state that you do not know.\n\nContext: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    # 5. Build the chain
    lcel_chain = (
        RunnablePassthrough.assign(context=dynamic_retriever)
        | prompt
        | llm
        | StrOutputParser()
    )

    # 6. Wrap with memory
    conversational_chain = RunnableWithMessageHistory(
        lcel_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    return conversational_chain