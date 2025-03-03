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
        self.user_index_path = DATA_DIR / "user_faiss_index"
        self.user_docs_path = DATA_DIR / "user_document_texts.pkl"
        self.embedding_model = SentenceTransformer(model_name)
        
        # Create data directory if it doesn't exist
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load existing indices and documents
        self.index = None
        self.document_texts = []
        self.user_index = None
        self.user_document_texts = []
        self.load_or_initialize()

    def load_or_initialize(self):
        """Load existing index and documents or initialize new ones"""
        try:
            # Load system knowledge base
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
                
            # Load user context knowledge base
            if self.user_index_path.exists() and self.user_docs_path.exists():
                # Load the user FAISS index
                self.user_index = faiss.read_index(str(self.user_index_path))
                
                # Load the user document texts
                with open(self.user_docs_path, 'rb') as f:
                    self.user_document_texts = pickle.load(f)
                print(f"Loaded {len(self.user_document_texts)} documents from existing user context")
            else:
                # Initialize new user index
                self.user_index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
                self.user_document_texts = []
                print("Initialized new user context knowledge base")
                
        except Exception as e:
            print(f"Error loading knowledge base: {str(e)}")
            # Initialize new indices if loading fails
            self.index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
            self.document_texts = []
            self.user_index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
            self.user_document_texts = []

    def save(self):
        """Save the current indices and documents to disk"""
        try:
            # Save the system FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save the system document texts
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.document_texts, f)
            
            # Save the user FAISS index
            faiss.write_index(self.user_index, str(self.user_index_path))
            
            # Save the user document texts
            with open(self.user_docs_path, 'wb') as f:
                pickle.dump(self.user_document_texts, f)
            
            print(f"Saved {len(self.document_texts)} system documents and {len(self.user_document_texts)} user documents to knowledge base")
        except Exception as e:
            print(f"Error saving knowledge base: {str(e)}")

    def add_documents(self, documents):
        """Add documents to system vector store and save"""
        if not documents:
            return
        
        embeddings = self.embedding_model.encode(documents)
        self.index.add(embeddings)
        self.document_texts.extend(documents)
        
        # Save after adding new documents
        self.save()
        
    def add_user_documents(self, documents):
        """Add documents to user context vector store and save"""
        if not documents:
            return
        
        embeddings = self.embedding_model.encode(documents)
        self.user_index.add(embeddings)
        self.user_document_texts.extend(documents)
        
        # Save after adding new documents
        self.save()

    def search(self, query, top_k=3):
        """Retrieve similar documents from both system and user context"""
        results = []
        
        # Search in system documents
        if self.document_texts and self.index.ntotal > 0:
            try:
                query_embedding = self.embedding_model.encode([query])
                distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
                system_results = [self.document_texts[i] for i in indices[0] if i < len(self.document_texts)]
                results.extend(system_results)
            except Exception as e:
                print(f"Error during system vector search: {str(e)}")
        
        # Search in user context documents
        if self.user_document_texts and self.user_index.ntotal > 0:
            try:
                query_embedding = self.embedding_model.encode([query])
                distances, indices = self.user_index.search(query_embedding, min(top_k, self.user_index.ntotal))
                user_results = [self.user_document_texts[i] for i in indices[0] if i < len(self.user_document_texts)]
                results.extend(user_results)
            except Exception as e:
                print(f"Error during user context vector search: {str(e)}")
                
        return results

    def get_document_count(self):
        """Return the number of documents in the store"""
        return len(self.document_texts)
        
    def get_user_document_count(self):
        """Return the number of user context documents in the store"""
        return len(self.user_document_texts)

    def clear(self):
        """Clear the knowledge base"""
        self.index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
        self.document_texts = []
        self.user_index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
        self.user_document_texts = []
        
        # Remove saved files
        if self.index_path.exists():
            self.index_path.unlink()
        if self.docs_path.exists():
            self.docs_path.unlink()
        if self.user_index_path.exists():
            self.user_index_path.unlink()
        if self.user_docs_path.exists():
            self.user_docs_path.unlink()