import sqlite3
import json
from typing import List, Optional, Union


class SqliteDB:
    def __init__(self, db_name='example1.db'):
        """
        初始化方法，用于创建或连接到一个数据库。

        :param db_name: 数据库文件的名字。默认为 'example.db'。
        """
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

        # 创建数据表，如果不存在的话
        self.c.execute('''CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, content TEXT)''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS metadata (document_id TEXT PRIMARY KEY, timestamp REAL, metadata_json TEXT)''')
        self.conn.commit()

    def insert_document(self, document_id: str, content: str, metadata: dict):
        """
        向数据库插入一个新文档和相关的元数据。

        :param document_id: 文档的唯一ID。
        :param content: 文档的内容。
        :param metadata: 包含元数据的字典，应包含时间戳。
        """
        timestamp = metadata.get('timestamp', 0.0)  # 从元数据中获取时间戳
        self.c.execute('SELECT id FROM documents WHERE id = :id', {"id": document_id})
        if self.c.fetchone() is not None:
            print(f"Document with id {document_id} already exists!")
            return
        self.c.execute('INSERT INTO documents VALUES (:id, :content)', {"id": document_id, "content": content})
        self.c.execute('INSERT INTO metadata VALUES (:document_id, :timestamp, :metadata_json)',
                       {"document_id": document_id, "timestamp": timestamp, "metadata_json": json.dumps(metadata)})
        self.conn.commit()

    def query_documents(self, query: str) -> List[dict]:
        """
        执行SQL查询并返回结果。

        :param query: SQL查询字符串。
        :return: 包含查询结果的字典列表。
        """
        results = []
        for row in self.c.execute(query):
            doc = {"id": row[0], "content": row[1], "timestamp": row[2], "metadata": json.loads(row[3])}
            results.append(doc)
        return results

    def update_document(self, document_id: str, content: Optional[str] = None, metadata: Optional[dict] = None,
                        timestamp: Optional[float] = None):
        """
        更新现有文档的内容、元数据和时间戳。

        :param document_id: 要更新的文档的ID。
        :param content: (可选)新的内容。
        :param metadata: (可选)新的元数据字典。
        :param timestamp: (可选)新的时间戳。
        """
        if content:
            self.c.execute('UPDATE documents SET content = :content WHERE id = :id',
                           {"content": content, "id": document_id})
        if metadata:
            self.c.execute('UPDATE metadata SET metadata_json = :metadata_json WHERE document_id = :document_id',
                           {"metadata_json": json.dumps(metadata), "document_id": document_id})
        if timestamp:
            self.c.execute('UPDATE metadata SET timestamp = :timestamp WHERE document_id = :document_id',
                           {"timestamp": timestamp, "document_id": document_id})
        self.conn.commit()

    def delete_document(self, document_id: str):
        """
        从数据库中删除文档和相关的元数据。

        :param document_id: 要删除的文档的ID。
        """
        self.c.execute('DELETE FROM documents WHERE id = :id', {"id": document_id})
        self.c.execute('DELETE FROM metadata WHERE document_id = :document_id', {"document_id": document_id})
        self.conn.commit()

    def pop_documents(self, k: int, earliest: bool = True, delete: bool = True) -> List[dict]:
        """
        获取并返回最早或最晚的k个文档，并可选地从数据库中删除它们。

        :param k: 要弹出的文档数量。
        :param earliest: 如果为True，弹出最早的文档；否则弹出最晚的文档。
        :param delete: 如果为True，从数据库中删除弹出的文档。
        :return: 包含弹出的文档的字典列表。
        """
        order = 'ASC' if earliest else 'DESC'
        query = f'''SELECT d.id, d.content, m.timestamp, m.metadata_json FROM documents d
                    INNER JOIN metadata m ON d.id = m.document_id
                    ORDER BY m.timestamp {order} LIMIT {k}'''
        docs = self.query_documents(query)

        if delete:
            for doc in docs:
                self.delete_document(doc['id'])

        return docs

    def document_exists(self, document_id: str) -> bool:
        self.c.execute('SELECT id FROM documents WHERE id = :id', {"id": document_id})
        return self.c.fetchone() is not None

    def close(self):
        self.conn.close()


# 使用例子：
# db = SqliteDB()
# db.insert_document("3", "Hello, Python!",  {"language": "Python","timestamp": 1.0})
# db.insert_document("4", "Hello, Java!", {"language": "Java", "timestamp": 2.0})
#
# print("Earliest Document:")
# print(db.pop_documents(1, earliest=True, delete=False))
# print("Latest Document:")
# print(db.pop_documents(1, earliest=False, delete=False))
#
# db.close()

