import asyncio
from pathlib import Path
from agents import Runner

from agent.agent import make_rw_agent, make_rwcv_agent, print_report
from human_ref.prompt.prompts import RWCV_INSTRUCTIONS, RW_INSTRUCTIONS, STORAGE_CODE_INPUT, overall_storage_prompt, query_code_input, storage_plan_prompt, todo_instructions, todo_prompt
from sessions.sessions import make_session
from setup.setup import setup_workspace, gen_tables
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import start as start_duckdb

INFRA = Path(__file__).parent / "infra"
BENCHMARK = Path(__file__).parent / "human_ref" / "agentlogs"
SF10 = BENCHMARK / "parquets" / "sf10"
QUERY = BENCHMARK / "querys"
HUMAN_INPUT = BENCHMARK / "input"
TABLES = gen_tables(SF10)
QUERIES = [1,2,3]
PARTITIONS = BENCHMARK / "parquets" / "partitions"


if __name__ == "__main__":
    print("Start duckdb")
    start_duckdb(SF10, QUERY, TABLES)

    print("Setup workspace")
    setup_workspace(QUERIES, INFRA, SF10, QUERY, HUMAN_INPUT, TABLES, PARTITIONS)

    for n in QUERIES:
        print(f"Generate query {n} storage plan")
        result = asyncio.run(Runner.run(make_rw_agent(RW_INSTRUCTIONS), input=storage_plan_prompt(n),
            session=make_session(f"plan_q{n}"), max_turns=75))
        print_report(result)

    print("Generate overall storage plan")
    result = asyncio.run(Runner.run(make_rw_agent(RW_INSTRUCTIONS), input=overall_storage_prompt(QUERIES),
        session=make_session("storage"), max_turns=700))
    print_report(result)

    # print("Archive and delete seprate storage plan")
    # for n in QUERIES:
    #     p = WORKSPACE / f"storage_plan{n}.txt"
    #     asyncio.run(make_session(f"plan_q{n}_archive").add_items([{"role": "assistant", "content": p.read_text()}]))
    #     p.unlink()

    # print("Generate TODO based on overall storage plan")
    # result = asyncio.run(Runner.run(make_rwcv_agent(RWCV_INSTRUCTIONS), input=todo_prompt(QUERIES),
    #     session=make_session("storage_todo"), max_turns=700))
    # print_report(result)
    # for f in ("TODO_storage.md", *(f"TODO_query{n}.md" for n in QUERIES)):
    #     (WORKSPACE / f).read_text()

    # print("start coding")
    # result = asyncio.run(Runner.run(make_rwcv_agent(todo_instructions("TODO_storage.md")), input=STORAGE_CODE_INPUT, session=make_session("code_storage"), max_turns=700))
    # print_report(result)

    # for n in QUERIES:
    #     result = asyncio.run(Runner.run(make_rwcv_agent(todo_instructions(f"TODO_query{n}.md")), input=query_code_input(n), session=make_session(f"code_q{n}"), max_turns=700))
    #     print_report(result)
