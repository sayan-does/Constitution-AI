import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from config import DOCUMENTS_DIR

from document_processor import DocumentProcessor
from chatbot import LegalRAGChatbot

app = FastAPI(title="Legal RAG Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = LegalRAGChatbot()

@app.post("/upload-knowledge-base")
async def upload_knowledge_base(files: List[UploadFile] = File(...)):
    """Upload and process documents for knowledge base"""
    processed_texts = []
    for file in files:
        file_path = DOCUMENTS_DIR / file.filename
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        try:
            text = DocumentProcessor.process_document(file_content, file_type)
            processed_texts.append(text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # Add documents to vector store
    chatbot.vector_store.add_documents(processed_texts)
    return {"status": "Knowledge base updated", "documents_processed": len(processed_texts)}

@app.post("/chat")
async def chat_endpoint(query: str, context_file: Optional[UploadFile] = File(None)):
    """Main chat endpoint with optional context file"""
    # Process context file if provided
    context_texts = []
    if context_file:
        file_content = await context_file.read()
        file_type = context_file.filename.split('.')[-1].lower()
        context_text = DocumentProcessor.process_document(file_content, file_type)
        context_texts.append(context_text)
    
    # Retrieve relevant documents from vector store
    retrieved_docs = chatbot.vector_store.search(query)
    
    # Combine context and retrieved docs
    all_context = context_texts + retrieved_docs
    
    # Generate response
    response = chatbot.generate_response(query, all_context)
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)