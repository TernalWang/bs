import json
import re
import shlex
from pathlib import Path

import duckdb

PROFILE = Path("/tmp/duckdb_profile.json")


def start(sf1, query_dir, tables):
    global _con, SF1, QUERY_DIR, TABLES
    SF1, QUERY_DIR, TABLES = sf1, query_dir, tables
    _con = duckdb.connect(":memory:")
    for t in TABLES:
        _con.execute(f"create table {t} as select * from read_parquet('{SF1}/{t}.parquet')")
    _con.execute("PRAGMA enable_profiling='json'")
    _con.execute(f"PRAGMA profiling_output='{PROFILE}'")
    print("[ready]")
    return _con


def dump_schema():
    con = duckdb.connect()                        # 独立连接:只读 parquet footer,不依赖 start() 载表
    ddl = []
    for t in TABLES:
        rows = con.execute(f"describe select * from read_parquet('{SF1}/{t}.parquet')").fetchall()
        cols = ",\n".join(f"    {c[0]:<16}{c[1]}" for c in rows)
        ddl.append(f"create table {t}\n(\n{cols}\n);")
    con.close()
    return "\n\n".join(ddl) + "\n"


def dump_scale_stats():
    con = duckdb.connect()                        # 独立连接:直接扫 parquet,不依赖 start() 载表
    scales = [SF1, SF1.parent / "sf100"]          # 只对比 sf1 与 sf100:100倍跨度
    no_range = ("VARCHAR", "CHAR", "BLOB", "JSON", "UUID", "LIST", "STRUCT", "MAP")  # 这些类型不打 min/max
    lines = ["数据量会增长到当前的1000倍。以下为 1倍与100倍两个规模实例实测的表行数、列 distinct 数(近似)与 min/max，随数据量增长的量不要当作设计常量："]
    for t in TABLES:
        for p in scales:
            f = f"{p}/{t}.parquet"
            n = con.execute(f"select count(*) from read_parquet('{f}')").fetchone()[0]
            s = con.execute(f"summarize select * from read_parquet('{f}')").fetchall()
            parts = [f"{c}_distinct={u}" + ("" if typ.upper().startswith(no_range) else f"[{mn}..{mx}]") for c, typ, mn, mx, u, *_ in s]
            lines.append(f"{t}@{p.name} rows={n}  " + "  ".join(parts))
    con.close()
    return "\n".join(lines) + "\n"


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
