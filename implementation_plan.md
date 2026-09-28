# AI Chef: Inventory & RAG Recipe System Roadmap

## Project & Architecture Status (End of Ingestion Phase)

### What We Have Built (Current State)
1. **Telegram Interface (Milestone 1):** Echo bot is functioning.
2. **Data Entry Agent (Milestone 2):** Successfully implemented Gemini Function Calling (`GenerateContentConfig(tools=[update_inventory])`). It parses natural language and executes the tool.
3. **Firestore Integration:** The bot dynamically creates collections and documents, writing structured data directly to a Google Cloud Firestore NoSQL database. We architected the DB to use the item name (e.g., "chicken") as the Document ID for efficient lookups.
4. **Data Retrieval (Milestone 3A):** Implemented `check_inventory` which uses `db.collection("inventory").where(filter=FieldFilter("quantity", ">", 0)).stream()` to read back available ingredients and format them into a string for the LLM.
5. **Vector Ingestion Pipeline (Milestone 3B):** Implemented `rag_proccesor.py`.
   - Separated PDF text extraction (`pypdf`) from the chunking logic.
   - Built a pure Python `chunk_text` helper function to slice strings into fixed sizes using `range` stepping.
   - Successfully instantiated a local `SentenceTransformer` (`all-MiniLM-L6-v2`) to embed chunks into 384-dimensional vectors.
   - Successfully loaded 82 vectors into a `faiss.IndexFlatL2` database.

### Mentorship & User Profile (Updated Observations)
* **Learning Style:** The user strongly prefers a "mentor/mentee" dynamic. Do NOT provide complete, ready-to-run code dumps. Provide skeletons with `[YOUR TURN]` blanks.
* **Capabilities:** The user is highly capable of logical deduction and mathematical operations (e.g., quickly grasped Python `range` slicing for chunking). 
* **Growth Areas:** The user benefits from architectural explanations regarding Object-Oriented Programming (OOP) and Separation of Concerns. Specifically, explaining *why* we separate utility functions (like `chunk_text`) from orchestrator functions (like `add_to_index`), and clarifying function arguments vs. global state. 
* **Guidance Method:** Always explain the "Why" (e.g., why FAISS needs `float32`). If the user writes code that works but is architecturally flawed, gently correct the structure to teach best practices.

### Libraries in Use
* **LLM:** `google-genai` (using Gemini Flash). 
* **Database:** `firebase-admin` (Google Cloud Firestore). 
* **PDF Processing:** `pypdf`.
* **Vector/RAG:** `sentence-transformers` (local embeddings) and `faiss-cpu` (vector database).

## The Roadmap

### Milestone 1 & 2: ✅ COMPLETED
* Telegram Bot Setup
* Function Calling for Inventory Add/Remove (Firestore Writes)

### Milestone 3: The Knowledge Base (Ingestion) - ✅ COMPLETED
* ✅ **Part A:** Database Retrieval (`check_inventory` tool).
* ✅ **Part B:** PDF Text Extraction, Chunking, Embedding, and FAISS indexing (`rag_proccesor.py`).

### Milestone 4: Retrieval & The RAG-Powered Chef Agent (NEXT UP)
**Goal:** Query the Vector DB and combine it with Firestore inventory to generate a grounded LLM response.
*   **Step 1 (Retrieval):** Build a `search(self, query, top_k)` method in `rag_proccesor.py` that embeds a user question, searches FAISS, and returns the top matching text chunks.
*   **Step 2 (Generation):** A query pipeline that:
    1. Reads available ingredients from Firestore.
    2. Fetches top matching recipes from FAISS.
    3. Asks the Gemini LLM to recommend a meal *strictly* based on those retrieved recipes and available ingredients.

### Milestone 5: The Orchestrator
**Goal:** Tie everything together into a seamless Telegram experience.
*   **Deliverable:** The Telegram bot receives a message, routes to the inventory agent or the chef agent, and returns the final response.

## Next Steps for the Next Agent
Pick up exactly at **Milestone 4 - Step 1 (Retrieval)**. The user has populated FAISS but has NOT written the search logic yet. Guide the user through writing `search(query, top_k)` in `rag_proccesor.py` using the established mentor/mentee format. Explain how a query vector is compared against database vectors.
