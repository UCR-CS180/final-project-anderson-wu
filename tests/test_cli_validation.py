import pytest

from interface.cli import validate_situation_text


def test_empty_input_fails() -> None:
    with pytest.raises(ValueError):
        validate_situation_text("   ")


def test_too_short_input_fails() -> None:
    with pytest.raises(ValueError):
        validate_situation_text("Too short")


def test_valid_input_passes() -> None:
    text = "My partner and I keep arguing about plans and I feel ignored."
    assert validate_situation_text(text) == text
