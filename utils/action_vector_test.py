from vector_database.Chroma_vdb import ChromaDBManager
from embedding.embedding_model import LocalEmbedding
from utils.action_info import ActionDescriptions
from utils.action_extractor import *
import json
import os

class ActionDBManager:
    def __init__(self, db_path):
        self.manager = ChromaDBManager(db_path)
        self.embedding_model = LocalEmbedding()
        self.db_path = db_path

    def initialize_collection(self, collection_name, similarity_type="cosine"):
        self.manager.create_or_get_collection(name=collection_name, similarity_type=similarity_type)
        print(f"{collection_name} Collection created or retrieved.")
        print("vdb_path: ", self.db_path)

    def add_actions_to_db(self, actions_list):
        docs = [{"id": str(i), "content": action, "metadata": {"timestamp": 0.0}}
                for i, action in enumerate(actions_list)]
        embeddings = [self.embedding_model.embed_text(doc["content"]) for doc in docs]
        self.manager.add_documents(documents=docs, embeddings=embeddings)
        print("Documents added.")

    def search_actions(self, query, top_k=5):
        """
        使用给定的查询字符串搜索语义上相近的动作
        :param query: 查询字符串
        :param top_k: 返回最相近的前k个结果
        :return: 搜索结果列表
        """
        query_embedding = self.embedding_model.embed_text(query)
        query_result = self.manager.query(embeddings=query_embedding, n_results=top_k)

        # 处理查询结果
        formatted_result = {
            'ids': query_result['ids'][0] if query_result['ids'] else [],
            'documents': query_result['documents'][0] if query_result['documents'] else [],
            'metadatas': query_result['metadatas'][0] if query_result['metadatas'] else [],
            'embeddings': query_result.get('embeddings', [])
        }

        return formatted_result

    def populate_action_db(self, collection_name, race, similarity_type="cosine"):
        """
        初始化集合，并将动作列表添加到数据库中
        :param collection_name: 要创建或获取的集合的名称
        :param race: 指定的种族，例如"Protoss"或"Zerg"
        :param similarity_type: 用于集合的相似性度量类型，默认为"cosine"
        """
        self.initialize_collection(collection_name, similarity_type)
        action_desc = ActionDescriptions(race)
        actions_list = list(action_desc.flattened_actions.values())
        self.add_actions_to_db(actions_list)


def interactive_search(action_db_manager):
    """
    通过用户输入的查询字符串进行搜索，并打印搜索结果
    :param action_db_manager: ActionDBManager对象实例
    """
    while True:
        query = input("Please enter the action you are searching for (type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        search_results = action_db_manager.search_actions(query)
        print("Search results:", search_results)


def read_command(command_file):
    with open(command_file, 'r', encoding='utf-8') as file:
        command_data = json.load(file)
    return command_data


def extract_and_search_actions(command_file, db_path):
    # 初始化ActionDBManager对象
    action_db_manager = ActionDBManager(db_path)
    action_db_manager.initialize_collection("protoss_actions")

    # 读取命令
    commands = read_command(command_file)

    action_desc = ActionDescriptions("Protoss")  # 读取动作描述
    action_dict = action_desc.action_descriptions  # 读取动作字典
    action_extractor = ActionExtractor(action_dict)  # 初始化动作提取器
    empty_idx = action_desc.empty_action_id  # 空动作的索引

    for i in range(len(commands)):
        command = commands[i]
        if isinstance(command, list):
            command = " ".join(command)

        # 根据修改后的函数，提取动作
        action_ids, valid_actions = extract_actions_from_command(command, action_extractor=action_extractor,
                                                                 empty_idx=empty_idx,
                                                                 action_db_manager=action_db_manager)

        # 输出计数器和相关信息，以便于调试
        # print(f"Command Counter: {i}")
        # print("Command: ", command)
        print("Valid actions found: ", valid_actions)
        print("Action IDs: ", action_ids)
        for id in action_ids:
            if type(id) != int:
                raise ValueError(f"动作ID必须是整数，但是发现了 {type(id)} 类型的ID。")

        # 如果发现提取出现问题，可以进一步调试
        if not valid_actions:
            print(f"Extraction Problem at Command Counter: {i}")


def configure_protoss_actions(db_path):
    action_db_manager = ActionDBManager(db_path)
    action_db_manager.populate_action_db("protoss_actions", "Protoss")


def configure_terran_actions(db_path):
    action_db_manager = ActionDBManager(db_path)
    action_db_manager.populate_action_db("terran_actions", "Terran")


def configure_zerg_actions(db_path):
    action_db_manager = ActionDBManager(db_path)
    action_db_manager.populate_action_db("zerg_actions", "Zerg")


if __name__ == "__main__":
    relative_path_parts = ["..", "..", "utils", "actionvdb", "action_vdb"]
    db_path = os.path.join(*relative_path_parts)
    configure_zerg_actions(db_path)
    configure_protoss_actions(db_path)
