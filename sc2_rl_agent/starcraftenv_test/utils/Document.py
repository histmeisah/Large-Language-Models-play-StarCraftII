import uuid
import json
import hashlib


class Document:
    def __init__(self, content: str, metadata: dict):
        """
        初始化方法
        :param content: 文档的内容。
        :param metadata: 文档的元数据，以字典形式存储。
        """
        self.id = self.generate_id(content, metadata)  # 使用生成的哈希值作为id
        self.content = content
        self.metadata = metadata

    @staticmethod
    def generate_id(content: str, metadata: dict) -> str:
        """根据文档内容和metadata生成ID（哈希值）"""
        metadata_str = json.dumps(metadata, sort_keys=True)  # 将metadata转换为排序后的字符串
        combined_str = content + metadata_str  # 将内容和metadata字符串拼接
        return hashlib.sha256(combined_str.encode('utf-8')).hexdigest()

    def to_dict(self) -> dict:
        """
        将Document对象转化为字典。
        :return: 包含Document对象信息的字典。
        """
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }

    def to_json_str(self) -> str:
        """
        将Document对象转化为JSON字符串。
        :return: 包含Document对象信息的JSON字符串。
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, doc_dict: dict):
        """
        从字典中创建Document对象。
        :param doc_dict: 包含Document对象信息的字典。
        :return: 一个新的Document对象。
        """
        doc = cls(
            content=doc_dict["content"],
            metadata=doc_dict["metadata"]
        )
        doc.id = doc_dict["id"]
        return doc

    @classmethod
    def from_json_str(cls, json_str: str):
        """
        从JSON字符串中创建Document对象。
        :param json_str: 包含Document对象信息的JSON字符串。
        :return: 一个新的Document对象。
        """
        doc_dict = json.loads(json_str)
        return cls.from_dict(doc_dict)


def create_documents(contents: list, metadatas: list) -> list:
    """
    根据提供的contents和metadatas列表创建多个Document对象。
    :param contents: 包含多个文档内容的列表。
    :param metadatas: 包含多个文档元数据的列表。
    :return: 包含多个Document对象（以字典形式表示）的列表。
    """
    documents = []
    for content, metadata in zip(contents, metadatas):
        document = Document(content, metadata)
        documents.append(document.to_dict())
    return documents

# 使用实例
# contents = ["Hello World", "Welcome to the Universe"]
# metadatas = [{"timestamp": "1"}, {"timestamp": "2"}]
#
# documents = create_documents(contents, metadatas)
# print(documents)  # 打印包含多个文档信息的列表
# 使用实例
# contents = ["Hello World", "Welcome to the Universe"]
# metadatas = [{"timestamp": "1"}, {"timestamp": "2"}]
#
# documents = []
# for content, metadata in zip(contents, metadatas):
#     document = Document(content, metadata)
#     documents.append(document.to_dict())
#
# print(documents)  # 打印包含多个文档信息的列表
