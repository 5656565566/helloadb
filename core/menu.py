from .log import logger


class Menu:
    def __init__(self) -> None:
        self.temp = {}

    def start(self):
        logger.opt(colors=True).info("欢迎使用<y> hello adb </y><g>你可以使用 help 获得帮助</g>")

    def in_run(self):
        try:
            cmd = input(">>>")

        except KeyboardInterrupt:
            print("")
            logger.opt(colors=True).info("程序已关闭 !")
            exit()

        if cmd == "help":
            print("list                列出脚本")
            print("run 数字id 循环次数 执行脚本 (使用 list 获取循环次数)")
            print("uiautomator 设备id  获取前台 Ui xml")
            print("screenshot 设备id   截图 (使用画图等软件处理后可用于找图 请勿压缩图片)")
            print("getactivity 设备id  获取当前屏幕上的app的activity")
            print("test                测试设备")
            print("devices             列出设备 与设备id")
            print("reload              重载程序")
            print("exit                退出程序")

        if cmd == "exit":
            logger.opt(colors=True).info("程序已关闭 !")
            exit()

        return cmd