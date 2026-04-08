Statement 1: Fine Print Decoder (RAG System)

GOAL- 
A high-precision Retrieval-Augmented Generation (RAG) system designed to decode complex legal jargon from the Titan Secure Health Insurance Policy into simple, "ELI5" (Explain Like I'm Five) language with 100% source transparency.

SYSTEM ARCHITECTURE-
The pipeline follows a modular RAG workflow to ensure accuracy and prevent hallucination:

(1) Ingestion: PDF documents are processed and parsed using PyPDF / LangChain.

(2) Chunking: Documents are split using the RecursiveCharacterTextSplitter with a chunk size of 1000 and an overlap of 200 to maintain context across clauses.

(3) Embeddings: Text chunks are converted into numerical vectors using sentence-transformers (Local Embeddings).

(4) Vector Store: Vectors are stored in ChromaDB (Persistent Local Storage) for semantic retrieval.

(5) Generation (LLM): The system uses Google's Flan-T5-Small to transform retrieved legal text into simplified language.

(6) Source Attribution: Every response includes metadata extraction to cite the exact Section, Clause, and Page Number.

SETUP INSTRUCTIONS-
1. Clone & Navigate
First, ensure you are in the specific project directory to avoid path errors with the local database and documents.

2. Virtual Environment Setup
It is highly recommended to use a virtual environment to keep dependencies isolated and avoid ModuleNotFound errors.

3. Install Dependencies
Install the core RAG stack (LangChain, ChromaDB, and Sentence-Transformers).

4. Environment Variables
The system uses a .env file for configuration. 
Open .env and ensure the following paths are correct:
CHROMA_PATH: Where your vector data will be saved (default: ./chroma_db).
DATA_PATH: Where the PDF is located (default: ./docs/).

USAGE GUIDE-
Step 1: Ingest the Policy
Before you can ask questions, the system must "read" the insurance policy and build the vector index.

Step 2: Query the Decoder
Once the ingestion is complete, start the interactive session.


FOLDER STRUCTURE-
RAGATHON/
├── docs/                                  
└── Statement-1-Insurance-Decoder/         
    ├── chroma_db/                         
    ├── docs/                             
    │   ├── Green_bank_Credit_Card_Agreement.txt
    │   ├── Sunset_Apartments_Rental_Contract.txt
    │   └── Titan_Secure_Health_Insurance_Policy.txt
    ├── src/                              
    ├── .env                               
    ├── decoder.py                       
    └── README.md                      