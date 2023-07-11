from adbutils import AdbClient, adb, AdbTimeout, AdbDevice
from random import randint, random
from pathlib import Path
import os
import time
import threading
import cv2
import numpy as np

from .models import *
from ..log import logger

# 工作目录
mianPath = Path(os.getcwd())

# 缓存目录
tempPath = mianPath / "temp"

# 脚本目录
scriptPath = mianPath / "scripts"

if not tempPath.is_dir():
    os.mkdir("temp")

if not scriptPath.is_dir():
    os.mkdir("script")

def script_dir_get():
    """
    获取目录的脚本
    """
    script_dir_list  = []

    for path in os.listdir(scriptPath):
        tempPath = scriptPath / path
        if os.path.isdir(tempPath):
            script_dir_list.append(tempPath)

    return script_dir_list

def script_files_get():
    """
    获取单文件的脚本
    """
    script_files_list  = []

    for path in os.listdir(scriptPath):
        tempPath = scriptPath / path
        if os.path.isfile(tempPath):
            script_files_list.append(tempPath)

    return script_files_list

class ScriptManage:

    def __init__(self) -> None:
        self.default_offset = None
        self.scripts = {}
        self.script_dir_list = script_dir_get()
        self.script_files_list = script_files_get()
        self.adbclient = None
        self.devices = [] # 存储已经连接的adb设备
        self.wifis = [] # 存储需要连接的wifi设备
        self.threads = {}
        self.appActivitys = {}

    def list_scripts(self) -> list[str]:
        return self.scripts.keys()

    def reload(self):
        self.script_dir_list = script_dir_get()
        self.script_files_list = script_files_get()

        self.load()
        self.device_manage()
        

    def device_manage(self):
        if self.adbclient == None:
            self.adbclient = AdbClient("127.0.0.1", port=5037)

        for wifi in self.wifis:
            try:
                adb.connect(wifi, timeout=3.0)
                logger.opt(colors=True).success(f"<y>{wifi}</y> <g>连接成功</g>")

            except AdbTimeout as e:
                logger.opt(colors=True).error(f"<y>{wifi}</y> <r>连接失败</r>")

        self.devices = self.adbclient.device_list()

        logger.opt(colors=True).info(f"已经连接 <g>{len(self.adbclient.device_list())}</g> 台设备")

        if len(self.adbclient.device_list()) > 1:
            logger.opt(colors=True).debug(f"设备列表 :")

        for device in self.adbclient.device_list():
            logger.opt(colors=True).debug(f"设备 : <g>{device.serial}</g>")


    def load(self):

        for file in self.script_files_list:
            self.read_script_file(file)

        for path in self.script_dir_list:
            self.read_script_file(path)

        logger.opt(colors=True).info(f"已经加载 <g>{len(self.scripts.keys())}</g> 个脚本")

        logger.opt(colors=True).success(f"<g>加载完成</g>")

    def script_run(self, script_name, loop_num : int = 1):
        for device in self.devices:

            logger.opt(colors=True).info(f"<y>{device.serial}</y> : <g>开始运行脚本</g>")

            func = Func(device=device, script=self.scripts[script_name])
            func.default_offset = self.default_offset
            func.appActivitys = self.appActivitys
            
            for i in range(0, loop_num):
                logger.opt(colors=True).info(f"已经执行 <g>{i + 1}</g> 次 ! 剩余 <g>{loop_num - i - 1}</g> 次")
                func._run_script()

        if len(self.devices) == 0:
            logger.opt(colors=True).warning("<r>无设备 !</r>")

    def run(self, device_id, script):
        if device := self.devices[device_id]:

            logger.opt(colors=True).info(f"<y>{device.serial}</y> : <g>开始运行脚本</g>")

            func = Func(device=device, script=script)
            func._run_script()

        else:
            logger.opt(colors=True).warning("<r>设备不存在 !</r>")

    def read_script_file(self, path: Path):
        try:
            if path.is_file():
                script = open(path ,encoding = "utf-8")
                script_ = Script(name = path.name.split(".")[0] ,files = path)
            else:
                script = open(path / "script.txt" ,encoding = "utf-8")
                script_ = Script(name = path.name ,files = path)

        except:

            if ("script.txt" not in str(path)) and ("txt" not in str(path)):
                logger.error(f'未发现 script.txt 的脚本 {path} 无效')

            else:
                logger.error(f'脚本文件 {path} 读取失败')
        
        else:

            temp = [script_] # 用于控制脚本逻辑深度
            deep_num = 0 # 逻辑深度
            line_num = 0 # 显示行数

            for line in script.read().split('\n'):

                line_num = line_num + 1

                if "#" not in line and line != "": # 对 注释 缩进 进行屏蔽
                    cmd = list(filter(lambda x: x.strip() != "", line.split(" ")))             

                    if cmd[0] in ["name", "名称"]:
                        try:
                            script_.name = cmd[1]
                        except:
                            logger.opt(colors=True).error(f"<y>>脚本{script_.name}-line {line_num}</y> : <r>脚本名称不能为空</r>")

                    try:
                        deep, _script_cmd = self.script_cmd(cmd)

                    except:
                        logger.opt(colors=True).error(f"<y>脚本{script_.name}-line {line_num}</y> : <r>语句错误！</r>")

                    else:
                    
                        if deep > 0:
                            temp.append(_script_cmd)

                        temp[deep_num].data.append(_script_cmd)

                        if deep < 0 and deep_num == 0:
                            logger.opt(colors=True).warning(f"<y>line {line_num}</y> : <r>似乎没有语句可以结束</r>")
                            continue

                        deep_num = deep_num + deep

                        if deep_num == 0:
                            temp = [script_]
                        
            self.scripts[script_.name] = script_

            logger.debug(script_)


    def script_cmd(self, cmd: list):
        if cmd[0] in ["name", "名称"]:
            return (0, Name(name = cmd[1]))

        if cmd[0] in ["click", "点击"]:
            return (0, Click(x= cmd[1], y= cmd[2], random= (None if len(cmd) > 2 else cmd[3])))

        if cmd[0] in ["swipe", "滑动"]:
            return (0, Swipe(x1= cmd[1], y1= cmd[2], x2= cmd[3], y2= cmd[4], time= cmd[5], random= (None if len(cmd) > 5 else cmd[6])))

        if cmd[0] in ["keyevent", "模拟按键"]:
            return (0, Keyevent(key_id= cmd[1]))
        
        if cmd[0] in ["screenshot", "截图"]:
            return (0, Screenshot())

        if cmd[0] in ["app", "打开应用"]:
            return (0, OpenApp(appActivity= cmd[1]))
            
        if cmd[0] in ["sleep", "延迟"]:
            return (0, Sleep(time= cmd[1], random= (None if len(cmd) > 1 else cmd[2])))

        if cmd[0] in ["init","初始化"]:
            return (1, RunOne())

        if cmd[0] in ["findclick","找图点击"]:
            return (0, FindPictureClick(conditions= cmd[1]))

        if cmd[0] in ["findif","找图判断"]:
            return (1, FindPicture(conditions= cmd[1]))
        
        if cmd[0] in ["loop","循环"]:
            return (1, RunLoop(loop_num= cmd[1]))

        if cmd[0] in ["loopif","条件循环"]:
            return (1, RunLoopIf(conditions= cmd[1], loop_if= cmd[2:]))

        if cmd[0] in ["run","执行脚本"]:
            return (0, RunScipt(name= cmd[1]))
        
        if cmd[0] in ["random","随机"]:
            return (1, RandomRun(name= cmd[1]))

        if cmd[0] in ["end","结束"]:
            return (-1, End())
        

