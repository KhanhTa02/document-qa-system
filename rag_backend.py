import os
import logging
from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentQASystem:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.vectorstore = None
        self.embeddings = None
        self.llm = None
        self.bm25 = None
        self.documents = []
        
        self._setup_embeddings()
        self._setup_llm()
        self._process_document()
        self._setup_vectorstore()
        self._setup_bm25()

    def _setup_embeddings(self):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        logger.info("Embeddings initialized")

    def _setup_llm(self):
        self.llm = OllamaLLM(model="llama3.1")
        logger.info("LLM initialized")

    def _process_document(self):
        loader = UnstructuredLoader(
            self.pdf_path,
            chunking_strategy="by_title",
            max_characters=1000000,
            include_orig_elements=False,
        )
        raw_docs = loader.load()
        
        for doc in raw_docs:
            page_num = doc.metadata.get('page_number', doc.metadata.get('page', 0))
            processed_doc = Document(
                page_content=doc.page_content,
                metadata={'page': page_num, 'source': self.pdf_path}
            )
            self.documents.append(processed_doc)
        
        logger.info(f"Processed {len(self.documents)} document chunks")

    def _setup_vectorstore(self):
        self.vectorstore = Chroma.from_documents(
            documents=self.documents,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        logger.info("Vector store setup complete")

    def _setup_bm25(self):
        doc_texts = [doc.page_content for doc in self.documents]
        tokenized_docs = [doc.split() for doc in doc_texts]
        self.bm25 = BM25Okapi(tokenized_docs)
        logger.info("BM25 setup complete")

    def _is_complex(self, question: str) -> bool:
        complexity_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
            Is this question complex and requiring sub-questions? Answer "Complex" or "Simple".
            
            Complex if:
            - Requires multiple steps or concepts
            - Needs to compare different approaches
            - Asks for detailed explanations with multiple aspects
            - Requires analysis across different sections
            
            Simple if:
            - Asks for a single definition or concept
            - Requires a straightforward factual answer
            - Can be answered with a single, direct response
            
            Question: {question}
            """
        )
        
        chain = complexity_prompt | self.llm
        response = chain.invoke({"question": question}).strip()
        is_complex = "complex" in response.lower().replace("*", "").replace("**", "")
        logger.info(f"Complexity: {response} (Complex: {is_complex})")
        return is_complex

    def _generate_sub_questions(self, question: str) -> List[str]:
        sub_question_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
            You are an expert question decomposer skilled in breaking down complex queries into clear, relevant, non-overlapping sub-questions.

            List 2-3 distinct sub-questions needed to fully answer the following main question. Each sub-question should:
            - Target a specific concept or step.
            - Be mutually exclusive and independently answerable.
            - Cover the full scope of the main question.
            
            Main Question: {question}
            
            Generate only the sub-questions, no other text (one per line):
            """
        )
        
        chain = sub_question_prompt | self.llm
        response = chain.invoke({"question": question})
        sub_questions = [q.strip() for q in response.split('\n') if q.strip()]
        
        logger.info(f"Generated {len(sub_questions)} sub-questions")
        
        # Log each sub-question
        for i, sub_q in enumerate(sub_questions, 1):
            logger.info(f"Sub-question {i}: {sub_q}")
        
        return sub_questions

    def _hybrid_retrieval(self, question: str, k: int = 10) -> List[Document]:
        # Vector search
        vector_results = self.vectorstore.similarity_search(question, k=k)
        
        # BM25 search
        tokenized_question = question.split()
        bm25_scores = self.bm25.get_scores(tokenized_question)
        bm25_indices = np.argsort(bm25_scores)[::-1][:k]
        bm25_results = [self.documents[i] for i in bm25_indices]
        
        # Combine and deduplicate
        all_results = vector_results + bm25_results
        unique_results = []
        seen_contents = set()
        
        for doc in all_results:
            if doc.page_content not in seen_contents:
                unique_results.append(doc)
                seen_contents.add(doc.page_content)
        
        return unique_results[:k]

    def _rerank_documents(self, question: str, documents: List[Document]) -> List[Document]:
        if not documents:
            return []
        
        # Simple reranking based on question-document similarity
        scored_docs = []
        question_words = set(question.lower().split())
        
        for doc in documents:
            doc_words = set(doc.page_content.lower().split())
            overlap = len(question_words.intersection(doc_words))
            score = overlap / len(question_words) if question_words else 0
            scored_docs.append((doc, score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs]

    def _extract_page_numbers(self, documents: List[Document]) -> List[str]:
        page_numbers = []
        for doc in documents:
            page_num = doc.metadata.get('page', doc.metadata.get('page_number', 'Unknown'))
            if page_num != 'Unknown':
                try:
                    page_num = int(page_num)
                    page_numbers.append(f"Page {page_num + 1}")
                except (ValueError, TypeError):
                    page_numbers.append(f"Page {page_num}")
            else:
                page_numbers.append("Unknown page")
        return page_numbers

    def answer_question(self, question: str) -> Dict[str, Any]:
        logger.info(f"Processing: {question}")
        
        # Check complexity and generate sub-questions if needed
        if self._is_complex(question):
            sub_questions = self._generate_sub_questions(question)
            logger.info(f"Complex question - generated {len(sub_questions)} sub-questions")
        else:
            sub_questions = [question]
            logger.info("Simple question - no sub-questions needed")
        
        # Retrieve documents
        if len(sub_questions) > 1:
            all_docs = []
            for sub_q in sub_questions:
                docs = self._hybrid_retrieval(sub_q, k=5)
                all_docs.extend(docs)
            
            # Deduplicate
            unique_docs = []
            seen = set()
            for doc in all_docs:
                if doc.page_content not in seen:
                    unique_docs.append(doc)
                    seen.add(doc.page_content)
            
            final_docs = self._rerank_documents(question, unique_docs)
        else:
            final_docs = self._hybrid_retrieval(question, k=8)
        
        if not final_docs:
            return {"answer": "No relevant information found.", "sources": []}
        
        # Generate answer
        qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            Answer this question based explicitly on the context, accurately and comprehensively. Only use information from the context.
            If the context doesn't have enough information, say so.
            
            Context: {context}
            Question: {question}
            
            Answer:
            """
        )
        
        qa_chain = qa_prompt | self.llm
        context = "\n\n".join([doc.page_content for doc in final_docs])
        response = qa_chain.invoke({"context": context, "question": question})
        
        page_numbers = self._extract_page_numbers(final_docs[:3])
        
        return {"answer": response, "sources": page_numbers} 