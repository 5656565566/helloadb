from adbutils import AdbClient, adb, AdbTimeout
from random import randint, random
from pathlib import Path
import os
import time
import threading
import cv2
import difflib

from .log import Log
from . import config

# 工作目录
mianPath = Path(os.getcwd())

# 缓存目录
tempPath = Path(os.getcwd()) /'temp'

if not tempPath.is_dir():
    os.mkdir('temp')

threadNum = 0

wifiDevice = config.wifiDevice

def run(script:dict, loopNum:int, path:Path):
    '''
    运行脚本
    '''

    global threadNum

    my = AdbClient(host="127.0.0.1", port=5037)
    if len(wifiDevice) >= 1:

        for n in wifiDevice:
            try:
                adb.connect(n, timeout=3.0)
            except AdbTimeout as e:
                print(e)

    if len(my.device_list()) == 0:
        Log.warning('不存在已经连接的adb设备')
        exit()

    else:
        Log.info(f'已连接 {len(my.device_list())} 台设备')

        for d in my.device_list():
            thread = threading.Thread(name=str(threadNum),target=run_scrpit,args=(script, loopNum, d, str(threadNum), path))
            thread.start()
            threadNum = threadNum + 1
        
        batteryLevelNoticeThread = threading.Thread(name='battery',target=battery_level_notice,args=(my,))
        batteryLevelNoticeThread.start()


def battery_level_notice(my:AdbClient):
    batteryRemind = config.batteryRemind
    battery = config.battery
    noticeDevice = []
    
    try:
        from win10toast import ToastNotifier
    except:
        EnableWin10Toast = False
        Log.debug(f'未找到库 win10toast')
    
    else:
        EnableWin10Toast = True
    
    while batteryRemind and threadNum != 0:
        for d in my.device_list():

            try:
                deviceBattery = int(difflib.get_close_matches('level', d.shell("dumpsys battery", timeout=0.5).replace(' ','').split('\n'), 1, cutoff=0.6)[0].split(':')[1])
            except:
                if d:
                    Log.debug(f'设备 {d.serial} 电量无法获取')
                else:
                    Log.debug(f'设备可能掉线')

            else:

                if deviceBattery < battery and d.serial not in noticeDevice:
                    Log.warning(f'设备 {d.serial} 电量低于 {battery}')
                    
                    if EnableWin10Toast:
                        toaster = ToastNotifier()
                        toaster.show_toast(
                            "电量提醒",
                            f"设备 {d.serial} 电量低于 {battery}",
                            icon_path=None,
                            duration=10)
                    
                    noticeDevice.append(d.serial)
                if deviceBattery >= battery and d.serial in noticeDevice:
                    Log.debug(f'设备 {d.serial} 电量恢复预设值')
                    noticeDevice.remove(d.serial)
                    
        time.sleep(2)


def run_scrpit(script:dict, loopNum:int, my:AdbClient, dId:str, path:Path):

    global threadNum

    while (loopNum > 0):
        Log.info(f'{my.serial} 脚本执行剩余 {loopNum} 次')
        for cmd in script['cmd']:
            if "click" in cmd:
                click(my, cmd)
            
            elif "keyevent" in cmd:
                Log.debug(f'模拟按下 {cmd[1]} 键')
                my.keyevent(cmd[1])

            elif "sleep" in cmd:
                sleep(cmd)

            elif "swipe" in cmd:
                swipe(my, cmd)

            elif "screenshot" in cmd:
                screenshot(my, dId)

            elif "findclick" in cmd:
                screenshot(my, dId)
                find_click(my, dId, cmd[1], path)

            elif "app" in cmd:
                open_app(my, cmd)
                script['cmd'].remove(cmd)

            elif "end" in cmd:
                Log.debug(f'脚本执行到末尾')

            elif "findif" in cmd:

                screenshot(my, dId)
                if screenshot_find(dId, cmd[1], path):

                    Log.debug(f'条件找图 {cmd[1]} 判断成功')

                    scriptif(my, cmd[2:], dId, path)

        loopNum = loopNum - 1

    threadNum = threadNum - 1

    if threadNum == 0:
        Log.info(f'脚本执行完成')
        

        
