import asyncio
import json
import shutil
from pathlib import Path
from agents import Runner

from agent.agent import agent
from sessions.sessions import make_session
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import run_query_json, start as start_duckdb

INFRA = Path(__file__).parent / "infra"
TPCH_SF1 = Path(__file__).parent / "tpch_parquet" / "sf1"
TPCH_QUERY = Path(__file__).parent / "tpch_query"
HUMAN_INPUT = Path(__file__).parent / "human_ref" / "input"

if __name__ == "__main__":
    print("Create workspace")
    WORKSPACE.mkdir(exist_ok=False)

    print("Create sessions.db")
    make_session("empty")

    print("Copy infra into workspace")
    shutil.copytree(INFRA, WORKSPACE / "infra", dirs_exist_ok=False)

    print("Copy tpch sf1 into workspace")
    shutil.copytree(TPCH_SF1, WORKSPACE / "parquets" / "sf1", dirs_exist_ok=False)

    print("Copy tpch_query into workspace")
    shutil.copytree(TPCH_QUERY, WORKSPACE / "querys", dirs_exist_ok=False)

    print("Start duckdb")
    start_duckdb()

    print("Generate duckdb plans")
    (WORKSPACE / "duckdb_plans").mkdir()
    for n in range(1, 23):
        (WORKSPACE / "duckdb_plans" / f"plan_q{n}.txt").write_text(json.dumps(run_query_json((HUMAN_INPUT / f"q{n}.txt").read_text().strip())[3], indent=2))

    print("模型思考期间无输出是正常的；每出现一行 [tool] = 模型调了一次工具")
    result = asyncio.run(Runner.run(agent, input="不要浪费太多token, 试试每一个tools功能正不正常就行然后写个 summary.txt"))
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