class Func:
    """执行adb脚本"""

    def __init__(self, device: AdbDevice, script: Script) -> None:
        self.default_offset = 3
        self.device = device
        self.temp = {"run_one" : []} # 用于脚本执行中的数据缓存
        self.script = script
        self.appActivitys = {}

    def _run_script(self, script = None):

        if script:
            for cmd in script:

                if cmd.cmd == "run_scipt":
                    return cmd.name

                func = getattr(self, cmd.cmd)
                if func(cmd):
                    self._run_script(cmd.data)
        else:
            for cmd in self.script.data:

                if cmd.cmd == "run_scipt":
                    return cmd.name

                func = getattr(self, cmd.cmd)
                if func(cmd):
                    self._run_script(cmd.data)

    def name(self, args: Name):
        logger.opt(colors=True).debug(f"<y>开始运行脚本</y> : <r>{args.name}</r>")

    def _offset(self, offset = None):
        """偏移"""

        if not offset:
            offset = self.default_offset
        
        return randint(-offset, offset)

    def _random(self, probability):
        """随机"""
        return random() < probability

    def sleep(self, args: Sleep):
        logger.debug("执行 Sleep")
        time.sleep(args.time)
        return 0

    def click(self, args: Click) -> int:

        x = args.x + (self._offset(args.random) if args.random else 0)
        y = args.y + (self._offset(args.random) if args.random else 0)

        self.device.click(x, y)
        logger.debug("执行 Click")
        return 0
    
    def swipe(self, args: Swipe) -> int:

        x1 = args.x1 + (self._offset(args.random) if args.random else 0)
        y1 = args.y1 + (self._offset(args.random) if args.random else 0)
        x2 = args.x2 + (self._offset(args.random) if args.random else 0)
        y2 = args.y2 + (self._offset(args.random) if args.random else 0)
        time = args.time
        self.device.swipe(x1, y1, x2, y2, time)
        logger.debug("执行 swipe")
        return 0
    
    def keyevent(self, args: Keyevent) -> int:
        self.device.keyevent(args.key_id)
        logger.debug("执行 Keyevent")
        return 0
    
    def open_app(self, args: OpenApp) -> int:

        appActivitys = self.appActivitys

        self.device.shell(f'am start {appActivitys[args.appActivity]}', timeout=2)

        logger.debug("执行 OpenApp")
        return 0
    
    def screenshot(self, args: Screenshot) -> int:

        path = self.script.files

        if ".txt" in str(self.script.files):
            path = tempPath

        try:
            self.device.screenshot().save(path / f"{self.device.serial}.png")
        except:
            logger.opt(colors=True).warning(f'无法为 <y>{self.device.serial}</y> 截图 请检查设备状态')
        else:
            logger.debug("执行 Screenshot")
        return 0
    
    def find_picture(self, args: FindPicture) -> int:
        if ".txt" in str(self.script.files):
            logger.opt(colors=True).warning(f'单文件脚本不支持此功能！')
            return 0

        path = self.script.files

        try:
            self.device.screenshot().save(path / f"{self.device.serial}.png")
        except:
            logger.opt(colors=True).warning(f'无法为 <y>{self.device.serial}</y> 截图 请检查设备状态')

        templatePath = path / f"{self.device.serial}.png"
    
        targetPath = path / f"{args.conditions if len(args.conditions.split('.')) > 1 else args.conditions + '.png'}"

        if not os.path.exists(targetPath):
            logger.opt(colors=True).error(f"未找到 <r>{targetPath}</r>")
            return 0

        template = cv2.imread(templatePath)
        target = cv2.imread(targetPath)

        find_pos = customized_match(target, template, (args.similarity))

        if find_pos:
            logger.debug("执行 FindPicture 匹配成功")
            return 1
        
        else:
            logger.debug("执行 FindPicture 匹配失败")
            return 0
        
    def end(self, args: End) -> int:
        return 0
    
    def find_picture_click(self, args: FindPictureClick):

        if ".txt" in str(self.script.files):
            logger.opt(colors=True).warning(f'单文件脚本不支持此功能！')
            return 0

        path = self.script.files

        try:
            self.device.screenshot().save(path / f"{self.device.serial}.png")
        except:
            logger.opt(colors=True).warning(f'无法为 <y>{self.device.serial}</y> 截图 请检查设备状态')

        templatePath = path / f"{self.device.serial}.png"
    
        targetPath = path / f"{args.conditions if len(args.conditions.split('.')) > 1 else args.conditions + '.png'}"

        if not os.path.exists(targetPath):
            logger.opt(colors=True).error(f"未找到 <r>{targetPath}</r>")
            return 0

        template = cv2.imread(templatePath)
        target = cv2.imread(targetPath)

        find_pos = customized_match(target, template, (args.similarity))

        if find_pos:
            self.device.click(find_pos[0], find_pos[1])

        logger.debug("执行 FindPictureClick")
        return 0
    
    def run_one(self, args: RunOne):
        logger.debug("执行 RunOne")

        if args in self.temp.get("run_one"):
            return 0
        
        else:
            self.temp["run_one"].append(args)

        self._run_script(args.data)

        return 0
    
    def run_loop(self, args: RunLoop):
        while(args.loop_num):
            logger.debug(f"执行 RunLoop 剩余{args.loop_num}次")
            self._run_script(args.data)
            args.loop_num = args.loop_num - 1

        return 0
    
    def random_run(self, args: RandomRun):
        if self._random(args.probability):
            logger.debug(f"执行 RandomRun ")
            self._run_script(args.data)

        else:
            logger.debug(f"不执行 RandomRun ")

        return 0

    def run_loop_if(self, args: RunLoopIf):
        logger.debug(f"执行 RunLoopIf TODO")
        return 0
    
def customized_match(target, template, threshold=0.02):
    # 如果目标图像和模板图像都带有透明通道，则需要提取透明通道
    if target.shape[2] == 4 and template.shape[2] == 4:
        target_alpha = target[:, :, 3]
        template_alpha = template[:, :, 3]

        # 将透明通道与图像通道合并，形成新的图像用于匹配
        target_rgb = target[:, :, :3]
        template_rgb = template[:, :, :3]
        target = cv2.cvtColor(target_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(template_rgb, cv2.COLOR_BGR2GRAY)
    else:
        # 将彩色图像转换为灰度图像
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    theight, twidth = target.shape[:2]

    # 使用模板匹配算法计算匹配结果
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)

    # 找到匹配结果中的最小值、最大值以及对应的位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 如果最小值大于自定义的阈值，说明匹配结果不好，返回None
    if min_val > threshold:
        return None

    # 计算目标图像中匹配位置的坐标（加上偏移量，使得匹配点位于模板图像的中心位置）
    x = min_loc[0] + twidth//3
    y = min_loc[1] + theight//3

    # 返回匹配位置的坐标
    return (x, y)