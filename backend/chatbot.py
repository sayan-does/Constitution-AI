import openai
import requests
from sentence_transformers import SentenceTransformer
from vector_store import VectorStoreManager
from document_processor import DocumentProcessor
import json


class LegalRAGChatbot:
    def __init__(self,
                 embedding_model_name='all-MiniLM-L6-v2',
                 openrouter_api_key="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",
                 model_name="openai/gpt-4o-mini"):
        self.vector_store = VectorStoreManager(embedding_model_name)
        self.api_key = openrouter_api_key
        self.model_name = model_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Initialize test data if knowledge base is empty
        if self.vector_store.get_document_count() == 0:
            self.initialize_test_data()

        # Process documents from DOCUMENTS_DIR
        self.load_directory_documents()

    def initialize_test_data(self):
        """Initialize the knowledge base with test legal documents"""
        test_documents = [
            """According to Section 302 of Indian Penal Code (IPC), whoever commits murder shall be punished with death, 
            or imprisonment for life, and shall also be liable to fine.""",

            """Under Section 304A of IPC, whoever causes the death of any person by doing any rash or negligent act 
            not amounting to culpable homicide, shall be punished with imprisonment of either description for a term 
            which may extend to two years, or with fine, or with both.""",

            """As per Section 375 of IPC, rape is defined as specific acts against a woman without her consent or will, 
            and is punishable under Section 376 with rigorous imprisonment of either description for a term which shall 
            not be less than ten years, but which may extend to imprisonment for life.""",

            """According to Section 420 of IPC, whoever cheats and thereby dishonestly induces the person deceived to 
            deliver any property to any person shall be punished with imprisonment of either description for a term 
            which may extend to seven years, and shall also be liable to fine.""",

            """The Right to Information Act, 2005 mandates timely response to citizen requests for government information. 
            It is an initiative taken by Department of Personnel and Training, Ministry of Personnel, Public Grievances 
            and Pensions to provide a RTI Portal Gateway to the citizens for quick search of information."""
        ]

        print("📚 Initializing knowledge base with test legal documents...")
        self.vector_store.add_documents(test_documents)
        print(
            f"✅ Added {len(test_documents)} test documents to the knowledge base.")
        return len(test_documents)

    def load_directory_documents(self):
        """Load and process documents from the DOCUMENTS_DIR"""
        print("📚 Processing documents from directory...")
        processed_texts = DocumentProcessor.process_directory_documents()
        if processed_texts:
            self.vector_store.add_documents(processed_texts)
            print(
                f"✅ Added {len(processed_texts)} documents from directory to the knowledge base.")
        else:
            print(
                "ℹ️ No documents found in directory or all documents were already processed.")

    def add_user_context(self, context_text):
        """Add user-provided context to the user context vector store"""
        if context_text:
            self.vector_store.add_user_documents([context_text])
            print(
                f"✅ Added user context to knowledge base. Total user contexts: {self.vector_store.get_user_document_count()}")
            return True
        return False

    def generate_response(self, query, context_docs):
        """Generate RAG-based response using OpenRouter"""
        if not context_docs:
            return "No relevant legal documents found. Please refine your query."

        # Validate context retrieval success
        if not any(isinstance(doc, str) and doc.strip() for doc in context_docs):
            return "Error: Retrieved context is empty or invalid."

        # Combine retrieved context with query
        prompt = self._create_prompt(query, context_docs)

        # Make OpenRouter API request
        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for bad responses

            # Validate API response
            response_data = response.json()
            if "choices" not in response_data or not response_data["choices"]:
                return "Error: Unexpected API response format."

            response_text = response_data["choices"][0]["message"]["content"]

            # Ensure the response is valid JSON
            try:
                json_output = json.loads(response_text)
                if "answer" in json_output and "basis" in json_output:
                    return json_output["answer"]
                else:
                    return "Error: Response JSON is missing required keys."
            except json.JSONDecodeError:
                return "Error: OpenRouter response is not valid JSON."

        except requests.exceptions.RequestException as e:
            return f"API request failed: {str(e)}"

    def _create_prompt(self, query, context_docs):
        """Create structured prompt with legal context"""
        max_context_length = 1500
        combined_context = ' '.join(context_docs)
        if len(combined_context) > max_context_length:
            combined_context = combined_context[:max_context_length] + "..."

        # OpenRouter GPT-4o-mini chat format
        prompt = f"""
        You are an AI-based Indian Law Advisor that provides accurate legal information strictly based on the provided context. 
        Your responses must be in JSON format containing:
        1. 'answer' - Clear legal advice based on context.
        2. 'basis' - Array of EXACT QUOTES from provided context that form the foundation of the answer.

        Context: {combined_context}

        User Query: {query}

        Expected Response Format:
        {{ 
          "answer": "Your legal advice...",
          "basis": [
            "Exact quote 1 from context...",
            "Exact quote 2 from context..."
          ]
        }}
        -Important
         1. you must provide response in the valid JSON format.
         2. give exact quotes of laws as the basis of the answer.
        """
        return prompt
