from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pypdf import PdfReader



class RAGProcessor:
    def __init__(self):
        print("Initializing RAG Processor...")

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384 
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []


    def search(self, query: str, top_k: int = 3):
        # 1. Embed the query using the same model we used for ingestion
        query_embedding = self.model.encode(query)

        # 2. Format the vector for FAISS (must be 2D float32 numpy array)
        # We use np.array([query_embedding]) to make it 2D (1 row, 384 columns)

        query_vector = np.array([query_embedding]).astype("float32")
        # 3. Perform the search on our FAISS index
        # This returns D (distances) and I (indices of the closest vectors)

        distances, indices = self.index.search(query_vector, top_k)
        top_indices = indices[0]

        results = []


        # 4. Map the integer indices back to our original text chunks
        for idx in top_indices:
            if idx != -1:  # FAISS returns -1 if it can't find enough matches
                chunk = self.chunks[idx] 
                results.append(chunk)
        return results




    def chunk_text(self, text, chunk_size=500):
        """
        Splits a massive string of text into smaller strings.
        """
        chunks = []
        for i in range(0, len(text), chunk_size):

            chunk = text[i: i + chunk_size]
            chunks.append(chunk)
        return chunks


    def add_to_index(self, extracted_text):
        """
        Takes raw extracted PDF text, chunks it, embeds it, and stores it.
        """

        new_chunks = self.chunk_text(extracted_text)

        self.chunks.extend(new_chunks)

        embeddings = self.model.encode(new_chunks)
        embeddings = np.array(embeddings).astype(np.float32)
        embeddings = self.index.add(embeddings)

# --- TESTING OUR RAG PROCESSOR ---
if __name__ == "__main__":
    print("1. Extracting text from PDF...")
    # (Move your PDF reading logic from the top of the file down here!)
    reader = PdfReader("recipes/Recetas.pdf")
    full_pdf_text = ""
    for page in reader.pages:
        full_pdf_text += page.extract_text() + " "
    print(f"Extracted {len(full_pdf_text)} characters from the PDF.")

    print("\n2. Starting the Engine...")
    processor = RAGProcessor()

    print("\n3. Chunking, Embedding, and Indexing...")
    processor.add_to_index(full_pdf_text)

    print("\n✅ SUCCESS!")
    print(f"Total chunks stored in FAISS: {processor.index.ntotal}")
    print(f"Total text strings stored in memory: {len(processor.chunks)}")
    print("\n4. Testing the Search!")
    print(processor.search("chicken recipe", top_k=2))
