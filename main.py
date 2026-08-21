import asyncio
import shutil
from pathlib import Path
from agents import Runner

from agent.agent import agent
from sessions.sessions import make_session
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import start as start_duckdb

INFRA = Path(__file__).parent / "infra"

# ========== 核心 3：一句话进去，agent 自己循环调工具直到完成 ==========
if __name__ == "__main__":
    print("Create workspace")
    WORKSPACE.mkdir(exist_ok=False)

    print("Create sessions.db")
    make_session("empty")

    print("Copy infra into workspace")
    shutil.copytree(INFRA, WORKSPACE / "infra", dirs_exist_ok=False)

    print("Start duckdb")
    start_duckdb()

    print("模型思考期间无输出是正常的；每出现一行 [tool] = 模型调了一次工具")
    result = asyncio.run(Runner.run(agent, input="看看 workspace 里有什么，写一个 summary.txt 总结"))
    print("\n===== 对话轨迹 =====")
    for i, item in enumerate(result.new_items, 1):
        print("\n" + "=" * 60)
        print(f"第 {i} 项 | 类型: {item.type}")
        print("=" * 60)
        print(item)
    print("\n===== 最终输出 =====")
    print(result.final_output)
    print("\n===== usage =====")
    print(result.context_wrapper.usage)
