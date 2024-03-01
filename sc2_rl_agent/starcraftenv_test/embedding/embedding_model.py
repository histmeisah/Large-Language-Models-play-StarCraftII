from typing import Any, Dict, List
import os
import logging
from sentence_transformers import SentenceTransformer
from sc2_rl_agent.starcraftenv_test.config.config import MODEL_BASE_PATH, EMBEDDING_CONFIG

logger = logging.getLogger("EMBEDDING")
logger.setLevel(logging.DEBUG)


class SingletonEmbeddingModel(type):
    """
    用来实现单例模式的基类
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonEmbeddingModel, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseEmbeddingModel(metaclass=SingletonEmbeddingModel):
    """
    所有向量化模型的基类，必须实现embed_text方法
    """
    # 必须实现的一个属性:model_name
    model_name: str = None

    def embed_text(self, input_string: str) -> List[float]:
        pass


class LocalEmbedding(BaseEmbeddingModel):
    """
    用来向量化文本的组件，按照config，加载本地的huggingface权重并进行推理
    推荐使用:
        1. uer/sbert-base-chinese-nli
        2. sentence-transformers/all-mpnet-base-v2
        3. sentence-transformers/all-MiniLM-L6-v2
    """

    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2", vector_width: int = 768):
        #####################################
        # 转化model_name为huggingface的本地文件夹,
        # 例: uer/sbert-base-chinese-nli  ==> uer_sbert-base-chinese-nli
        #####################################
        self.model_path_hf = MODEL_BASE_PATH / "embedding" / model_name.replace("/", "_")
        print("model_path_hf", self.model_path_hf)
        self.model_name = model_name
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # 加载模型到本地
        if not os.path.exists(self.model_path_hf):
            logger.info(f"模型{model_name}的权重不存在，正在下载... 目标路径：{self.model_path_hf}")
            model = SentenceTransformer(model_name)
            model.save(str(self.model_path_hf))
            self.model = model
        else:
            logger.info(f"模型{model_name}的权重已存在，加载本地权重... 路径：{self.model_path_hf}")
            self.model = SentenceTransformer(self.model_path_hf)

        # 获取并检查向量宽度
        vector_width_from_weights: int = self.model.get_sentence_embedding_dimension()  # e.g: 768
        assert vector_width == vector_width_from_weights, f"模型{model_name}的向量宽度为{vector_width_from_weights}，与用户指定的{vector_width}不符"
        self.vector_width = vector_width

        logger.info(f"模型{model_name}的权重已加载，向量宽度为{vector_width_from_weights}")

    def embed_text(self, input_string: str) -> List[float]:
        """
        Embed a given string using the local embedding model.

        Args:
            input_string (str): The input text to be embedded.

        Returns:
            List[float]: The embedding vector for the input string.
        """
        try:
            vector = self.model.encode(input_string).tolist()
        except Exception as e:
            import traceback
            logger.error(f"向量化文本时出现错误：{e}")
            vector = [0.0] * self.vector_width
        return vector


if __name__ == "__main__":
    # os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
    # os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
    # local embedding
    embedding = LocalEmbedding()
    print(embedding.embed_text("你好"))
    # hugingface embedding

    """ 下面是几个可用的模型例子
    "model_id": "uer/sbert-base-chinese-nli",
    "dim": 768,

    "model_id": "sentence-transformers/all-MiniLM-L6-v2",
    "dim": 384,

    代码例：
    "uer/sbert-base-chinese-nli" ==> LocalEmbedding(model_name="uer/sbert-base-chinese-nli", vector_width=768)
    embedding = LocalEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", vector_width=384)
    #组件会检查material/embedding文件夹下是否有对应的权重，如果没有，会自动下载(没有的话就需要互联网链接)

    embedding = HuggingFaceEmbedding(model_name=NPC_MEMORY_CONFIG["hf_model_id"], vector_width=NPC_MEMORY_CONFIG["hf_dim"])
    # 线上的API请求非常不稳定会有超时的情况，所以不推荐使用
    """
