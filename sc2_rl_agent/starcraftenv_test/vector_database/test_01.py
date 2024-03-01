class ChromaDBManager:
    def __init__(self, db_path: str):

        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = None
        self.path = db_path

    def list_collections(self):

        return self.client.list_collections()

    def create_or_get_collection(self, name: str, similarity_type: str = "cosine"):

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

        self.collection.add(
            documents=[doc["content"] for doc in documents],
            embeddings=embeddings,
            ids=[doc["id"] for doc in documents]
        )

    def get(self, ids: list[str] = None, limit: int = None, offset: int = None):

        return self.collection.get(ids=ids, limit=limit, offset=offset)

    def query(self, embeddings: List[float], n_results: int = 2, where: Optional[dict] = None,
              where_document: Optional[dict] = None, include=None) -> dict:

        if include is None:
            include = ["metadatas", "documents", "distances"]

        if not embeddings:
            raise ValueError("You must provide embeddings for querying.")

        return self.collection.query(query_embeddings=embeddings, n_results=n_results, where=where,
                                     where_document=where_document, include=include)

    def update(self, doc_id: str, new_content: Optional[str] = None,
               new_embedding: Optional[List[float]] = None):

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

        return self.collection.count()

    def peek_documents(self, limit: int = 10) -> dict:

        return self.collection.peek(limit=limit)

    def reset_database(self):

        self.client.reset()

    def modify_collection(self, name: Optional[str] = None, metadata: Optional[dict] = None) -> None:

        if self.collection:
            self.collection.modify(name=name, metadata=metadata)

    def updates(self, ids: list[str], embeddings: Optional[list] = None, metadatas: Optional[list] = None,
                documents: Optional[list] = None) -> None:

        if self.collection:
            self.collection.update(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def upsert_documents(self, ids: list[str], embeddings: Optional[list] = None, metadatas: Optional[list] = None,
                         documents: Optional[list] = None) -> None:

        if self.collection:
            self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def delete(self, ids: Optional[list[str]] = None, where: Optional[dict] = None,
               where_document: Optional[dict] = None):

        if self.collection:
            self.collection.delete(ids=ids, where=where, where_document=where_document)

    def delete_collection(self, name: str) -> None:

        self.client.delete_collection(name=name)
