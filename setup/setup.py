import json
import re
import shutil
from pathlib import Path

from human_ref.prompt.prompts import ARGS_PARSER_QUERY, ARGS_PARSER_READ, LOADER_FIELD, LOADER_ONE, QIMPL, QUERY_CASE
from sessions.sessions import make_session
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import run_query_json, dump_schema


def gen_args_parser(hpp: Path, query_dir: Path) -> None:
    parts = []
    for qfile in sorted(query_dir.glob("q*.txt"), key=lambda p: int(p.stem[1:])):
        n = qfile.stem[1:]
        names = dict.fromkeys(re.findall(r"\[([A-Z0-9_]+)\]", qfile.read_text()))
        fields = "".join(f"    std::string {k};\n" for k in names)
        reads = "".join(ARGS_PARSER_READ % {"n": n, "k": k} for k in names)
        parts.append(ARGS_PARSER_QUERY % {"n": n, "fields": fields, "reads": reads})
    hpp.write_text(hpp.read_text().replace("// ARGS_PARSER_QUERIES", "\n\n".join(parts)))


def gen_tables(sf1: Path) -> list[str]:
    return [p.stem for p in sorted(sf1.glob("*.parquet"))]


def gen_loader(hpp: Path, cpp: Path, tables: list[str]) -> None:
    fields = "".join(LOADER_FIELD % {"table": t} for t in tables)
    ones = "".join(LOADER_ONE % {"table": t} for t in tables)
    hpp.write_text(hpp.read_text().replace("// TABLES_FIELD", fields.rstrip("\n")))
    cpp.write_text(cpp.read_text().replace("// TABLES_LOAD_ONE", ones.rstrip("\n")))


def gen_query(cpp: Path, query_dir: Path) -> None:
    ns = [int(p.stem[1:]) for p in sorted(query_dir.glob("q*.txt"), key=lambda p: int(p.stem[1:]))]
    cpp.write_text(cpp.read_text().replace("// QN_INCLUDES", "\n".join(f'#include "q{n}_impl.hpp"' for n in ns)).replace("// QUERY_CASES", "\n".join(QUERY_CASE % {"n": n} for n in ns)))
    for n in ns:
        (cpp.parent / f"q{n}_impl.hpp").write_text(QIMPL % {"n": n})


def setup_workspace(queries: list[int], infra: Path, sf10: Path, query: Path, human_input: Path, tables: list[str], partitions: Path) -> None:
    print("Create workspace")
    WORKSPACE.mkdir(exist_ok=False)

    print("Create sessions.db in workspace")
    make_session("empty")

    print("Copy infra into workspace")
    shutil.copytree(infra, WORKSPACE / "infra", dirs_exist_ok=False)

    print("Copy sf10 into workspace")
    shutil.copytree(sf10, WORKSPACE / "parquets" / "sf10", dirs_exist_ok=False)

    print("Copy partitions into workspace")
    (dst := WORKSPACE / "parquets" / "partitions").mkdir(parents=True); [shutil.copy2(f, dst / f.name) for f in sorted(partitions.glob("*.parquet"))[:10]]

    print("Create final dirs")
    (WORKSPACE / "parquets" / "final" / "final_dump").mkdir(parents=True)
    (WORKSPACE / "parquets" / "final" / "final_restore").mkdir(parents=True)

    print("Copy querys into workspace")
    shutil.copytree(query, WORKSPACE / "querys", ignore=lambda d, ns: [n for n in ns if n.startswith("q") and n[1:-4].isdigit() and int(n[1:-4]) not in queries], dirs_exist_ok=False)

    print("Generate duckdb plans into workspace")
    (WORKSPACE / "duckdb_plans").mkdir()
    for n in queries:
        (WORKSPACE / "duckdb_plans" / f"plan_q{n}.txt").write_text(json.dumps(run_query_json((human_input / f"q{n}.txt").read_text().strip())[3], indent=2))

    print("Generate schema into workspace")
    (WORKSPACE / "duckdb_plans" / "schema.txt").write_text(dump_schema())

    print("Generate args_parser into workspace")
    gen_args_parser(WORKSPACE / "infra" / "include" / "args_parser.hpp", WORKSPACE / "querys")

    print("Generate loader into workspace")
    gen_loader(WORKSPACE / "infra" / "include" / "loader.hpp", WORKSPACE / "infra" / "loader" / "loader.cpp", tables)

    print("Generate query into workspace")
    gen_query(WORKSPACE / "infra" / "query" / "query_impl.cpp", WORKSPACE / "querys")
