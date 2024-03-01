import hashlib
import json
import queue
import asyncio
from typing import TYPE_CHECKING, Optional, Tuple, cast, List, Callable, Union, Dict, Any

import numpy as np
import requests
import logging
from sc2_rl_agent.starcraftenv_test.vector_database.Chroma_vdb import ChromaDBManager
from sc2_rl_agent.starcraftenv_test.utils.database import SqliteDB
from sc2_rl_agent.starcraftenv_test.config.config import PROJECT_ROOT_PATH, \
    MEMORY_DB_PATH
from sc2_rl_agent.starcraftenv_test.embedding.embedding_model import BaseEmbeddingModel, LocalEmbedding
import os
from sc2_rl_agent.starcraftenv_test.utils.Document import Document, create_documents


class NPCMemory:
    def __init__(self, npc_name: str, k: int, EmbeddingModel: BaseEmbeddingModel):
        self.npc_name = npc_name
        self.latest_k = queue.Queue(maxsize=k)
        self.vdb_path = os.path.join(PROJECT_ROOT_PATH, "data")
        self.embedding_model = EmbeddingModel
        self.sqlite_db = SqliteDB(db_name=f"{npc_name}_db.db")  # 以 NPC 的名字作为数据库名

        # 使用ChromaDBManager来管理chroma向量数据库
        self.vector_database = ChromaDBManager(self.vdb_path)
        # 创建或获取名为npc_name的集合
        self.vector_database.create_or_get_collection(name=self.npc_name)

    def embed_text(self, text: str) -> list:
        vector = self.embedding_model.embed_text(text)
        return vector

    def __del__(self):
        self.sqlite_db.close()

    async def add_memory(self, documents: list[dict], update_sql_db: bool = True, update_vector_db: bool = True):
        """
        添加记忆到数据库中。

        :param documents: 要添加的记忆列表。
        :param update_sql_db: 是否需要更新SQLite数据库。默认为True。
        :param update_vector_db: 是否需要更新向量数据库。默认为True。

        使用方法：
        await obj.add_memory(documents=[{...}], update_sql_db=True, update_vector_db=True)
        """

        # 如果需要更新SQLite数据库
        if update_sql_db:
            for doc in documents:
                try:
                    self.sqlite_db.insert_document(document_id=doc['id'], content=doc['content'],
                                                   metadata=doc['metadata'])
                except Exception as e:
                    print(f"Error adding document to SQLite DB: {e}")

        # 如果需要更新向量数据库
        if update_vector_db:
            try:
                embeddings = [self.embedding_model.embed_text(doc["content"]) for doc in documents]
                self.vector_database.add_documents(documents, embeddings)
            except Exception as e:
                print(f"Error adding document to Vector DB: {e}")

    def time_score(self, game_time: str, memory_game_time: str) -> float:
        """
        本来打算：计算记忆的时间分数，记忆越新分数越高。
        实现：均匀给分，无视时间的差；也就是说只有相关度被考虑
        :param game_time: 当前游戏时间戳
        :param memory_game_time: 记忆的游戏时间戳
        :return:
        """
        # TODO：实现记忆的时间分数
        # score = float(game_time) - float(memory_game_time)
        return 1

    async def search_memory(self, query_text: str, k: int = 1) -> dict:
        """
        搜索记忆
        :param query_text: 查询的文本
        :param k: 返回的记忆数量
        :return:dict: Similar documents.
        """
        text = query_text
        # 1. 使用embedding_model将文本转化为向量
        query_vector = self.embedding_model.embed_text(text)
        # 2. 使用向量数据库查询
        result = self.vector_database.query(embeddings=query_vector, n_results=k)
        # 3. 格式化结果
        formatted_result = {
            'ids': result.get('ids', [])[0] if result.get('ids') else [],
            'distances': result.get('distances', [])[0] if result.get('distances') else [],
            'metadatas': result.get('metadatas', [])[0] if result.get('metadatas') else [],
            'documents': result.get('documents', [])[0] if result.get('documents') else [],
            'embeddings': []  # 或者可以填入具体的嵌套列表，如果有的话
        }
        # 4. 返回格式化后的结果
        return formatted_result

    def abstract_memory(self, importance_threshold):
        """摘要记忆"""
        pass

    def clear_memory(self):
        """
        清空向量数据库中的记忆
        """
        self.vector_database.delete_collection(name=self.npc_name)

    async def get_last_k_memory(self, k: int, delete: bool = False) -> dict:
        """
        弹出并返回最新的K条记忆。

        :param k: 要弹出的记忆数量。
        :param delete: 是否在弹出后删除记忆，默认为True。
        :return: 弹出的记忆列表。
        example return {'ids': ['1', '2'], 'metadatas': [None, None], 'documents': ['Updated World', 'Hello World2']}
        """
        # 使用peek_documents获取最新的k条记忆
        recent_documents = self.vector_database.peek_documents(limit=k)

        # 如果需要删除这些记忆
        if delete:
            ids_to_delete = recent_documents['ids']
            self.vector_database.delete(ids=ids_to_delete)

        return recent_documents

    async def upsert_memory(self, memories: Union[Dict[str, Any], List[Dict[str, Any]]], update_sql_db: bool = True,
                            update_vector_db: bool = True) -> None:
        """
        插入或更新记忆到数据库中。

        :param memories: 要插入或更新的记忆。可以是单一记忆或记忆列表。
        :param update_sql_db: 是否需要更新SQLite数据库。默认为True。
        :param update_vector_db: 是否需要更新向量数据库。默认为True。

        使用方法：
        await obj.upsert_memory(memories={...} or [{...}, {...}], update_sql_db=True, update_vector_db=True)
        """

        if isinstance(memories, dict):
            memories = [memories]

        for memory in memories:
            document_id = memory["id"]
            content = memory["content"]
            metadata = memory.get("metadata", None)

            # 如果需要更新SQLite数据库
            if update_sql_db:
                try:
                    document_exists = self.sqlite_db.document_exists(document_id)

                    if document_exists:
                        self.sqlite_db.update_document(document_id=document_id, content=content, metadata=metadata)
                    else:
                        self.sqlite_db.insert_document(document_id=document_id, content=content, metadata=metadata)
                except Exception as e:
                    print(f"Error upserting document to SQLite DB: {e}")

            # 如果需要更新向量数据库
            if update_vector_db:
                try:
                    embedding = self.embedding_model.embed_text(content)
                    self.vector_database.upsert_documents(ids=[document_id], documents=[content],
                                                          embeddings=[embedding],
                                                          metadatas=[metadata])
                except Exception as e:
                    print(f"Error upserting document to Vector DB: {e}")

    def pop_memory(self, k: int, oldest: bool = True, delete=True, update_sql_db: bool = True,
                   update_vector_db: bool = True) -> Dict:
        """
        根据时间戳从数据库中弹出最旧或最新的k个记忆。

        :param k: 要弹出的记忆数量。
        :param oldest: 如果为True，则弹出最旧的记忆。如果为False，则弹出最新的记忆。
        :param delete: 如果为True，则在弹出记忆后从数据库中删除它们。
        :param update_sql_db: 是否需要更新SQLite数据库。默认为True。
        :param update_vector_db: 是否需要更新向量数据库。默认为True。

        :return: 弹出的记忆列表，格式化为统一的格式。

        使用方法：
        obj.pop_memory(k=2, oldest=True, delete=True, update_sql_db=True, update_vector_db=True)
        """

        memories = []
        # 如果需要更新SQLite数据库
        if update_sql_db:
            try:
                memories = self.sqlite_db.pop_documents(k=k, earliest=oldest, delete=delete)
            except Exception as e:
                print(f"Error popping document from SQLite DB: {e}")

        # 如果需要更新向量数据库
        if update_vector_db:
            try:
                ids_to_delete = [memory['id'] for memory in memories]
                self.vector_database.delete(ids=ids_to_delete)
            except Exception as e:
                print(f"Error popping document from Vector DB: {e}")

        # 格式化输出
        formatted_memories = {
            'ids': [],
            'documents': [],
            'metadatas': [],
            'embeddings': [],  # 如果可用
            # 'distances': []  # 如果可用
        }

        for memory in memories:
            formatted_memories['ids'].append(memory['id'])
            formatted_memories['documents'].append(memory['content'])
            formatted_memories['metadatas'].append(memory['metadata'])
            # 如果有embedding或distance信息，也加入对应的列表中

        return formatted_memories


