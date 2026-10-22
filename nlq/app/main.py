# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from sqlalchemy import text
# from sqlalchemy.exc import SQLAlchemyError
# from fastapi.encoders import jsonable_encoder

# from app.database import engine
# from app.sql_generator import generate_sql
# from app.sql_validator import validate_sql, UnsafeQueryError


# from app.schema import get_database_schema

# MAX_ATTEMPTS = 3

# app = FastAPI(title="NLQ Text-to-SQL API")


# class NLQRequest(BaseModel):
#     question: str = Field(min_length=3, max_length=1000)


# @app.get("/health")
# def health():
#     return {"status": "ok"}




# @app.post("/query")
# def query_database(request: NLQRequest):
#     schema = get_database_schema()

#     previous_sql = None
#     error_message = None

#     for attempt in range(MAX_ATTEMPTS):
#         try:
#             # Generate or correct SQL.
#             generated_sql = generate_sql(
#                 question=request.question,
#                 schema=schema,
#                 previous_sql=previous_sql,
#                 error_message=error_message,
#             )

#             # Reject unsafe SQL immediately.
#             safe_sql = validate_sql(generated_sql)

#             # Execute in a fresh read-only transaction.
#             with engine.connect() as connection:
#                 with connection.begin():
#                     connection.exec_driver_sql(
#                         "SET TRANSACTION READ ONLY"
#                     )

#                     result = connection.execute(text(safe_sql))

#                     columns = list(result.keys())
#                     rows = [
#                         dict(row)
#                         for row in result.mappings().all()
#                     ]

#             return jsonable_encoder({
#                 "question": request.question,
#                 "sql": generated_sql,
#                 "columns": columns,
#                 "rows": rows,
#                 "row_count": len(rows),
#                 "attempts": attempt + 1,
#             })

#         except UnsafeQueryError as exc:
#             # Do not keep retrying prohibited queries.
#             raise HTTPException(
#                 status_code=400,
#                 detail="Generated SQL failed the safety checks.",
#             ) from exc

#         except SQLAlchemyError as exc:
#             # Internal correction context only; never return raw
#             # database errors or credentials to the API client.
#             previous_sql = generated_sql
#             error_message = str(exc.orig)[:1500]

#             if attempt == MAX_ATTEMPTS - 1:
#                 raise HTTPException(
#                     status_code=422,
#                     detail="Unable to generate an executable query.",
#                 ) from exc

#         except Exception as exc:
#             # Unexpected failures are not automatically retried.
#             raise HTTPException(
#                 status_code=502,
#                 detail="The NLQ service encountered an error.",
#             ) from exc   




# 2 nd version with langgraph 


from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.graph import text_to_sql_graph


app = FastAPI(title="Text-to-SQL API")


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
        description="Question about the database",
    )


class QueryResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    attempts: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    initial_state = {
        "question": request.question,
        "sql": "",
        "attempts": 0,
        "error": None,
        "columns": [],
        "rows": [],
    }

    try:
        result = text_to_sql_graph.invoke(initial_state)

        if result.get("error"):
            # Do not expose raw database errors to API clients.
            raise HTTPException(
                status_code=422,
                detail="The query could not be completed. "
                       "Please rephrase the question or try again.",
            )

        return QueryResponse(
            question=request.question,
            sql=result["sql"],
            columns=result["columns"],
            rows=result["rows"],
            row_count=len(result["rows"]),
            attempts=result["attempts"],
        )

    except HTTPException:
        raise

    except Exception:
        # Log the full exception securely on the server in a real app.
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the query.",
        )
