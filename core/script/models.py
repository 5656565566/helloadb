from pydantic import BaseModel
from typing import Any, Union, Optional, Type, TypeVar
from pathlib import Path

class Script(BaseModel):
    name : Optional[str]
    """脚本名称"""
    files : Path
    """完整路径"""
    data : Optional[list[Any]] = []
    """脚本内容"""
    
class BasicAdbFunc(BaseModel):
    """基础"""
    cmd : str
    """命令"""

TBasicAdbFunc = TypeVar("TBasicAdbFunc", bound=BasicAdbFunc)

class Name(BasicAdbFunc):
    cmd: Optional[str] = "name"
    name : str

class SpecialFunc(BaseModel):
    cmd : str
    """命令"""

class ShutdownPC(SpecialFunc):
    cmd: Optional[str] = "shutdown_pc"
    
class ShutdownDevices(SpecialFunc):
    cmd: Optional[str] = "shutdown_devices"

class GetActivity(SpecialFunc):
    cmd: Optional[str] = "get_activity"

class Custom(BaseModel):
    """自定义"""
    shell : str
    """自定义命令"""
    args : Optional[list[Any]]
    """参数"""

class Sleep(BaseModel):
    cmd: Optional[str] = "sleep"
    time : int
    random : Optional[Union[bool, int]] = False

AllFunc = Union[Type[TBasicAdbFunc], Type[SpecialFunc], Type[Sleep], Type[Custom]]

class Click(BasicAdbFunc):
    cmd: Optional[str] = "click"

    x : int
    """坐标 x"""
    y : int
    """坐标 x"""
    random : Optional[Union[bool, int]] = False
    """随机"""

class Swipe(BasicAdbFunc):
    cmd: Optional[str] = "swipe"

    x1 : int
    y1 : int
    x2 : int
    y2 : int
    time : float
    random : Optional[Union[bool, int]] = False
    """随机"""

class Keyevent(BasicAdbFunc):
    cmd: Optional[str] = "keyevent"
    key_id : int

class OpenApp(BasicAdbFunc):
    cmd: Optional[str] = "open_app"

    appActivity : str

class Screenshot(BasicAdbFunc):
    cmd: Optional[str] =  "screenshot"

class JudgFunc(SpecialFunc):
    conditions : str
    data : Optional[list[AllFunc]] = []

class FindPicture(JudgFunc):
    """找图判断"""
    cmd: Optional[str] =  "find_picture"
    similarity: Optional[float] =  0.02

class RandomRun(JudgFunc):
    """随机执行"""
    cmd: Optional[str] =  "random_run"
    probability: float

class End(SpecialFunc):
    """结束"""
    cmd: Optional[str] =  "end"

class FindPictureClick(SpecialFunc):
    """找图点击"""
    cmd: Optional[str] =  "find_picture_click"
    conditions : str
    similarity: Optional[float] =  0.02

class RunOne(SpecialFunc):
    """循环中只进行一次"""
    cmd: Optional[str] =  "run_one"
    data : Optional[list[AllFunc]] = []

class RunLoop(SpecialFunc):
    """循环"""
    cmd: Optional[str] =  "run_loop"
    loop_num: int
    data : Optional[list[AllFunc]] = []

class RunLoopIf(SpecialFunc):
    """条件循环"""
    cmd: Optional[str] =  "run_loop_if"
    conditions : str
    loop_if: list[str]
    data : Optional[list[AllFunc]] = []

class RunScipt(SpecialFunc):
    cmd: Optional[str] =  "run_scipt"
    data : Optional[Script] = None


class GetUiXml(BasicAdbFunc):
    cmd: Optional[str] =  "uiautomator"
    xml: Optional[str] = None