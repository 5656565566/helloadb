import yaml
import os

from pathlib import Path
from pydantic import BaseSettings

from .log import logger

class UserConfig(BaseSettings):
    loglevel : str = "DEBUG"
    default_offset : int = 3
    wifi_devices : list[str] = ["114.51.4.191:810"]
    appActivitys : dict = {"test" : "test"}
    low_battery : int = 20
    batteryRemind : bool = True
    shutdown_in_task_over : bool = False


class Config:
    def __init__(self, filename):
        self.filename = filename
        self.config = UserConfig()

    def load(self):

        if not os.path.exists(self.filename):
            self.save()

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                temp = yaml.load(f, Loader=yaml.Loader)
                self.config = UserConfig(**temp)
        except:
            logger.opt(colors=True).error("<r>配置文件错误, 即将重置</r>")
            self.save()

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            yaml.dump(self.config.dict(), f)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    def delete(self, key):
        del self.config[key]


config = Config(Path(os.getcwd()) / "config.yml")