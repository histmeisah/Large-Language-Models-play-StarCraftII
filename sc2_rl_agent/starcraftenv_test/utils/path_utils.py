# path_utils.py
import os


def get_current_directory():
    """
    获取当前脚本的目录
    :return: 当前脚本的目录路径
    """
    current_file_path = os.path.abspath(__file__)
    return os.path.dirname(current_file_path)


def construct_relative_path(relative_path_parts):
    """
    根据给定的部分构造相对于当前脚本目录的路径
    :param relative_path_parts: 相对路径的各个部分组成的列表
    :return: 构造出的相对路径
    """
    return os.path.join(get_current_directory(), *relative_path_parts)


def path_exists(path):
    """
    检查给定的路径是否存在
    :param path: 要检查的路径
    :return: 如果路径存在则返回True，否则返回False
    """
    return os.path.exists(path)


def calculate_relative_path(target, start):
    """
    计算从start到target的相对路径
    :param target: 目标绝对路径
    :param start: 开始绝对路径
    :return: 从start到target的相对路径
    """
    return os.path.relpath(target, start)


# 例如使用：
if __name__ == "__main__":
    utils_path = construct_relative_path(['sc2_rl_agent', 'starcraftenv_test', 'utils'])
    print(f"The path {utils_path} {'exists' if path_exists(utils_path) else 'does not exist'}.")
