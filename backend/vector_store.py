import faiss
import numpy as np
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from config import DATA_DIR

class VectorStoreManager:
    """Manages Faiss vector store for document embeddings with persistence"""
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.index_path = DATA_DIR / "faiss_index"
        self.docs_path = DATA_DIR / "document_texts.pkl"
        self.embedding_model = SentenceTransformer(model_name)
        
        # Create data directory if it doesn't exist
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load existing index and documents
        self.index = None
        self.document_texts = []
        self.load_or_initialize()

    def load_or_initialize(self):
        """Load existing index and documents or initialize new ones"""
        try:
            if self.index_path.exists() and self.docs_path.exists():
                # Load the FAISS index
                self.index = faiss.read_index(str(self.index_path))
                
                # Load the document texts
                with open(self.docs_path, 'rb') as f:
                    self.document_texts = pickle.load(f)
                print(f"Loaded {len(self.document_texts)} documents from existing knowledge base")
            else:
                # Initialize new index
                self.index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
                self.document_texts = []
                print("Initialized new knowledge base")
        except Exception as e:
            print(f"Error loading knowledge base: {str(e)}")
            # Initialize new index if loading fails
            self.index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
            self.document_texts = []

    def save(self):
        """Save the current index and documents to disk"""
        try:
            # Save the FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save the document texts
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.document_texts, f)
            
            print(f"Saved {len(self.document_texts)} documents to knowledge base")
        except Exception as e:
            print(f"Error saving knowledge base: {str(e)}")

    def add_documents(self, documents):
        """Add documents to vector store and save"""
        if not documents:
            return
        
        embeddings = self.embedding_model.encode(documents)
        self.index.add(embeddings)
        self.document_texts.extend(documents)
        
        # Save after adding new documents
        self.save()

    def search(self, query, top_k=3):
        """Retrieve similar documents"""
        if not self.document_texts:
            return []
            
        if self.index.ntotal == 0:
            return []
            
        try:
            query_embedding = self.embedding_model.encode([query])
            distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            return [self.document_texts[i] for i in indices[0] if i < len(self.document_texts)]
        except Exception as e:
            print(f"Error during vector search: {str(e)}")
            return []

    def get_document_count(self):
        """Return the number of documents in the store"""
        return len(self.document_texts)

    def clear(self):
        """Clear the knowledge base"""
        self.index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
        self.document_texts = []
        
        # Remove saved files
        if self.index_path.exists():
            self.index_path.unlink()
        if self.docs_path.exists():
            self.docs_path.unlink()