import json
import shlex
import subprocess
from langchain.tools import tool

@tool
def run_command(argv: list[str]) -> str:
    """执行终端命令。argv 是参数数组，不支持管道和重定向。"""
    if (
        not isinstance(argv, list) or
        not argv or
        not all(isinstance(item, str) for item in argv)
    ):
        return "argv invalid"

    print(f"\n准备执行：{shlex.join(argv)}")

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