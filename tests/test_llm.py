from unittest.mock import patch, Mock

import pytest

from backend.llm import generate_response


def test_empty_message():
    """Test that an empty message is rejected."""

    with pytest.raises(ValueError, match="Message cannot be empty."):
        generate_response("")


def test_whitespace_message():
    """Test that whitespace-only messages are rejected."""

    with pytest.raises(ValueError, match="Message cannot be empty."):
        generate_response("   ")


def test_successful_response():
    """Test that a valid Gemini response is returned."""

    mock_interaction = Mock()
    mock_interaction.output_text = "Artificial Intelligence is the ability of machines to perform intelligent tasks."

    with patch(
        "backend.llm.client.interactions.create",
        return_value=mock_interaction
    ):
        response = generate_response(
            "Explain artificial intelligence in simple terms."
        )

    assert response == (
        "Artificial Intelligence is the ability of machines "
        "to perform intelligent tasks."
    )

def test_quota_error():
    """Test graceful handling of Gemini quota errors."""

    from google.genai.errors import APIError

    mock_error = APIError(
        429,
        {"error": {"message": "Quota exceeded"}}
    )

    with patch(
        "backend.llm.client.interactions.create",
        side_effect=mock_error
    ):
        response = generate_response(
            "Explain artificial intelligence."
        )

    assert "quota has been exceeded" in response.lower()