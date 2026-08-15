import os
import json
from config import Config


class RAGService:
    """Retrieval-Augmented Generation service using FAISS vector storage."""

    def __init__(self):
        self.enabled = bool(Config.GEMINI_API_KEY)
        self._embeddings = None
        self._vectorstores = {}

    def _get_embeddings(self):
        if self._embeddings is None and self.enabled:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._embeddings = GoogleGenerativeAIEmbeddings(
                    model=Config.EMBEDDING_MODEL,
                    google_api_key=Config.GEMINI_API_KEY,
                )
            except Exception:
                self.enabled = False
        return self._embeddings

    def _get_store_path(self, material_id):
        return os.path.join(Config.VECTORSTORE_FOLDER, f'material_{material_id}')

    def _get_metadata_path(self, material_id):
        return os.path.join(self._get_store_path(material_id), 'metadata.json')

    def process_material(self, material_id, filepath, title):
        """Process a PDF and store embeddings in FAISS."""
        if not self.enabled:
            return False, 'AI features disabled: GEMINI_API_KEY not configured.'

        try:
            try:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
            except ImportError:
                from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import FAISS
            from services.pdf_processor import extract_text_from_pdf

            chunks = extract_text_from_pdf(filepath)
            if not chunks:
                return False, 'No text could be extracted from the PDF.'

            documents = []
            metadatas = []
            for chunk in chunks:
                documents.append(chunk['text'])
                metadatas.append({
                    'page': chunk['page'],
                    'title': title,
                    'material_id': material_id,
                })

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

            split_docs = []
            for doc_text, meta in zip(documents, metadatas):
                splits = splitter.split_text(doc_text)
                for split in splits:
                    split_docs.append({'text': split, 'metadata': meta})

            texts = [d['text'] for d in split_docs]
            metas = [d['metadata'] for d in split_docs]

            embeddings = self._get_embeddings()
            if not embeddings:
                return False, 'Failed to initialize embedding model.'

            vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metas)

            store_path = self._get_store_path(material_id)
            os.makedirs(store_path, exist_ok=True)
            vectorstore.save_local(store_path)

            with open(self._get_metadata_path(material_id), 'w') as f:
                json.dump({'title': title, 'material_id': material_id}, f)

            self._vectorstores[material_id] = vectorstore
            return True, 'PDF processed successfully for AI search.'

        except Exception as e:
            return False, f'RAG processing failed: {str(e)}'

    def _load_vectorstore(self, material_id):
        if material_id in self._vectorstores:
            return self._vectorstores[material_id]

        store_path = self._get_store_path(material_id)
        if not os.path.exists(store_path):
            return None

        try:
            from langchain_community.vectorstores import FAISS
            embeddings = self._get_embeddings()
            if not embeddings:
                return None
            vectorstore = FAISS.load_local(
                store_path, embeddings, allow_dangerous_deserialization=True
            )
            self._vectorstores[material_id] = vectorstore
            return vectorstore
        except Exception:
            return None

    def search(self, query, material_ids=None, subject_material_ids=None, k=4):
        """Search relevant chunks across materials."""
        if not self.enabled:
            return []

        ids_to_search = material_ids or subject_material_ids or []
        if not ids_to_search:
            return []

        all_results = []
        for mid in ids_to_search:
            vs = self._load_vectorstore(mid)
            if vs:
                try:
                    results = vs.similarity_search_with_score(query, k=k)
                    for doc, score in results:
                        all_results.append({
                            'text': doc.page_content,
                            'metadata': doc.metadata,
                            'score': score,
                        })
                except Exception:
                    continue

        all_results.sort(key=lambda x: x['score'])
        return all_results[:k]

    def delete_material_store(self, material_id):
        """Remove vector store for a material."""
        store_path = self._get_store_path(material_id)
        if os.path.exists(store_path):
            import shutil
            shutil.rmtree(store_path)
        if material_id in self._vectorstores:
            del self._vectorstores[material_id]

    def get_material_ids_for_subject(self, subject_id, db_session):
        from database.models import StudyMaterial
        materials = db_session.query(StudyMaterial).filter_by(subject_id=subject_id).all()
        valid_ids = []
        for m in materials:
            if os.path.exists(self._get_store_path(m.id)):
                valid_ids.append(m.id)
        return valid_ids


rag_service = RAGService()
