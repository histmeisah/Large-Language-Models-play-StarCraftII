import chromadb

from typing import TYPE_CHECKING, Optional, Tuple, cast, List, Callable
from sc2_rl_agent.starcraftenv_test.embedding.embedding_model import LocalEmbedding
import numpy as np


class ChromaDBManager:
    def __init__(self, db_path: str):
        """
        Initialize the ChromaDBManager.

        Args:
            db_path (str): Path to the database.
        """
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None
        self.path = db_path

    def list_collections(self):
        """
        List all collections in the database.
        list_collections() -> Sequence[Collection]
        example return: [collection(name="my_collection", metadata={})]
        """
        return self.client.list_collections()

    def create_or_get_collection(self, name: str, similarity_type: str = "cosine"):
        """
        Create or get a collection with a given name and similarity type.

        Args:
            name (str): The name of the collection.
            similarity_type (str): One of 'L2', 'ip', or 'cosine'.
            余弦距离=1−余弦相似度

            # Squared L2 (Euclidean Squared Distance)
            d = sum((Ai - Bi)^2). Smaller is more similar.

            Inner Product "Distance"
            d = 1.0 - sum(Ai * Bi). Smaller is more similar.

            Cosine Distance (not similarity)
            d = 1.0 - (sum(Ai * Bi) / (sqrt(sum(Ai^2)) * sqrt(sum(Bi^2)))). Smaller is more similar.

        """
        similarity_mapping = {
            "L2": "l2",
            "ip": "ip",
            "cosine": "cosine"
        }

        if similarity_type not in similarity_mapping:
            raise ValueError("similarity_type must be one of 'L2', 'ip', or 'cosine'.")

        metadata = {"hnsw:space": similarity_mapping[similarity_type]}
        self.collection = self.client.get_or_create_collection(name=name, metadata=metadata)

    def add_documents(self, documents: list[dict], embeddings: list[list[float]]):
        """
        Add documents and their embeddings to the collection.

        Args:
            documents (list[dict]): List of documents to add. Each document should have an 'id' and 'content'.
            embeddings (list[list[float]]): List of embeddings corresponding to the documents.

        Example:
            docs = [{"id": "1", "content": "This is a sentence"}, {"id": "2", "content": "Another sentence"}]
            embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            manager.add_documents(documents=docs, embeddings=embeddings)
        """
        print(f"Adding documents: {documents}")
        self.collection.add(
            documents=[doc["content"] for doc in documents],
            embeddings=embeddings,
            ids=[doc["id"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents]
        )

    def get(self, ids: list[str] = None, limit: int = None, offset: int = None):
        """
        Get embeddings and their associated data from the data store.

        Args:
            ids (list[str], optional): List of document IDs to retrieve.
            limit (int, optional): Maximum number of documents to retrieve.
            offset (int, optional): Offset to start retrieving documents from.

        Returns:
            dict: Retrieved documents.

        Example:
            retrieved_docs = manager.get(ids=["1", "2"], limit=10, offset=0)
        """
        return self.collection.get(ids=ids, limit=limit, offset=offset)

    def query(self, embeddings: List[float], n_results: int = 2, where: Optional[dict] = None,
              where_document: Optional[dict] = None, include=None) -> dict:
        """
        Query the collection for similar documents based on the provided embeddings.

        Args:
            embeddings (list[list[float]]): The embeddings to query for similar documents.
            n_results (int, optional): Number of similar documents to retrieve. Defaults to 2.
            where (dict, optional): A filter to apply on the results. E.g. `{"color" : "red"}`.
            where_document (dict, optional): A filter to apply on the document texts. E.g. `{$contains: {"text": "hello"}}`.
            include (list[str], optional): A list of what to include in the results. Defaults to ["metadatas", "documents", "distances"].

        Returns:
            dict: Similar documents.

        Example:
            similar_docs_by_embedding = manager.query(embeddings=[[...]], n_results=5)
        """

        if include is None:
            include = ["metadatas", "documents", "distances"]

        if not embeddings:
            raise ValueError("You must provide embeddings for querying.")

        return self.collection.query(query_embeddings=embeddings, n_results=n_results, where=where,
                                     where_document=where_document, include=include)

    def update(self, doc_id: str, new_content: Optional[str] = None,
               new_embedding: Optional[List[float]] = None):
        """
        Update a document's content and/or its embedding in the collection.
        ... [rest of the docstring]
        """
        current_data = self.collection.get(ids=[doc_id])

        # 检查返回的数据结构
        if not current_data or 'ids' not in current_data or not current_data['ids']:
            raise ValueError(f"No data found for document ID: {doc_id}")

        # 获取当前的embedding和metadata
        current_embedding = current_data['embeddings'][0] if 'embeddings' in current_data and current_data[
            'embeddings'] else None
        current_metadata = current_data['metadatas'][0] if 'metadatas' in current_data and current_data[
            'metadatas'] else None

        # 使用新的embedding（如果提供了）
        if new_embedding is not None:
            current_embedding = new_embedding

        # 确保所有的数据都是列表形式
        ids_list = [doc_id]
        embeddings_list = [current_embedding] if current_embedding is not None else None
        metadatas_list = [current_metadata] if current_metadata is not None else None
        documents_list = [new_content] if new_content is not None else None

        # 更新文档
        self.collection.update(
            ids=ids_list,
            embeddings=embeddings_list,
            metadatas=metadatas_list,
            documents=documents_list
        )

    def count_documents(self) -> int:
        """
        Count the total number of embeddings added to the database.

        Returns:
            int: Total number of embeddings.

        Example:
            total_docs = manager.count_documents()
        """
        return self.collection.count()

    def peek_documents(self, limit: int = 10) -> dict:
        """
        Get the first few results in the database up to the specified limit.

        Args:
            limit (int, optional): Number of documents to retrieve. Defaults to 10.

        Returns:
            dict: First few documents.

        Example:
            first_docs = manager.peek_documents(limit=5)
        """
        return self.collection.peek(limit=limit)

    def reset_database(self):
        """
        Reset the database.

        Example:
            manager.reset_database()
        """
        self.client.reset()

    def modify_collection(self, name: Optional[str] = None, metadata: Optional[dict] = None) -> None:
        """
        Modify the collection name or metadata.

        Args:
            name (str, optional): New name for the collection.
            metadata (dict, optional): New metadata for the collection.

        Example:
            manager.modify_collection(name="new_name", metadata={"type": "new_type"})
        """
        if self.collection:
            self.collection.modify(name=name, metadata=metadata)

    def updates(self, ids: list[str], embeddings: Optional[list] = None, metadatas: Optional[list] = None,
                documents: Optional[list] = None) -> None:
        """
        Update the embeddings, metadatas, or documents for provided ids.

        Args:
            ids (list[str]): List of document IDs to update.
            embeddings (list, optional): List of embeddings.
            metadatas (list, optional): List of metadatas.
            documents (list, optional): List of documents.

        Example:
            doc_ids = ["1", "2"]
            docs = [{"content": "Updated content 1"}, {"content": "Updated content 2"}]
            manager.updates(ids=doc_ids, documents=docs)
        """
        if self.collection:
            self.collection.update(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def upsert_documents(self, ids: list[str], embeddings: Optional[list] = None, metadatas: Optional[list] = None,
                         documents: Optional[list] = None) -> None:
        """
        Update the embeddings, metadatas, or documents for provided ids, or create them if they don't exist.

        Args:
            ids (list[str]): List of document IDs to upsert.
            embeddings (list, optional): List of embeddings.
            metadatas (list, optional): List of metadatas.
            documents (list, optional): List of documents.

        Example:
            doc_ids = ["3", "4"]
            docs = [{"content": "New content 3"}, {"content": "New content 4"}]
            manager.upsert_documents(ids=doc_ids, documents=docs)
        """
        if self.collection:
            self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def delete(self, ids: Optional[list[str]] = None, where: Optional[dict] = None,
               where_document: Optional[dict] = None):
        """
        Delete the embeddings based on ids and/or a where filter.

        Args:
            ids (list[str], optional): List of document IDs to delete.
            where (dict, optional): Filter for which documents to delete.
            where_document (dict, optional): Filter based on document content.

        Example:
            manager.delete(ids=["1", "2"])
        """
        if self.collection:
            self.collection.delete(ids=ids, where=where, where_document=where_document)

    def delete_collection(self, name: str) -> None:
        """
        Arguments:

        name - The name of the collection to delete.

        Raises:

        ValueError - If the collection does not exist.

        Example:
            manager.delete_collection(name="my_collection")
        """

        self.client.delete_collection(name=name)


def test_chroma():
    # 初始化
    db_path = "./test_db"  # 你可以修改为你想要的路径
    manager = ChromaDBManager(db_path)

    # 测试创建/获取集合
    manager.create_or_get_collection(name="test_collection", similarity_type="L2")
    print("Collection created or retrieved.")
    embedding_model = LocalEmbedding()
    docs = [
        {"id": "3", "content": "hellow, world", "metadata": {"timestamp": 0.0}},
        {"id": "4", "content": "welcome to the starcraft2", "metadata": {"timestamp": 0.0}},
    ]
    embeddings = [embedding_model.embed_text(doc["content"]) for doc in docs]
    manager.add_documents(documents=docs, embeddings=embeddings)
    print("Documents added.")

    # 测试查询文档
    query_embedding = embedding_model.embed_text("world")
    query_result = manager.query(embeddings=query_embedding)
    print("Query results:", query_result)
    #
    # # 测试更新文档内容
    new_content = "hellow, OpenAI"
    new_embedding = embedding_model.embed_text(new_content)
    manager.update(doc_id="3", new_content=new_content, new_embedding=new_embedding)
    updated_doc = manager.get(ids=["3"])
    print("Updated document:", updated_doc)
    #
    # # 测试文档数量
    count = manager.count_documents()
    print(f"Total number of documents: {count}")
    #
    # # 测试peek_documents
    first_docs = manager.peek_documents(limit=1)
    print("First document:", first_docs)
    #
    # # 测试删除文档
    manager.delete(ids=["1"])
    remaining_doc = manager.get(ids=["2", "3", "4"])
    print("Remaining document after deletion:", remaining_doc)

    # 最后，测试删除集合 (这将删除整个集合及其中的所有文档)
    # manager.delete_collection(name="test_collection")
    # print("Collection deleted.")
    print("list of collections", manager.client.list_collections())


# Query results: {'ids': [['3', '4']], 'distances': [[0.39938256714043896, 0.8612450285182921]], 'metadatas': [[None, None]], 'embeddings': None, 'documents': [['hellow, world', 'welcome to the starcraft2']]}
def test_chroma_2():
    client = chromadb.PersistentClient(path="./test_db")
    collection = client.get_or_create_collection(name="2134", metadata={"hnsw:space": "cosine"})
    print("Collection created or retrieved.")
    collection.add(
        embeddings=[[1.2, 2.3, 4.5], [6.7, 8.2, 9.2]],
        documents=["This is a document", "This is another document"],
        metadatas=[{"source": "my_source"}, {"source": "my_source"}],
        ids=["id3", "id4"]
    )
    print("Documents added.")
    result=collection.peek(limit=1)
    print("result:",result)





if __name__ == "__main__":
    # 调用测试函数
    test_chroma()
