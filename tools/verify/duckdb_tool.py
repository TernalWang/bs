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


def dump_schema():
    con = duckdb.connect()                        # 独立连接:只读 parquet footer,不依赖 start() 载表
    ddl = []
    for t in TABLES:
        rows = con.execute(f"describe select * from read_parquet('{SF1}/{t}.parquet')").fetchall()
        cols = ",\n".join(f"    {c[0]:<16}{c[1]}" for c in rows)
        ddl.append(f"create table {t}\n(\n{cols}\n);")
    con.close()
    return "\n\n".join(ddl) + "\n"


def run_query(line):
    toks = shlex.split(line)                     # '1 "90"' → ['1','90']; 引号内空格不劈
    tpl = (QUERY_DIR / f"q{toks[0]}.txt").read_text()
    names = dict.fromkeys(re.findall(r"\[([A-Z0-9_]+)\]", tpl))   # 参数名去重,按首次出现保序
    sql = tpl
    for k, v in zip(names, toks[1:], strict=True):                # 每个名字只给一次值,同名全部替换
        sql = sql.replace(f"[{k}]", v)
    _con.execute(sql).fetchall()                  # 第一次只跑不取,预热 page cache/memory
    result = _con.execute(sql)                    # 第二次才计延迟,消除冷启动噪声
    rows = result.fetchall()
    cols = [d[0] for d in result.description]
    latency_ms = json.loads(PROFILE.read_text())["latency"] * 1000
    return cols, rows, latency_ms


def run_query_json(line):
    cols, rows, ms = run_query(line)
    prof = json.loads(PROFILE.read_text())
    return cols, rows, ms, prof
