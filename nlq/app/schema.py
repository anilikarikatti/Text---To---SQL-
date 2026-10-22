from sqlalchemy import inspect

from app.database import engine

# Explicitly restrict which tables the NLQ application can query.
ALLOWED_TABLES = {
    "customers",
    "products",
    "orders",
    "order_items",
}


def get_database_schema() -> str:
    inspector = inspect(engine)
    schema_parts = []

    for table_name in sorted(ALLOWED_TABLES):
        if not inspector.has_table(table_name, schema="public"):
            continue

        columns = inspector.get_columns(
            table_name,
            schema="public",
        )

        column_definitions = []

        for column in columns:
            column_definitions.append(
                f"{column['name']} {column['type']}"
            )

        schema_parts.append(
            f"Table: public.{table_name}\n"
            f"Columns: {', '.join(column_definitions)}"
        )

        foreign_keys = inspector.get_foreign_keys(
            table_name,
            schema="public",
        )

        for fk in foreign_keys:
            referred_table = fk["referred_table"]
            constrained_columns = fk["constrained_columns"]
            referred_columns = fk["referred_columns"]

            schema_parts.append(
                "Relationship: "
                f"public.{table_name}({', '.join(constrained_columns)}) "
                f"-> public.{referred_table}"
                f"({', '.join(referred_columns)})"
            )

    return "\n\n".join(schema_parts)