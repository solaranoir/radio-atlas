from typing import Any

from app.analytics.aggregation.persistence import MAX_BIND_PARAMETERS, _chunked


def _rows(count: int, columns: int) -> list[dict[str, Any]]:
    return [{f"c{column}": row for column in range(columns)} for row in range(count)]


def test_chunks_stay_within_bind_parameter_limit() -> None:
    rows = _rows(20_000, 10)

    chunks = list(_chunked(rows))

    assert all(len(chunk) * 10 <= MAX_BIND_PARAMETERS for chunk in chunks)
    assert [len(chunk) for chunk in chunks] == [6_553, 6_553, 6_553, 341]
    assert [row for chunk in chunks for row in chunk] == rows


def test_small_input_is_a_single_chunk() -> None:
    rows = _rows(3, 10)

    assert list(_chunked(rows)) == [rows]
