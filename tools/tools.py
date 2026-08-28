import csv
import time
from pathlib import Path

from agents import function_tool

from tools.compile import compile_tool
from tools.shell import shell_tool
from tools.verify import duckdb_tool
from tools.write import write_tool

EXPECTED_DIR = Path("/tmp/expected_result")  # run_query 标准答案 CSV 的落盘目录

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
    """执行基准查询。使用前参考 querys/q<N>.txt 模板，查看其中的 [NAME]占位符及上下文确定各参数取值。
    line 格式: '<N> <参数1> <参数2> ...'，按占位符首次出现的顺序以空格分隔填入；同名占位符只需填一次（自动替换所有出现处）；模板已含所需引号，传纯值即可。
    返回延迟(ms)和标准答案CSV的路径；CSV约定与引擎输出一致(delimiter=','、escapechar='\\\\'、quotechar='"'、header)。
    拿你引擎的csv与它核验：先抽查，全部一致再做整文件对比；DOUBLE 浮点列（schema 为 DOUBLE 的列或 avg() 等浮点计算）允许末位舍入级差异，但须严谨：用脚本量化确认误差确属舍入量级，其余列必须完全一致。"""
    cols, rows, latency_ms = duckdb_tool.run_query(line)
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPECTED_DIR / f"{time.time_ns()}.csv"
    # csv 模块 doublequote 默认 True：引号翻倍，escapechar 只转义反斜杠——须与引擎写入约定一致
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter=",", quotechar='"', escapechar="\\")
        w.writerow(cols)
        w.writerows(rows)
    return (f"latency: {latency_ms:.3f} ms\n标准答案已写入 {path}\n"
            "拿你引擎的csv与它核验：先抽查，全部一致再做整文件对比")
