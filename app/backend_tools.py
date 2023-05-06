"""
Различные функции для бэкэнда
"""
import os
from datetime import datetime
import random
import yaml 

def read_config():
    with open("./conf/config.yaml", "r", encoding='utf-8') as yaml_file:
        config = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return config

config = read_config()

def add_timestamp(filename: str):
    """Добавляет время в название файла. Также добавляет рандомное число, чтобы файлы, присланные в одно время, не пересекались

    Args:
        filename (str): имя файла с расширением

    Returns:
        (str): имя файла с датой и временем и рандомным числом
    """
    return filename[:filename.rfind('.')] + '_'+datetime.now().strftime("%m-%d-%Y_%H.%M.%S")+str(random.random())+filename[filename.rfind('.'):]


def init_storage_path():
    """
    Инициализация папки с контентом, куда всё будет сохраняться
    """

    if not os.path.exists(config['content_storage_path']):
        os.mkdir(config['content_storage_path'])

    return config['content_storage_path']

