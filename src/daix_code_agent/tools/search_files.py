import subprocess
from langchain.tools import tool

@tool
def search_files(key_words: str, directory: str = "src") -> list[str]:
    """" 根据文件内容中的关键词搜索文件，返回匹配的文件路径 """
    res = subprocess.run(
        ["grep", "-lrF","--",key_words,directory],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if res.returncode == 1:
        return []

    if res.returncode != 0:
        raise RuntimeError(res.stderr)


    return res.stdout.splitlines()