from . import config

# 日志等级
logLevel = config.logLevel
'''
NO 无错误以外日志
DEBUG 全日志
INFO 运行状态日志
'''

# 哼哼哼啊啊啊啊啊啊啊啊啊啊啊啊啊

if logLevel == 'NO':
    print('[INFO] 当前静默模式运行中...')

class Log:
    @staticmethod
    def debug(log):
        if logLevel == 'DEBUG':
            print(f"[DEBUG] {log}")

    @staticmethod
    def info(log):
        if not logLevel == 'NO':
            print(f"[INFO] {log}")

    @staticmethod
    def warning(log):
            print(f"[WARNING] {log}")