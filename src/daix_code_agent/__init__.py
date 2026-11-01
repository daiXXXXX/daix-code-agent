import json
import os
import subprocess
from shlex import shlex

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TOOLS = [{
    "type": "function",
    "function": {
        "name": "run_command",
        "description": "执行终端命令。argv 是参数数组，不支持管道和重定向。",
        "parameters": {
            "type": "object",
            "properties": {
                "argv": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["argv"],
            "additionalProperties": False,
        },
    },
}]

def run_command(argv: list[str]) -> str:
    if (
        not isinstance(argv, list) or
        not argv or
        not all(isinstance(item, str) for item in argv)
    ):
        return "argv invalid"

    print("\n准备执行：{shlex.join(argv)}")

    answer = input("允许执行？[y/N] ").strip().lower()

    if answer != "y" :
        raise SystemExit("已停止")

    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = {
            "exit_code": result.returncode,
            "stdout": result.stdout[:10000],
            "stderr": result.stderr[:10000],
        }

        return json.dumps(output, ensure_ascii=False)

    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"执行失败：{exc}"

def main() -> None:
    task = input("")
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_BASE_URL"],
    )
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个 Code Agent，通过终端命令完成用户任务。"
                "先查看相关文件，再修改代码；修改后运行验证。"
                "根据工具实际返回结果判断是否完成，用中文回答。"
            ),
        },
        {"role": "user", "content": task},
    ]

    for _ in range(10):
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "qwen3.5-flash"),
            messages=messages,
            tools=TOOLS
        )

        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            print(message.content)
            return

        for call in message.tool_calls:
            try:
                if call.function.name != "run_command":
                    raise ValueError("unknow tool")
                args = json.loads(call.arguments)

                # 模型返回的工具参数
                output = run_command(args["argv"])
            except (ValueError, KeyError, TypeError) as exc:
                output = f"工具参数错误：{exc}"

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": output,
            })
    raise SystemExit("达到 10 轮上限，任务尚未确认完成")