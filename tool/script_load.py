import os
import time
from pathlib import Path

from tool.menu import menu
from tool.log import Log
from . import script as _
# 这下开摆了


# 工作目录
mianPath = Path(os.getcwd())

# 脚本目录
scriptPath = Path(os.getcwd()) /'script'

if not scriptPath.is_dir():
    os.mkdir('script')

scriptDirList = []
'''
脚本路径列表
'''
scriptList = []
'''
脚本列表
'''
scriptIfDepth = 0

def script_dir_get():
    '''
    获取脚本
    '''
    for path in os.listdir(scriptPath):
        tempPath = scriptPath / path
        if os.path.isdir(tempPath):
            scriptDirList.append(tempPath)

def script_read():
    '''
    加载脚本
    '''
    for path in scriptDirList:
        try:
            script = open(path / "script.txt",encoding = "utf-8")

        except:
            Log.warning(f'未发现 script.txt 的脚本文件 {path} 无效')

        else:
            # 对脚本文件解析并写入缓冲区
            Log.debug(f'{path} 读取到脚本文件')

            data = {'path':path}
            cmd = []

            global scriptIfDepth

            for line in script.read().split('\n'):
                if line.count('name', 0, len(line)) or line.count('名', 0, len(line)):
                    name = line.split(' ')
                    if name[-1] == 'task':
                        pass
                    else:
                        data['name'] = name[-1]
                
                elif line.count('#', 0, len(line)):
                    # 注释
                    pass
                
                elif line.count('找图点击', 0, len(line)) or line.count('findclick', 0, len(line)):
                    findClick = no_space(line)
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["findclick", findClick[1]])')

                elif line.count('点击', 0, len(line)) or line.count('click', 0, len(line)):
                    click = no_space(line)
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["click", click[1], click[2]])')

                elif line.count('滑动', 0, len(line)) or line.count('swipe', 0, len(line)):
                    swipe = no_space(line)
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["swipe", swipe[1], swipe[2], swipe[3], swipe[4], swipe[5]])')

                elif line.count('延迟', 0, len(line)) or line.count('sleep', 0, len(line)):
                    sleep = no_space(line)
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["sleep", sleep[1]])')

                elif line.count('截图', 0, len(line)) or line.count('screenshot', 0, len(line)):
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["screenshot"])')

                elif line.count('找图判断', 0, len(line)) or line.count('findif', 0, len(line)):
                    findIf = no_space(line)
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["findif", findIf[1]])')
                    scriptIfDepth = scriptIfDepth + 1 # 条件语句深度加

                elif line.count('按键', 0, len(line)) or line.count('keyevent', 0, len(line)):
                    keyEvent = no_space(line)
                    exec(f'cmd{"[-1]" * scriptIfDepth}.append(["keyevent", keyEvent[1]])')

                elif line.count('结束', 0, len(line)) or line.count('end', 0, len(line)):
                    if scriptIfDepth > 0:
                        scriptIfDepth = scriptIfDepth - 1 # 条件语句深度减少
                    else:
                        Log.warning(f'发现错误的 结束语句 请检查脚本拼写')
                    
                elif line == '':
                    pass
                
                else:
                    Log.warning(f'发现错误语句 {line} 请检查脚本拼写')
            
            cmd.append(['end'])
            data['cmd'] = cmd

            script.close()

            scriptList.append(data)
            Log.info(f'脚本 {name[-1]} 加载成功')

def no_space(cmd:str):
    '''
    剔除空格
    '''
    if type(cmd) == str:
        cmd = cmd.split(' ')

    if "" in cmd:
        cmd.remove('')
        no_space(cmd)

    return cmd

def start():
    while True:

        threadNum = _.threadNum

        if threadNum == 0:

            if scriptDirList or scriptList:
                scriptList.clear()
                scriptDirList.clear()
                Log.debug(f'脚本已重载成功')

            else:
                Log.info('脚本加载完成')

            script_dir_get()
            script_read()

            for script in scriptList:
                print(f'{scriptList.index(script) + 1}. {script["name"]}')

            scriptList.append(len(scriptList))

            menu(scriptList)
        
        time.sleep(1)