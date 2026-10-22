import sqlglot
from sqlglot import exp

from app.schema import ALLOWED_TABLES


class UnsafeQueryError(ValueError):
    pass


def validate_sql(sql: str) -> str:
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except Exception as exc:
        raise UnsafeQueryError("Generated SQL is invalid.") from exc

    if len(statements) != 1 or statements[0] is None:
        raise UnsafeQueryError("Only one SQL statement is allowed.")

    expression = statements[0]

    if not isinstance(expression, exp.Select):
        raise UnsafeQueryError("Only SELECT queries are allowed.")

    if expression.args.get("into") or expression.args.get("locks"):
        raise UnsafeQueryError(
            "SELECT INTO and locking queries are not allowed."
        )

    # Check every referenced table against our allowlist.
    for table in expression.find_all(exp.Table):
        if table.db and table.db != "public":
            raise UnsafeQueryError("Schema is not allowed.")

        if table.name not in ALLOWED_TABLES:
            raise UnsafeQueryError("Table is not allowed.")

    # Wrap the query to impose a maximum returned row count.
    return (
        "SELECT * FROM ("
        + expression.sql(dialect="postgres")
        + ") AS nlq_result LIMIT 100"
    )