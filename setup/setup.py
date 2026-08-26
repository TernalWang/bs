import json
import re
import shutil
from pathlib import Path

from human_ref.prompt.prompts import ARGS_PARSER_HEAD, ARGS_PARSER_QUERY, ARGS_PARSER_READ
from sessions.sessions import make_session
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import run_query_json, dump_schema


def gen_args_parser(query_dir: Path) -> str:
    parts = [ARGS_PARSER_HEAD]
    for qfile in sorted(query_dir.glob("q*.txt"), key=lambda p: int(p.stem[1:])):
        n = qfile.stem[1:]
        names = dict.fromkeys(re.findall(r"\[([A-Z0-9_]+)\]", qfile.read_text()))
        fields = "".join(f"    std::string {k};\n" for k in names)
        reads = "".join(ARGS_PARSER_READ % {"n": n, "k": k} for k in names)
        parts.append(ARGS_PARSER_QUERY % {"n": n, "fields": fields, "reads": reads})
    return "\n\n".join(parts) + "\n"


def setup_workspace(queries: list[int], infra: Path, tpch_sf1: Path, tpch_query: Path, human_input: Path) -> None:
    print("Create workspace")
    WORKSPACE.mkdir(exist_ok=False)

    print("Create sessions.db in workspace")
    make_session("empty")

    print("Copy infra into workspace")
    shutil.copytree(infra, WORKSPACE / "infra", dirs_exist_ok=False)

    print("Copy tpch sf1 into workspace")
    shutil.copytree(tpch_sf1, WORKSPACE / "parquets" / "sf1", dirs_exist_ok=False)

    print("Copy querys into workspace")
    shutil.copytree(tpch_query, WORKSPACE / "querys", dirs_exist_ok=False)

    print("Generate duckdb plans into workspace")
    (WORKSPACE / "duckdb_plans").mkdir()
    for n in queries:
        (WORKSPACE / "duckdb_plans" / f"plan_q{n}.txt").write_text(json.dumps(run_query_json((human_input / f"q{n}.txt").read_text().strip())[3], indent=2))

    print("Generate schema into workspace")
    (WORKSPACE / "duckdb_plans" / "schema.txt").write_text(dump_schema())

    print("Generate args_parser.hpp into workspace")
    (WORKSPACE / "infra" / "include" / "args_parser.hpp").write_text(gen_args_parser(WORKSPACE / "querys"))
