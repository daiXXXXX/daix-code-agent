import subprocess


def search_files(key_words: str, directory: str = "src") -> list[str]:
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