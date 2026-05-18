from app.rag.vector_store import VectorStore

store = VectorStore()

def retrieve_examples(query):
    return store.search(query)