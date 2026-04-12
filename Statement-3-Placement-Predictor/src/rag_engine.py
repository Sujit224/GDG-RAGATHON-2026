from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os

class ExperienceMatcher:
    def __init__(self, persist_dir="./vectorstore"):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_dir = persist_dir
        self.vector_db = self._init_db()

    def _init_db(self):
        if not os.path.exists(self.persist_dir):
            sample_experiences = [
                Document(page_content="Amazon Interview: Focused heavily on DSA, Java, and AWS Cloud concepts.", metadata={"company": "Amazon", "stack": "Java, AWS", "difficulty": 8}),
                Document(page_content="Goldman Sachs: Required strong grip on C++, Algorithms, and Systems Design.", metadata={"company": "Goldman Sachs", "stack": "C++, Systems", "difficulty": 9}),
                Document(page_content="Google: Deep dive into Python, Distributed Systems, and Open Source contributions.", metadata={"company": "Google", "stack": "Python, OS", "difficulty": 8}),
                Document(page_content="Startup X: Focused on Fullstack React, Node.js and fast-paced problem solving.", metadata={"company": "Startup X", "stack": "React, Node", "difficulty": 6}),
                Document(page_content="Microsoft: C#, Cloud Architecture, and Azure services. System design important.", metadata={"company": "Microsoft", "stack": "C#, Azure", "difficulty": 7}),
                Document(page_content="Meta: JavaScript, React, Node.js for fullstack. Frontend and backend both important.", metadata={"company": "Meta", "stack": "JavaScript, React", "difficulty": 8}),
            ]
            return Chroma.from_documents(
                sample_experiences, 
                self.embeddings, 
                persist_directory=self.persist_dir
            )
        return Chroma(persist_directory=self.persist_dir, embedding_function=self.embeddings)

    def match_experiences(self, tech_stack: list):
        """
        Bonus: Smart Experience Matcher using Cosine Similarity.
        Compares student's tech stack against senior interview reports.
        """
        if not tech_stack:
            return []
        
        query = " ".join(tech_stack)
        results = self.vector_db.similarity_search(query, k=3)
        
        formatted_results = []
        for res in results:
            formatted_results.append({
                "company": res.metadata.get("company"),
                "content": res.page_content,
                "difficulty": res.metadata.get("difficulty", 5),
                "tech_stack": res.metadata.get("stack")
            })
        return formatted_results