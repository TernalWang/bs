import json
import re
import shlex
from pathlib import Path

import duckdb

SF1 = Path(__file__).resolve().parents[2] / "tpch_parquet" / "sf1"
QUERY_DIR = Path(__file__).resolve().parents[2] / "tpch_query"
PROFILE = Path("/tmp/duckdb_profile.json")
TABLES = ["region", "nation", "customer", "supplier",
          "part", "partsupp", "orders", "lineitem"]

_con = None


def start():
    global _con
    if _con is not None:
        return _con
    con = duckdb.connect(":memory:")
    con.execute("PRAGMA threads=1")                # 载表+查询全单核:first-touch 集中,NUMA 友好
    for t in TABLES:
        con.execute(f"create table {t} as select * from read_parquet('{SF1}/{t}.parquet')")
    con.execute("PRAGMA enable_profiling='json'")
    con.execute(f"PRAGMA profiling_output='{PROFILE}'")
    print("[ready]")
    _con = con
    return con


def run_query(line):
    toks = shlex.split(line)                     # '1 "90"' → ['1','90']; 引号内空格不劈
    tpl = (QUERY_DIR / f"q{toks[0]}.txt").read_text()
    names = dict.fromkeys(re.findall(r"\[([A-Z0-9_]+)\]", tpl))   # 参数名去重,按首次出现保序
    sql = tpl
    for k, v in zip(names, toks[1:], strict=True):                # 每个名字只给一次值,同名全部替换
        sql = sql.replace(f"[{k}]", v)
    result = _con.execute(sql)
    rows = result.fetchall()
    cols = [d[0] for d in result.description]
    latency_ms = json.loads(PROFILE.read_text())["latency"] * 1000
    return cols, rows, latency_ms


def run_query_json(line):
    cols, rows, ms = run_query(line)
    prof = json.loads(PROFILE.read_text())
    return cols, rows, ms, prof
