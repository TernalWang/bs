from agents import function_tool

from tools.compile import compile_tool
from tools.shell import shell_tool
from tools.verify import duckdb_tool
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


@function_tool
def compile_cpp() -> str:
    """编译 workspace/infra 引擎(bash infra/build.sh),成功或编译错误原样返回。"""
    return compile_tool.compile_cpp()


@function_tool
def run_query(line: str) -> str:
    """执行基准查询(共22条)。使用前必须先读 querys/q<N>.txt 模板，查看其中的 [NAME] 占位符及上下文确定各参数取值。line 格式: '<N> <参数1> <参数2> ...'，按占位符首次出现的顺序以空格分隔填入；同名占位符只需填一次（自动替换所有出现处）；模板已含所需引号，传纯值即可。返回延迟(ms)、列名和结果行。"""
    cols, rows, latency_ms = duckdb_tool.run_query(line)
    header = "\t".join(cols)
    body = "\n".join("\t".join(map(str, r)) for r in rows)
    return f"latency: {latency_ms:.3f} ms\ncolumns: {header}\n{body}"
