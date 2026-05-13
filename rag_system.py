import chromadb
from sentence_transformers import SentenceTransformer
import hashlib

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("business_docs")

    def add_document(self, text, filename):
        words = text.split()
        chunks = []
        for i in range(0, len(words), 200):
            chunk = " ".join(words[i:i+200])
            chunks.append(chunk)

        for i, chunk in enumerate(chunks):
            embedding = self.model.encode(chunk).tolist()
            doc_id = hashlib.md5(f"{filename}_{i}".encode()).hexdigest()
            self.collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": filename, "chunk": i}],
                ids=[doc_id]
            )
        return len(chunks)

    def retrieve(self, query, n_results=3):
        if self.collection.count() == 0:
            return ""
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count())
        )
        if results['documents'][0]:
            return "\n\n".join(results['documents'][0])
        return ""

    def get_all_docs(self):
        if self.collection.count() == 0:
            return []
        results = self.collection.get()
        return list(set([m['source'] for m in results['metadatas']]))