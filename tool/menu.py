import time

from .log import Log
from .script import run

taskList = []
'''
#TODO 任务存储 计划性执行脚本
task(执行配置中的任务)
'''

def menu(scriptList:list):
        scriptNum = input('请选择要运行的脚本 标号 或 exit(退出) reload(重载脚本)>>>')
        if scriptNum == 'exit':
            exit()

        elif scriptNum == 'task':
            pass

        elif scriptNum == 'reload':
            pass

        elif scriptNum:
            try:
                scriptNum = int(scriptNum)
            except:
                Log.warning('未知的序号')
                menu(scriptList)
                        
            else:
                if scriptList[-1] < scriptNum:
                        Log.warning('超出最大序号')
                        menu(scriptList)
                            
                else:
                    try:
                        loopNum = int(input('输入循环次数>>>'))
                    except:
                        Log.warning('未知的数字')
                        menu(scriptList)
                    else:
                        if loopNum == 0 or loopNum > 1000000000:
                                Log.warning('无意义数字')
                                menu(scriptList)
                        else:
                            print("\n\n\n")
                            run(scriptList[scriptNum-1], loopNum, scriptList[scriptNum-1]['path'])