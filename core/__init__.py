from pathlib import Path

import time
import os

from .log import logger, default_filter
from .script import ScriptManage, Screenshot, Script, GetActivity
from .config import config
from .menu import Menu
from .plugin import PluginManager

def run():
    """主运行函数"""
    logger.info("正在加载...")
    script = ScriptManage()
    plugin = PluginManager(["scrcpy"])
    plugin.load_plugins()

    scrcpy = plugin.get_plugin_executable_path("scrcpy.exe")

    if scrcpy:
        logger.info("检测到 scrcpy 的可执行文件")

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

            if "getactivity" in cmd:
                
                cmd = cmd.split(" ")

                script.run(int(cmd[1]) - 1, Script(name="run", files=Path(os.getcwd()), data = [GetActivity()]))

            if cmd == "reload":
                script.reload()

            if "run" in cmd:
                
                menu.temp["cmd"] = "run"

                scripts_name = list(script.scripts.keys())
                
                cmd = cmd.split(" ")

                if len(cmd) > 2:
                    script.script_run(scripts_name[int(cmd[1]) -1], int(cmd[2]))

                else:
                    script.script_run(scripts_name[int(cmd[1]) -1])

                while script.threads.keys():
                    time.sleep(3)
                    for thread in script.threads.keys():
                        if not script.threads[thread].is_alive():
                            break

            if cmd == "debug":
                for script in script.scripts.values():
                    logger.debug(script)
        
        except KeyboardInterrupt:

            if menu.temp.get("cmd") == "run":
                logger.opt(colors=True).info("脚本已停止运行！")
                exit()
            
            else:
                print("")
                logger.opt(colors=True).info("程序已关闭 !")
                exit()
        
        except Exception as e:
            logger.opt(colors=True).error(f"<r>发生错误</r> <y>{e}</y>")
        