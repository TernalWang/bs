from pathlib import Path

from tools.shell.shell_tool import WORKSPACE


def write_file(path: str, content: str) -> str:
    print(f"[tool] write_file: {path}（{len(content)} 字符）")
    target = (WORKSPACE / path).resolve()  # 绝对路径会顶掉前缀，.. 和软链被摊平
    if not (target.is_relative_to(WORKSPACE) or target.is_relative_to(Path("/tmp"))):
        return f"拒绝写入 {target}：只允许 workspace 和 /tmp"
    target.write_text(content)
    return "ok"
