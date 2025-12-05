from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_classic.chains import RetrievalQA
import json
import sys
from datetime import datetime




def load_json_file(file_path,logfile):
    """
    Reads a JSON file and returns the data.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    except Exception as e:
        log_exception(e,"load_json_file",logfile)
    

# Usage

retrieved_data = load_json_file(file_path,logfile)

def langchainrag(retrieved_data,logfile):
    try:
        question = retrieved_data.get('query',[])
        docs = retrieved_data.get('retrieved_chunks',[])

        print(question)
        print(docs)

        # Extract only the text
        texts = [chunk['text'] for chunk in docs]

        # Check query
        if not (isinstance(question, str) and question.strip()):       #isinstance checks whether it is a particular data type and also whether it is empty or not
            log_exception("Query is invalid or empty.","langchainrag",logfile)

        for i, chunk in enumerate(docs, start=1):
            if not (isinstance(chunk.get('text'), str) and chunk.get('text').strip()):
                log_exception(f"Chunk {i} has invalid or empty text.","langchainrag",logfile)
            if not isinstance(chunk.get('page'), int):
                log_exception(f"Chunk {i} has invalid page number.","langchainrag",logfile)

        # 3) Use Ollama embeddings (default: "nomic-embed-text")
        emb = OllamaEmbeddings(model="nomic-embed-text")
        
        # 4) Build FAISS vectorstore
        vectorstore = FAISS.from_texts(texts, emb)

        retriever = vectorstore.as_retriever()
        
        # 5) Create TinyLlama LLM
        llm = OllamaLLM(model="tinyllama")
        
        # 6) Build QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, 
            retriever=retriever,
            return_source_documents=False    
        )

        answer = qa_chain.run(question)

        output={"result":answer}


        print("\nANSWER:\n", answer)

        with open(jsonpath, "w") as g:
            json.dump(output, g ,indent=4)

    except Exception as e:
        log_exception(e,"langchainrag",logfile)

langchainrag(retrieved_data,logfile)