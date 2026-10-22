from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.schema import get_database_schema
from app.sql_generator import generate_sql
from app.sql_validator import validate_sql


MAX_ATTEMPTS = 3


def generate_sql_node(state: dict) -> dict:
    sql = generate_sql(
        question=state["question"],
        schema=get_database_schema(),
        previous_sql=state.get("sql") or None,
        error_message=state.get("error"),
    )

    return {
        "sql": sql,
        "attempts": state.get("attempts", 0) + 1,
        "error": None,
    }


def validate_sql_node(state: dict) -> dict:
    validated_sql = validate_sql(state["sql"])

    return {
        "sql": validated_sql,
    }


def execute_sql_node(state: dict) -> dict:
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(
                    text("SET TRANSACTION READ ONLY")
                )

                result = connection.execute(text(state["sql"]))

                return {
                    "columns": list(result.keys()),
                    "rows": [
                        dict(row)
                        for row in result.mappings().all()
                    ],
                    "error": None,
                }

    except SQLAlchemyError as exc:
        return {
            "error": str(exc)[:1500],
            "columns": [],
            "rows": [],
        }