import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from constants.constants import DB_DIRECTORY

class DatabaseManager:
    def __init__(self):
        """Initialize database parameters and setup embedding function."""
        load_dotenv()
        self.open_api_key = os.environ.get('OPENAI_API_KEY')
        self.database_name = os.environ['DATABASE_NAME']
        self.database_dir = DB_DIRECTORY
        self.embedding_model = os.environ['OPENAI_EMBEDDINGMODEL']
        self.embedding_func = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.open_api_key,
            model_name=self.embedding_model
        )
        self.client = self._initialize_client()
        self.collection = self._get_or_create_collection()

    def _initialize_client(self):
        """Create the database directory if it doesn't exist and initialize Chroma client."""
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)
            print("Database directory created successfully.")
        print("create database")

        return chromadb.PersistentClient(path=self.database_dir)

    def _get_or_create_collection(self):
        """Retrieve or create the collection with the specified name and embedding function."""
        print("get or create collection")
        collection = self.client.get_or_create_collection(
            name=self.database_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_func
        )

        return collection

    def add_data(self, data, metadata, ids_list):
        """Add data and corresponding metadata to the collection."""
        if not isinstance(data, list) or not isinstance(metadata, list):
            raise ValueError("Data and metadata should be lists.")
        print("begin add data")

        self.collection.add(documents=data, metadatas=metadata, ids=ids_list)
        # batch_size = 1
        # for i in range(0, len(data), batch_size):
        #     batch_data = data[i:i + batch_size]
        #     batch_metadata = metadata[i:i + batch_size]
        #     batch_ids = id[i:i + batch_size]
        #     self.collection.add(documents=batch_data, metadatas=batch_metadata, ids=batch_ids)
        #     print(f"Added batch {i // batch_size + 1}")

        print("Data added to the database successfully.")

    def remove_database(self):
        """Remove the collection from the database."""
        self.client.delete_collection(name=self.database_name)
        print("Database collection removed successfully.")
    def delete_data(self, filename):
        self.collection.delete(where={"filename":filename})
    def query_collection(self, questions: [str]) -> [str]:
        """Get data from vector database"""
        print('Get data from vector database')
        collection_answer = self.collection.query(
            query_texts=questions,
            n_results=10,
        )

        collection_documents = collection_answer['documents']
        collection_distances = collection_answer['distances']
        collection_id = collection_answer['ids']
        collection_metadatas = collection_answer['metadatas']
        documents = []

        for i in range(len(questions)):
            for j in range(len(collection_distances[0])):
                documents.append({'id': collection_id[i][j], 'document': collection_documents[i][j],
                                  'score': collection_distances[i][j], 'metadatas': collection_metadatas[i][j]})
        documents_sorted = sorted(documents, key=lambda x: x['score'], reverse=False)
        unique_docs = {}
        top_documents = []

        for doc in documents_sorted:
            if doc['id'] not in unique_docs:
                unique_docs[doc['id']] = doc
                if doc['metadatas']['raw_text'] not in top_documents:
                    top_documents.append(doc['metadatas']['raw_text'])
            if len(top_documents) == 20:
                break
        return top_documents