import ctypes
import os
import subprocess
import sys
from pathlib import Path

# 焊死在这里：全项目唯一的 WORKSPACE 定义，tools/write/agent/main/sessions 都从这里 import
# 本文件在 bs/tools/shell/ 下，往上两层才是项目根
WORKSPACE = Path(__file__).resolve().parents[2] / "workspace"

# ========== Landlock：内核级文件系统沙箱 ==========
# 本机 AppArmor 限制了非特权 user namespace（apparmor_restrict_unprivileged_userns=1），
# systemd-run/bwrap 那类 mount namespace 方案全部静默失效；Landlock 是内核 LSM，
# 不需要特权，限制一旦生效不可解除，子进程全部继承。
# 语义：白名单之外一律不可见。系统目录(/usr /etc /proc /dev)只读可执行，
# 供 bash/gcc/python 正常工作；WORKSPACE 和 /tmp 读写全开；项目其他目录摸不到。
# /dev/null 单独给写权限（bash 重定向刚需，目录权限加在文件上内核会 EINVAL）。
_FS = {
    "EXECUTE": 1 << 0, "WRITE_FILE": 1 << 1, "READ_FILE": 1 << 2, "READ_DIR": 1 << 3,
    "REMOVE_DIR": 1 << 4, "REMOVE_FILE": 1 << 5, "MAKE_CHAR": 1 << 6, "MAKE_DIR": 1 << 7,
    "MAKE_REG": 1 << 8, "MAKE_SOCK": 1 << 9, "MAKE_FIFO": 1 << 10, "MAKE_BLOCK": 1 << 11,
    "MAKE_SYM": 1 << 12, "REFER": 1 << 13, "TRUNCATE": 1 << 14,
}
_SYS_CREATE, _SYS_ADD, _SYS_RESTRICT = 444, 445, 446  # x86_64 syscall 号
_PR_SET_NO_NEW_PRIVS = 38


class _RulesetAttr(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]


class _PathBeneathAttr(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]


def _apply_landlock() -> None:
    """生效后，本进程及其所有后代只能写 WORKSPACE 和 /tmp。失败即抛异常，绝不无沙箱执行。"""
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long

    def sc(nr, *args):
        rc = libc.syscall(ctypes.c_long(nr), *args)
        if rc == -1:
            raise OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
        return rc

    abi = sc(_SYS_CREATE, ctypes.c_void_p(None), ctypes.c_size_t(0), ctypes.c_uint(1))
    if abi < 1:
        raise RuntimeError("内核不支持 Landlock，拒绝无沙箱执行")
    v1 = ["EXECUTE", "WRITE_FILE", "READ_FILE", "READ_DIR", "REMOVE_DIR", "REMOVE_FILE",
          "MAKE_CHAR", "MAKE_DIR", "MAKE_REG", "MAKE_SOCK", "MAKE_FIFO", "MAKE_BLOCK", "MAKE_SYM"]
    keys = v1 + (["REFER"] if abi >= 2 else []) + (["TRUNCATE"] if abi >= 3 else [])
    handled = 0
    for k in keys:
        handled |= _FS[k]
    rs = sc(_SYS_CREATE, ctypes.byref(_RulesetAttr(handled)),
            ctypes.c_size_t(ctypes.sizeof(_RulesetAttr)), ctypes.c_uint(0))
    ro = _FS["EXECUTE"] | _FS["READ_FILE"] | _FS["READ_DIR"]
    file_rw = _FS["READ_FILE"] | _FS["WRITE_FILE"] | _FS["TRUNCATE"]
    rules = [
        ("/usr", ro), ("/etc", ro), ("/proc", ro), ("/dev", ro),
        (WORKSPACE, handled), ("/tmp", handled),
        ("/dev/null", file_rw),
    ]
    for path, allowed in rules:
        fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
        try:
            sc(_SYS_ADD, ctypes.c_long(rs), ctypes.c_long(1),
               ctypes.byref(_PathBeneathAttr(allowed, fd)), ctypes.c_uint(0))
        finally:
            os.close(fd)
    if libc.prctl(_PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_NO_NEW_PRIVS) 失败")
    sc(_SYS_RESTRICT, ctypes.c_long(rs), ctypes.c_void_p(None))


if __name__ == "__main__" and sys.argv[1:2] == ["--exec"]:
    # helper 进程入口：先套上 Landlock 再 exec bash，之后 bash 及其所有后代都出不去。
    # 不用 preexec_fn：agent 框架在线程里调工具，多进程 fork 后跑 ctypes 有死锁风险。
    _apply_landlock()
    os.execvp("bash", ["bash", "-c", sys.argv[2]])


def run_shell(command: str) -> str:
    print(f"[tool] run_shell: {command}")
    p = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--exec", command],
        cwd=WORKSPACE, capture_output=True, text=True, timeout=120,
    )
    return p.stdout + p.stderr
