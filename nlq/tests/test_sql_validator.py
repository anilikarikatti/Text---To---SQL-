import pytest

from app.sql_validator import validate_sql, UnsafeQueryError


def test_select_query_is_accepted():
    sql = validate_sql(
        "SELECT name FROM products"
    )

    assert "LIMIT 100" in sql


def test_update_is_rejected():
    with pytest.raises(UnsafeQueryError):
        validate_sql(
            "UPDATE products SET name = 'Changed'"
        )


def test_delete_is_rejected():
    with pytest.raises(UnsafeQueryError):
        validate_sql(
            "DELETE FROM products"
        )


def test_multiple_statements_are_rejected():
    with pytest.raises(UnsafeQueryError):
        validate_sql(
            "SELECT * FROM products; DELETE FROM products"
        )


def test_invalid_sql_is_rejected():
    with pytest.raises(UnsafeQueryError):
        validate_sql(
            "SELECT FROM WHERE"
        )