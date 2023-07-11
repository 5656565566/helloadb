from pathlib import Path
import os

from .log import logger, default_filter
from .script import ScriptManage, Screenshot, Script
from .config import config
from .menu import Menu


def run():
    """主运行函数"""
    logger.info('正在加载...')
    script = ScriptManage()

    config.load()

    default_filter.level = config.config.loglevel

    script.wifis = config.config.wifi_devices
    script.default_offset = config.config.default_offset
    script.appActivitys = config.config.appActivitys

    script.device_manage()
    script.load()
    
    menu = Menu()
    menu.start()

    while True:
        try:
            cmd = menu.in_run()

            if cmd == "list":
                scripts = script.scripts.keys()
                logger.opt(colors=True).info(f"已经加载 <g>{len(scripts)}</g> 个脚本")

                n = 0

                for script in scripts:
                    n = n + 1
                    logger.opt(colors=True).info(f"{n}. <g>{script}</g>")

            if cmd == "devices":
                
                n = 0

                device_list = script.adbclient.device_list()

                logger.opt(colors=True).info(f"已经连接 <g>{len(device_list)}</g> 台设备 !")

                if len(device_list) > 1:
                    logger.opt(colors=True).debug(f"设备列表 :")

                for device in device_list:
                    n = n + 1
                    logger.opt(colors=True).debug(f"{n}. <g>{device.serial}</g>")

            if "screenshot" in cmd:

                cmd = cmd.split(" ")

                script.run(int(cmd[1]) - 1, Script(name="run", files=Path(os.getcwd()), data = [Screenshot()]))

            if cmd == "reload":
                script.reload()

            if "run" in cmd:
                
                scripts_name = list(script.scripts.keys())
                
                cmd = cmd.split(" ")

                if len(cmd) > 2:
                    script.script_run(scripts_name[int(cmd[1]) -1], int(cmd[2]))

                else:
                    script.script_run(scripts_name[int(cmd[1]) -1])

            if cmd == "debug":
                for script in script.scripts.values():
                    logger.debug(script)

        except Exception as e:
            logger.opt(colors=True).error(f"<r>发生错误</r> <y>{e}</y>")