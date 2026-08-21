from agents import SQLiteSession

from tools.shell.shell_tool import WORKSPACE

SESSION_PATH = WORKSPACE / "sessions.db"


def make_session(conv_id: str) -> SQLiteSession:
    return SQLiteSession(conv_id, db_path=SESSION_PATH)
