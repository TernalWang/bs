import asyncio
import json
import shutil
from pathlib import Path
from agents import Runner

from agent.agent import print_report, rwcv_agent, rw_agent
from sessions.sessions import make_session
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import run_query_json, dump_schema, start as start_duckdb

INFRA = Path(__file__).parent / "infra"
TPCH_SF1 = Path(__file__).parent / "tpch_parquet" / "sf1"
TPCH_QUERY = Path(__file__).parent / "tpch_query"
HUMAN_INPUT = Path(__file__).parent / "human_ref" / "input"

if __name__ == "__main__":
    print("Create workspace")
    WORKSPACE.mkdir(exist_ok=False)

    print("Create sessions.db")
    session_storage = make_session("storage")
    session_query06 = make_session("query06")
    session_query14 = make_session("query14")

    print("Copy infra into workspace")
    shutil.copytree(INFRA, WORKSPACE / "infra", dirs_exist_ok=False)

    print("Copy tpch sf1 into workspace")
    shutil.copytree(TPCH_SF1, WORKSPACE / "parquets" / "sf1", dirs_exist_ok=False)

    print("Copy tpch_query into workspace")
    shutil.copytree(TPCH_QUERY, WORKSPACE / "querys", dirs_exist_ok=False)

    print("Start duckdb")
    start_duckdb()

    print("Generate duckdb plans into workspace")
    (WORKSPACE / "duckdb_plans").mkdir()
    for n in range(1, 23):
        (WORKSPACE / "duckdb_plans" / f"plan_q{n}.txt").write_text(json.dumps(run_query_json((HUMAN_INPUT / f"q{n}.txt").read_text().strip())[3], indent=2))

    print("Generate schema into workspace")
    (WORKSPACE / "duckdb_plans" / "schema.txt").write_text(dump_schema())

    print("模型思考期间无输出是正常的；每出现一行 [tool] = 模型调了一次工具")

    result = asyncio.run(Runner.run(rw_agent, input="""你的任务是分析给定的查询负载，为其中访问到的每张表设计一份有创造性的内存(in-memory)存储布局方案。
        你可以输出详细的自由格式文本，不仅探讨常规存储布局建议，也探讨非常规、新颖、甚至"疯狂"的存储设计。
        鼓励你加入额外的想法：新的分区策略、投机式的编码技术、实验性的列分组与数据组织方式。
        对每张被访问的表，大胆展开：混合布局、SoA/AoS(数组结构/结构数组)的各种变体、新颖的列编码、自适应分区等。
        把这次当作突破现有规范的机会，提出未来感的、甚至离经叛道的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理

        查询负载见文件：querys/q6.txt。
        DuckDB 对该查询生成的执行计划见文件：duckdb_plans/plan_q6.txt。
        表结构见文件：duckdb_plans/schema.txt。

        基于以上查询、执行计划和表结构，为被访问的表给出详细且有创造性的存储布局方案，写入文件 storage_plan06.txt。""",
        session=session_query06))
    print_report(result)

    result = asyncio.run(Runner.run(rw_agent, input="""你的任务是分析给定的查询负载，为其中访问到的每张表设计一份有创造性的内存(in-memory)存储布局方案。
        你可以输出详细的自由格式文本，不仅探讨常规存储布局建议，也探讨非常规、新颖、甚至"疯狂"的存储设计。
        鼓励你加入额外的想法：新的分区策略、投机式的编码技术、实验性的列分组与数据组织方式。
        对每张被访问的表，大胆展开：混合布局、SoA/AoS(数组结构/结构数组)的各种变体、新颖的列编码、自适应分区等。
        把这次当作突破现有规范的机会，提出未来感的、甚至离经叛道的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理

        查询负载见文件：querys/q14.txt。
        DuckDB 对该查询生成的执行计划见文件：duckdb_plans/plan_q14.txt。
        表结构见文件：duckdb_plans/schema.txt。

        基于以上查询、执行计划和表结构，为被访问的表给出详细且有创造性的存储布局方案，写入文件 storage_plan14.txt。""",
        session=session_query14))
    print_report(result)


    result = asyncio.run(Runner.run(rw_agent, input="""你的任务是综合全部材料，产出一份统一、有创造性的内存(in-memory)存储布局方案。
        阅读以下文件：
        - 两条查询的模板：querys/q6.txt、querys/q14.txt
        - DuckDB 生成的执行计划：duckdb_plans/plan_q6.txt、duckdb_plans/plan_q14.txt
        - 表结构：duckdb_plans/schema.txt
        - 针对单条查询已有的存储方案：storage_plan06.txt、storage_plan14.txt

        两份单查询方案可能对同一张表给出不同甚至冲突的布局，你要权衡取舍：在同时服务两条查询的前提下，选择或融合出最优的设计；
        必要时可以提出两份方案都没有的新设计，鼓励非常规、新颖、甚至"疯狂"的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理

        基于以上所有材料，写出最终的统一存储布局方案，写入文件 storage_plan.txt。""",
        session=session_storage))
    print_report(result)

    # result = asyncio.run(Runner.run(rwcv_agent, input="", session=session_storage))
    # result = asyncio.run(Runner.run(rwcv_agent, input="", session=session_query06))
    # result = asyncio.run(Runner.run(rwcv_agent, input="", session=session_query14))
