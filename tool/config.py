wifiDevice = []
'''
请填写wifi设备表
格式

['ip:port','ip:port',...]

如
['114.51.4.191:9801','x.x.x.x:xxxx']

'''
logLevel = 'DEBUG'
'''
日志等级
NO 无错误以外日志
DEBUG 全日志
INFO 运行状态日志
'''
batteryRemind = True
'''
电池电量提醒
默认为 True 设置为 False 关闭
'''
battery = 20
'''
当电量为 battery% 时提醒
默认 低于 20
'''
appActivity = {
    '快手' : 'com.kuaishou.nebula/com.yxcorp.gifshow.HomeActivity'
}
'''
app Activity
{'app name' : 'activity'}

用于指令 开启应用 xx
        app xxx
'''