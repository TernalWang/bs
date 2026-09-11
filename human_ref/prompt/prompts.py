from tools.shell.shell_tool import WORKSPACE

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
        "DECIMAL舍入只许一次除非万不得已"
        "数据量会增长到当前的1000倍：规模相关的模块和参数（行数、基数、分区数、字典容量等）不要写死，从实际数据推导（哪些量恒定、哪些随规模增长见 duckdb_plans/scale_stats.txt）。"
        "run_shell 可以看文件、跑 infra/build/db、"
        "小修改（替换字符串、改几行代码、勾选 TODO）用 sed/awk 完成。"
        "write_file 可以写文件。"
        "compile_cpp 可以把infra编译成db这个binary。"
        "run_query可以返回查询的标准答案和延迟的baseline"
        "拿你 db 的输出与它对比验证。"
        "验证完以后再检查一遍自己的代码"
    )

def storage_plan_prompt(n: int) -> str:
    return f"""你的任务是分析给定的查询负载，为其中访问到的每张表设计一份有创造性的内存(in-memory)存储布局方案。
        你可以输出详细的自由格式文本，不仅探讨常规存储布局建议，也探讨非常规、新颖、甚至"疯狂"的存储设计。
        鼓励你加入额外的想法：投机式的编码技术、实验性的列分组与数据组织方式。
        对每张被访问的表，大胆展开：混合布局、SoA/AoS(数组结构/结构数组)的各种变体、新颖的列编码等。
        把这次当作突破现有规范的机会，提出未来感的、甚至离经叛道的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 执行模型为两段式：每条查询先在每个分区上并行执行，各分区分别产出一个中间结果，再把全部分区的中间结果合并得到该查询的最终结果
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理
        - 数据以固定分区文件形式提供（当前 10 个分片）：所有分区同构、共用同一套存储布局，每个分区以 Arrow Table 输入、独立构建为一个 Database 对象，方案只需描述单个分区内部的布局；跨分区的并行调度由框架负责
        - 分区数会从当前的 10 个增长到上百甚至上千个，行数、基数、字典容量等规模参数同样会变：你能看到的只是当前规模，请直接按上千分区的规模来设计存储布局，不要以当前 10 个分区为假设，任何当前观察到的数字都不要写死
        - 原始数据本身不保序并且随着数据增长更不保序
        - 不要去读任何其他的文件
        - 本阶段唯一允许写的文件是 storage_plan{n}.txt，不得创建或修改任何其他文件

        查询负载见文件：querys/q{n}.txt。
        DuckDB 对该查询生成的执行计划见文件：duckdb_plans/plan_q{n}.txt。
        表结构见文件：duckdb_plans/schema.txt。
        框架骨架见文件：infra/db.cpp（load → 每分区 build → 查询执行的主流程）与 infra/query/query_impl.cpp（两段式执行与调度机器）。

        基于以上查询、执行计划和表结构，为被访问的表给出详细且有创造性的存储布局方案，写入文件 storage_plan{n}.txt。"""

def overall_storage_prompt(queries: list[int]) -> str:
    return f"""你的任务是综合全部材料，产出一份统一、有创造性的内存(in-memory)存储布局方案。
        阅读以下文件：
        - 各查询的模板：{"、".join(f"querys/q{x}.txt" for x in queries)}
        - DuckDB 生成的执行计划：{"、".join(f"duckdb_plans/plan_q{x}.txt" for x in queries)}
        - 表结构：duckdb_plans/schema.txt
        - 框架骨架：infra/db.cpp（load → 每分区 build → 查询执行的主流程）与 infra/query/query_impl.cpp（两段式执行与调度机器）
        - 针对单条查询已有的存储方案：{"、".join(f"storage_plan{x}.txt" for x in queries)}

        各单查询方案可能对同一张表给出不同甚至冲突的布局，你要权衡取舍：在同时服务全部查询的前提下，选择或融合出最优的设计；
        必要时可以提出各方案都没有的新设计，鼓励非常规、新颖、甚至"疯狂"的存储技术。
        输出每张表的存储布局。只输出最终的存储布局。

        重要约束：
        - 执行模型为两段式：每条查询先在每个分区上并行执行，各分区分别产出一个中间结果，再把全部分区的中间结果合并得到该查询的最终结果
        - 必须存储全部数据，且存储方式要能无损还原(flatten)回原始数据
        - 不允许冗余存储同一份数据，但可以使用压缩、编码、元数据或特殊数据结构
        - 优化目标：单节点内存分析型查询处理
        - 数据以固定分区文件形式提供（当前 10 个分片）：所有分区同构、共用同一套存储布局，每个分区以 Arrow Table 输入、独立构建为一个 Database 对象，方案只需描述单个分区内部的布局；跨分区的并行调度由框架负责
        - 分区数会从当前的 10 个增长到上百甚至上千个，行数、基数、字典容量等规模参数同样会变：你能看到的只是当前规模，请直接按上千分区的规模来设计存储布局，不要以当前 10 个分区为假设，任何当前观察到的数字都不要写死
        - 原始数据本身不保序并且随着数据增长更不保序
        - 不要去读任何其他的文件
        - 本阶段唯一允许写的文件是 storage_plan.txt，不得创建或修改任何其他文件

        基于以上所有材料，写出最终的统一存储布局方案，写入文件 storage_plan.txt。"""

