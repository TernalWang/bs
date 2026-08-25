import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled

from tools.shell.shell_tool import WORKSPACE
from tools.tools import compile_cpp, run_query, run_shell, write_file

# ========== 插头：client + 模型对象，不碰全局状态 ==========
load_dotenv(Path(__file__).resolve().parents[1] / ".env")  # .env 在项目根
set_tracing_disabled(True)  # 关掉往 OpenAI 传 trace
client = AsyncOpenAI(
    api_key=os.environ["GLM_API_KEY"],
    base_url="https://api.z.ai/api/coding/paas/v4/",  # 结尾的 / 不能少
)
model = OpenAIChatCompletionsModel(model="glm-5.3", openai_client=client)

# ========== 核心 2：agent = 模型 + 指令 + 工具 ==========
rwcv_agent = Agent(
    name="demo_queryagent",
    model=model,
    instructions=f"你在 {WORKSPACE} 下工作，run_shell 可以看文件、跑 infra/build/db 等，write_file 可以写文件，compile_cpp 可以把infra编译成db这个binary，run_query可以返回查询的标准答案和延迟的baseline，拿你 db 的输出与它对比验证。",
    tools=[run_shell, write_file, compile_cpp, run_query],
)

rw_agent = Agent(
    name="demo_storageagent",
    model=model,
    instructions=f"你在 {WORKSPACE} 下工作，用 run_shell 看文件, 用 write_file 写文件。",
    tools=[run_shell, write_file],
)


def print_report(result):
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