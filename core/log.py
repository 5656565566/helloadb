import sys
import loguru

from typing import Union

logger = loguru.logger

class Filter:
    def __init__(self) -> None:
        self.level: Union[int, str] = "INFO"

    def __call__(self, record):
        module_name: str = record["name"]
        module = sys.modules.get(module_name)
        if module:
            module_name = getattr(module, "__module_name__", module_name)
        record["name"] = module_name.split(".")[0]
        levelno = (
            logger.level(self.level).no if isinstance(self.level, str) else self.level
        )
        return record["level"].no >= levelno


logger.remove()

default_format = (
    "[<g>{time:YY-MM-DD HH:mm:ss}</g>] "
    "[<lvl>{level:^7}</lvl>] "
    # "<c><u>{name}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}"
)
default_filter = Filter()

# 配置日志输出到控制台并带有颜色
logger.add(
    sink=sys.stdout,
    format=default_format,
    filter=default_filter,
    level=0,
    colorize=True,
    diagnose=False,
)

if __name__ == "__main__":
    # 示例日志输出
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.success('Success message')