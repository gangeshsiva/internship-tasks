from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.chains import RetrievalQA

# 1) Load only a single page from the PDF
loader = PyPDFLoader("C:\\Users\\gangeshvar.s\\Desktop\\highlighttext\\input\\AI_11_ISC_2 1.pdf")
documents = loader.load()

# choose one page (0-indexed) — e.g., first page
page_docs = [documents[0]]

# 2) Split into chunks for embedding
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(page_docs)

# 3) Use Ollama embeddings (default: "nomic-embed-text")
emb = OllamaEmbeddings(model="nomic-embed-text")

# 4) Build FAISS vectorstore
vectorstore = FAISS.from_documents(chunks, emb)

retriever = vectorstore.as_retriever()

# 5) Create TinyLlama LLM
llm = OllamaLLM(model="tinyllama")

# 6) Build QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm, 
    retriever=retriever,
    chain_type="stuff"    #It takes all chunks returned by the retriever, concatenates them, and then sends them directly to the LLM with your question.
)

# 7) Ask a question
query = "What are the icd codes present in the page?"
answer = qa_chain.run(query)

print("\nANSWER:\n", answer)