def scriptif(my:AdbClient, cmdIf:list, dId:str, path:Path):
    for cmd in cmdIf:
        if "click" in cmd:
            click(my, cmd)
        
        elif "keyevent" in cmd:
            Log.debug(f'模拟按下 {cmd[1]} 键')
            my.keyevent(cmd[1])

        elif "sleep" in cmd:
            sleep(cmd)

        elif "swipe" in cmd:
            swipe(my, cmd)

        elif "screenshot" in cmd:
            screenshot(my, dId)

        elif "findclick" in cmd:
            screenshot(my, dId)
            find_click(my, dId, cmd[1], path)

        elif "app" in cmd:
            open_app(my, dId)

        elif "findif" in cmd:

            screenshot(my, dId)
            if screenshot_find(dId, cmd[1], path):

                Log.debug(f'条件找图 {cmd[1]} 判断成功')

                scriptif(my, cmd[2:], dId, path)


def open_app(my:AdbClient, cmd:list):
    '''
    开启app操作
    '''
    appActivity = config.appActivity

    if cmd[1] in appActivity:
        my.shell(f'am start {appActivity[cmd[1]]}', timeout=0.5)
        Log.debug(f'{cmd[1]} 打开成功')
    else:
        Log.warning(f'{cmd[1]} 不存在于 appActivity 记录中 前往config 配置后重启程序')

def click(my:AdbClient, cmd:list):
    '''
    点击操作
    '''
    try:
        my.click(int(cmd[1])+randint(1,3), int(cmd[2])+randint(1,3))
    except:
        Log.warning(f'发现语句 {" ".join(cmd)} 执行错误 请检查语句参数')

    else:
        Log.debug(f'{my.serial} 执行点击')
    
def sleep(cmd:list):
    '''
    延迟操作
    '''
    try:
        time.sleep(int(cmd[1])+random())
    except:
        Log.warning(f'发现语句 {" ".join(cmd)} 执行错误 请检查语句参数')
    else:
        Log.debug(f'执行延迟')
    
def swipe(my:AdbClient, cmd:list):
    '''
    滑动操作
    '''
    try:
        my.swipe(int(cmd[1])+randint(1,3), int(cmd[2])+randint(1,3), int(cmd[3])+randint(1,3), int(cmd[4])+randint(1,3), float(cmd[5]))
    except:
        Log.warning(f'发现语句 {" ".join(cmd)} 执行错误 请检查语句参数')
    else:
        Log.debug(f'{my.serial} 执行滑动')

def screenshot(my:AdbClient, dId:str):
    '''
    截图操作
    '''
    try:
        my.screenshot().save(tempPath / f'{dId}.jpg')
    except:
        Log.warning(f'无法为 {my.serial} 截图请检查设备状态')
    else:
        Log.debug(f'为 {my.serial} 截图')

def find_click(my:AdbClient, dId:str, source:str, path:Path):
    
    templatePath = ".\\" + str(tempPath).split('\\')[-1] + f"\\{dId}.jpg"
    
    targetPath = ".\\" + "script\\" + str(path).split('\\')[-1] + "\\" + source
    
    template = cv2.imread(templatePath)
    target = cv2.imread(targetPath)
    
    find_pos = find_f(target, template)

    Log.debug(f'{my.serial} 找图 {source} 点击')

    if find_pos:
        my.click(find_pos[0]+randint(1,3), find_pos[1]+randint(1,3))

def screenshot_find(dId:str, source:str, path:Path):
    '''
    在截图中寻找
    '''
    templatePath = ".\\" + str(tempPath).split('\\')[-1] + f"\\{dId}.jpg"
    
    targetPath = ".\\" + "script\\" + str(path).split('\\')[-1] + "\\" + source
    
    template = cv2.imread(templatePath)
    target = cv2.imread(targetPath)
    try:
        return find_f(target,template)
    except:
        Log.warning(f'找图 {source} 资源不存在 检查相关脚本文件夹内是否含有该文件')

def find_f(target, template):
    '''
    找图匹配
    '''
    theight, twidth = target.shape[:2]
    # 执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	# 如果匹配度小于99%，就认为没有找到。

    if min_val > 0.02:
        return None
    
    # 绘制矩形边框，将匹配区域标注出来
    x = min_loc[0] + twidth//3
    y = min_loc[1] + theight//3
    return (x, y)