from tools.shell.shell_tool import run_shell


def compile_cpp() -> str:
    return run_shell("bash infra/build.sh")