def todo_prompt(queries: list[int]) -> str:
    query_todos = "\n        ".join(f"- TODO_query{x}.md：Q{x} 执行阶段（query_impl.cpp）。验收：能编译，且用 run_query 多组参数取得标准答案和延迟 baseline，与自己引擎的输出对比一致，并记录性能对比。" for x in queries)
    return f"""你是一名资深的数据库工程师和熟练的程序员。
        用 C++ 编写一个专用的高性能数据库引擎，只针对一组预定义的查询做优化。
        该引擎需要执行 {"、".join(f"querys/q{x}.txt" for x in queries)} 中描述的 SQL 查询（共 {len(queries)} 条！！）。
        数据类型和运算符可以硬编码进程序，以避免解释执行的开销。

        首先，在文件 `infra/include/builder_impl.hpp`/`infra/builder/builder_impl.cpp` 中，把表从 ArrowTable (原始数据本身不保徐并且随着数据增长更不保序) 转换为自定义的数据结构（构建阶段）。
        把它存储为一个 Database 结构体对象（预定义在 `infra/include/builder_impl.hpp`/`infra/builder/builder_impl.cpp` 中）。
        使用高效的内存数据表示，让查询能够快速执行。存储方案写在文件 `storage_plan.txt` 里，它描述了如何把 parquet 数据存入内存以获得最优的查询执行性能。请按照这份存储方案来实现内存数据结构。

        然后在这个数据结构上执行查询（执行阶段）。执行逻辑的接口已经预定义在 `infra/query/query_impl.cpp` 中。
        查询接口作用于一个 QueryRequest 列表，每个请求对应一条要执行的查询。
        每条查询的格式为：`<查询号> <查询参数>`（例如查询 Q42 带参数 "EUROPE" 和 "1995-01-01" 时："42 EUROPE 1995-01-01"）含空格的值必须加双引号（如 "REG AIR"）。
        解析查询号和参数时，使用 `infra/include/args_parser.hpp` 中定义的 header-only C++ 解析器。
        数据库引擎应按顺序执行参数列表中指定的所有查询。

        把每条查询的输出写入单独的 csv 文件。
        命名为 `result<RUN_NR>.csv`，其中 `<RUN_NR>` 是该查询在参数列表中的位置（从 1 开始计数）。
        CSV 参数：(delimiter=',', quotechar='"', escapechar='\\\\', header=True, quoting=QUOTE_MINIMAL, doublequote=True)，
        即：仅当字段含逗号/引号/换行时才用引号包裹；字段内的引号写成两个（""）；字段内的反斜杠写成 \\\\。与run_query标准答案CSV完全同格式。

        表结构见文件 duckdb_plans/schema.txt。
        数据规模增长统计见文件 duckdb_plans/scale_stats.txt。(数据量会增长到当前的1000倍 这个相关的应该告知所有TODO)

        请为实现这个数据库引擎制定 TODO 计划，包含各个步骤，并附上数据结构等方面的概念性注释。
        我之后会按顺序用不同的 agent 逐个执行，共 {len(queries) + 1} 个 agent（1 个构建阶段 + {len(queries)} 个查询阶段），所以把计划拆成对应的 {len(queries) + 1} 个文件：
        - TODO_storage.md：构建阶段（builder_impl.hpp / builder_impl.cpp）。验收：实现后 compile_cpp 编译通过即可。
        {query_todos}
        以上文件即执行顺序；每个文件里的步骤完成后逐项标记。现在先不要开始实现，也先不要执行这些步骤。"""

STORAGE_CODE_INPUT = "开始完成storage layer"

def query_code_input(n: int) -> str:
    return f"开始完成query {n}"

# ====== args_parser ======

ARGS_PARSER_READ = """    if (!(iss >> std::quoted(args.%(k)s))) {
        throw std::runtime_error("Q%(n)s: failed to parse %(k)s");
    }
"""

ARGS_PARSER_QUERY = """//Q%(n)s
struct Q%(n)sArgs {
%(fields)s};
inline Q%(n)sArgs parse_q%(n)s(const QueryRequest& request) {
    Q%(n)sArgs args;
    std::istringstream iss(request.line);

    std::string qid;
    if (!(iss >> qid)) {  // consume query id
        throw std::runtime_error("Q%(n)s: failed to parse query id");
    }

%(reads)s    return args;
}"""

# ====== loader ======

LOADER_FIELD = """    ArrowTable %(table)s;
"""

LOADER_DECL = """    auto tables = std::vector<ParquetTables>(%(count)d);
"""

LOADER_LOAD = """    tables[%(i)d].%(table)s = ReadParquetTable(path + "%(stem)s.parquet");
"""

# ====== builder ======

BUILDER_BUILD = """    std::vector<Database*> dbs(%(count)d);

    #pragma omp parallel for schedule(dynamic) num_threads(50)
    for (int i = 0; i < %(count)d; ++i) dbs[i] = build(&tables[i]);

    std::vector<QueryRequest> requests = read_requests();

    results(dbs, requests);
"""

# ====== query ======

QUERY_CASE = """                case %(n)2d: run_query(%(n)d, dbs, parse_q%(n)d(request), run_nr, mid_q%(n)d, final_q%(n)d); break;"""

# ====== qN ======

QIMPL = """#include "query_impl.hpp"


struct Q%(n)dMid {
    // TODO: Data structures to hold the intermediate results of one partition
};

inline Q%(n)dMid* mid_q%(n)d(Database*, const Q%(n)dArgs&) {
    // TODO: implement the per-partition execution logic for Q%(n)d
    return new Q%(n)dMid{};
}

inline void final_q%(n)d(std::vector<Q%(n)dMid*>&, const Q%(n)dArgs&, int run_nr) {
    // TODO: produce the final result from all midresults and write result<run_nr>.csv
}
"""
