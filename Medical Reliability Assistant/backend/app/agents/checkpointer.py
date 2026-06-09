"""
app/agents/checkpointer.py
LangGraph checkpointing with SQLite backend.
Allows mid-workflow resumption (e.g., after human-in-the-loop pause).
"""
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.core.config import get_settings

settings = get_settings()

_checkpointer: AsyncSqliteSaver = None


async def get_checkpointer() -> AsyncSqliteSaver:
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = AsyncSqliteSaver.from_conn_string(settings.checkpoint_db_path)
    return _checkpointer
