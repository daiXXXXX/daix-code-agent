import os

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

from daix_code_agent.tools.search_files import search_files
from daix_code_agent.tools.run_command import run_command

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # 显示 INFO 及以上级别的日志
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

run_config: RunnableConfig | None = {
    "max_concurrency": 1,
    "recursion_limit": 100,
}

logger = logging.getLogger("init")

def main() -> None:
    client = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "qwen3.5-flash"),
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_BASE_URL"],
        use_responses_api=False
    )

    agent = create_agent(
        model=client,
        tools=[run_command, search_files],
        system_prompt=(
            "你是一个 Code Agent，通过工具完成用户任务。"
            "先查看相关文件，再修改代码；修改后运行验证。"
            "根据工具实际返回结果判断是否完成，用中文回答。"
        ),
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=10,
                exit_behavior="end"
            )
        ]
    )

    task = input("请输入：")

    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": task}]
        },
        config={
            "max_concurrency": 1,
            "recursion_limit": 100,
        },
    )

    # 流式输出
    # for chunk, update in agent.stream(
    #     {"messages": [{"role": "user", "content": task}]},
    #     config = run_config,
    #     stream_mode="messages",
    # ):
    #     print(chunk.text, end = "", flush=True)
        # for step, item in update.items():
        #     if not isinstance(item, dict):
        #         continue
        #
        #     for message in item.get("messages", []):
        #         print(f"----{step}---")
        #         message.pretty_print()

    print(result["messages"][-1].text)