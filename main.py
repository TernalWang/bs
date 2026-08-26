import asyncio
import json
import shutil
from pathlib import Path
from agents import Runner

from agent.agent import make_rw_agent, make_rwcv_agent, print_report
from sessions.sessions import make_session
from tools.shell.shell_tool import WORKSPACE
from tools.verify.duckdb_tool import run_query_json, dump_schema, start as start_duckdb

INFRA = Path(__file__).parent / "infra"
TPCH_SF1 = Path(__file__).parent / "tpch_parquet" / "sf1"
TPCH_QUERY = Path(__file__).parent / "tpch_query"
HUMAN_INPUT = Path(__file__).parent / "human_ref" / "input"

RW_INSTRUCTIONS = f"你在 {WORKSPACE} 下工作，用 run_shell 看文件, 用 write_file 写文件。"
RWCV_INSTRUCTIONS = (
    f"你在 {WORKSPACE} 下工作，"
    "run_shell 可以看文件、跑 infra/build/db 等，"
    "write_file 可以写文件，"
    "compile_cpp 可以把infra编译成db这个binary，"
    "run_query可以返回查询的标准答案和延迟的baseline，拿你 db 的输出与它对比验证。"
)

def todo_instructions(todo_file: str) -> str:
    return (
        f"你在 {WORKSPACE} 下按照{todo_file}完成工作"
        "每完成一项就在文件中✅标记一下别的TODO.md和你无关！。"
        "run_shell 可以看文件、跑 infra/build/db、"
        "小修改（替换字符串、改几行代码、勾选 TODO）用 sed/awk 完成。"
        "write_file 可以写文件。"
        "compile_cpp 可以把infra编译成db这个binary。"
        "run_query可以返回查询的标准答案和延迟的baseline"
        "拿你 db 的输出与它对比验证。"
    )


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

    print("Generate duckdb plans into workspace")
    (WORKSPACE / "duckdb_plans").mkdir()
    for n in range(1, 23):
        (WORKSPACE / "duckdb_plans" / f"plan_q{n}.txt").write_text(json.dumps(run_query_json((HUMAN_INPUT / f"q{n}.txt").read_text().strip())[3], indent=2))

    print("Generate schema into workspace")
    (WORKSPACE / "duckdb_plans" / "schema.txt").write_text(dump_schema())

    print("Generate query 06 storage plan")
    result = asyncio.run(Runner.run(make_rw_agent(RW_INSTRUCTIONS), input="""你的任务是分析给定的查询负载，为其中访问到的每张表设计一份有创造性的内存(in-memory)存储布局方案。
        你可以输出详细的自由格式文本，不仅探讨常规存储布局建议，也探讨非常规、新颖、甚至"疯狂"的存储设计。
        鼓励你加入额外的想法：新的分区策略、投机式的编码技术、实验性的列分组与数据组织方式。
        对每张被访问的表，大胆展开：混合布局、SoA/AoS(数组结构/结构数组)的各种变体、新颖的列编码、自适应分区等。
        把这次当作突破现有规范的机会，提出未来感的、甚至离经叛道的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理
        - 不要去读任何其他的文件

        查询负载见文件：querys/q6.txt。
        DuckDB 对该查询生成的执行计划见文件：duckdb_plans/plan_q6.txt。
        表结构见文件：duckdb_plans/schema.txt。

        基于以上查询、执行计划和表结构，为被访问的表给出详细且有创造性的存储布局方案，写入文件 storage_plan06.txt。""",
        session=make_session("plan_q6"), max_turns=75))
    print_report(result)

    print("Generate query 14 storage plan")
    result = asyncio.run(Runner.run(make_rw_agent(RW_INSTRUCTIONS), input="""你的任务是分析给定的查询负载，为其中访问到的每张表设计一份有创造性的内存(in-memory)存储布局方案。
        你可以输出详细的自由格式文本，不仅探讨常规存储布局建议，也探讨非常规、新颖、甚至"疯狂"的存储设计。
        鼓励你加入额外的想法：新的分区策略、投机式的编码技术、实验性的列分组与数据组织方式。
        对每张被访问的表，大胆展开：混合布局、SoA/AoS(数组结构/结构数组)的各种变体、新颖的列编码、自适应分区等。
        把这次当作突破现有规范的机会，提出未来感的、甚至离经叛道的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理
        - 不要去读任何其他的文件

        查询负载见文件：querys/q14.txt。
        DuckDB 对该查询生成的执行计划见文件：duckdb_plans/plan_q14.txt。
        表结构见文件：duckdb_plans/schema.txt。

        基于以上查询、执行计划和表结构，为被访问的表给出详细且有创造性的存储布局方案，写入文件 storage_plan14.txt。""",
        session=make_session("plan_q14"), max_turns=75))
    print_report(result)

    print("Generate overall storage plan")
    result = asyncio.run(Runner.run(make_rw_agent(RW_INSTRUCTIONS), input="""你的任务是综合全部材料，产出一份统一、有创造性的内存(in-memory)存储布局方案。
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
        - 不要去读任何其他的文件

        基于以上所有材料，写出最终的统一存储布局方案，写入文件 storage_plan.txt。""",
        session=make_session("storage"), max_turns=75))
    print_report(result)

    print("Delete seprate storage plan")
    (WORKSPACE / "storage_plan06.txt").unlink(missing_ok=True)
    (WORKSPACE / "storage_plan14.txt").unlink(missing_ok=True)

    print("Generate TODO based on overall storage plan")
    result = asyncio.run(Runner.run(make_rwcv_agent(RWCV_INSTRUCTIONS), input="""你是一名资深的数据库工程师和熟练的程序员。
        用 C++ 编写一个专用的高性能数据库引擎，只针对一组预定义的查询做优化。
        该引擎需要执行 querys/q6.txt 和 querys/q14.txt 中描述的 SQL 查询（共 2 条！！）。
        数据类型和运算符可以硬编码进程序，以避免解释执行的开销。

        首先，在文件 `infra/include/builder_impl.hpp`/`infra/builder/builder_impl.cpp` 中，把表从 ArrowTable 转换为自定义的数据结构（构建阶段）。
        把它存储为一个 Database 结构体对象（预定义在 `infra/include/builder_impl.hpp`/`infra/builder/builder_impl.cpp` 中）。
        使用高效的内存数据表示，让查询能够快速执行。存储方案写在文件 `storage_plan.txt` 里，它描述了如何把 parquet 数据存入内存以获得最优的查询执行性能。请按照这份存储方案来实现内存数据结构。

        然后在这个数据结构上执行查询（执行阶段）。执行逻辑的接口已经预定义在 `infra/query/query_impl.cpp` 中。
        查询接口作用于一个 QueryRequest 列表，每个请求对应一条要执行的查询。
        每条查询的格式为：`<查询号> <查询参数>`（例如查询 Q42 带参数 "EUROPE" 和 "1995-01-01" 时："42 EUROPE 1995-01-01"）含空格的值必须加双引号（如 "REG AIR"）。
        解析查询号和参数时，使用 `infra/include/args_parser.hpp` 中定义的 header-only C++ 解析器。
        数据库引擎应按顺序执行参数列表中指定的所有查询。

        把每条查询的输出写入单独的 csv 文件。
        命名为 `result<RUN_NR>.csv`，其中 `<RUN_NR>` 是该查询在参数列表中的位置（从 1 开始计数）。
        CSV 参数：(delimiter=',', escapechar='\\\\', quotechar='"', header=True)。

        表结构见文件 duckdb_plans/schema.txt。

        请为实现这个数据库引擎制定 TODO 计划，包含各个步骤，并附上数据结构等方面的概念性注释。
        我之后会用三个 agent 按顺序执行，所以把计划拆成三个文件：
        - TODO_storage.md：构建阶段（builder_impl.hpp / builder_impl.cpp）。验收：实现后 compile_cpp 编译通过即可。
        - TODO_query06.md：Q6 执行阶段（query_impl.cpp）。验收：能编译，且用 run_query 多组参数取得标准答案和延迟 baseline，与自己引擎的输出对比一致，并记录性能对比。
        - TODO_query14.md：Q14 执行阶段（query_impl.cpp），验收标准同 Q6。
        三个文件即执行顺序；每个文件里的步骤完成后逐项标记。现在先不要开始实现，也先不要执行这些步骤。""",
        session=make_session("storage_todo"), max_turns=100))
    print_report(result)

    print("start coding")
    result = asyncio.run(Runner.run(
        make_rwcv_agent(todo_instructions("TODO_storage.md")),
        input="开始完成storage layer",
        session=make_session("code_storage"),
        max_turns=700,
    ))
    print_report(result)
    result = asyncio.run(Runner.run(
        make_rwcv_agent(todo_instructions("TODO_query06.md")),
        input="开始完成query 6",
        session=make_session("code_q6"),
        max_turns=700,
    ))
    print_report(result)
    result = asyncio.run(Runner.run(
        make_rwcv_agent(todo_instructions("TODO_query14.md")),
        input="开始完成query 14",
        session=make_session("code_q14"),
        max_turns=700,
    ))
    print_report(result)