async def test_function():
    # 1. 初始化
    npcMemory = NPCMemory(npc_name="test1", k=10, EmbeddingModel=LocalEmbedding())

    # 2. 添加记忆
    contents = ["Hello World", "Welcome to the Universe", "Hello World2","let`s go"]


    metadatas = [{"timestamp": "1"}, {"timestamp": "2"}, {"timestamp": "3"}, {"timestamp": "4"}]
    documents = create_documents(contents, metadatas)
    await npcMemory.add_memory(documents)

    # 3. 弹出记忆
    popped_memories = npcMemory.pop_memory(k=2, oldest=True, delete=True)
    print("popped_memories:", popped_memories)
    remain_memory = await npcMemory.get_last_k_memory(k=2, delete=False)
    print("get_last_k_memory:", remain_memory)
    # 4. 搜索记忆
    result = await npcMemory.search_memory("Hello", k=2)
    print("search_memory", result)
    print("result['ids][0]", result['ids'][0])

    # 5. 弹出剩余记忆
    popped_memories = npcMemory.pop_memory(k=1, oldest=True, delete=True)
    print("popped_memories:", popped_memories)

    # 6. 再次搜索记忆，确认记忆库为空
    result = await npcMemory.search_memory("Hello", k=1)


# 运行测试函数

asyncio.run(test_function())
