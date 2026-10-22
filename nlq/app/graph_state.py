from typing import Any, TypedDict


class TextToSQLState(TypedDict):
    question: str
    sql: str
    attempts: int
    error: str | None
    columns: list[str]
    rows: list[dict[str, Any]]