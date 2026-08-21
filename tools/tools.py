from agents import function_tool

from tools.shell import shell_tool
from tools.write import write_tool

# ========== 核心 1：工具 = 普通函数 ==========
# 具体实现在 shell/ 和 write/ 下，WORKSPACE 唯一定义在 shell_tool.py；这里只做 function_tool 包装


@function_tool
def run_shell(command: str) -> str:
    """在 workspace 下执行 shell 命令，返回输出。"""
    return shell_tool.run_shell(command)


@function_tool
def write_file(path: str, content: str) -> str:
    """在 workspace 下创建/覆盖文件。"""
    return write_tool.write_file(path, content)
