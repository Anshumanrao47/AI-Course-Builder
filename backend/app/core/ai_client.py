"""
Thin wrapper around the OpenAI API for structured JSON generation.

Every agent asks this module for a Pydantic model back, never raw text.
`call_structured` handles: prompting the model to return JSON only,
parsing the response, validating it against the given Pydantic model, and
retrying once on a validation failure (LLMs occasionally return
almost-valid JSON — a single retry with the error appended to the prompt
fixes the large majority of these without masking real failures).

If `USE_MOCK_AI` is on (or no API key is configured), `mock_fn` is used
instead of calling the network at all. Every agent supplies a mock so the
whole pipeline — assessment, planning, content, quizzes, evaluation,
adaptation — can be exercised end-to-end offline.
"""
import json
import logging
from typing import Callable, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.config import settings

logger = logging.getLogger("ai_client")

T = TypeVar("T", bound=BaseModel)


class AIGenerationError(Exception):
    """Raised when the AI provider fails or returns data that can't be validated."""


def _use_mock() -> bool:
    return settings.USE_MOCK_AI or not settings.OPENAI_API_KEY


def _client():
    from openai import OpenAI

    return OpenAI(api_key=settings.OPENAI_API_KEY)


def call_structured(
    *,
    system_prompt: str,
    user_prompt: str,
    response_model: type[T],
    mock_fn: Callable[[], T],
) -> T:
    """
    Call the model and return an instance of `response_model`, or raise
    AIGenerationError. Falls back to `mock_fn()` in mock mode.
    """
    if _use_mock():
        return mock_fn()

    schema_hint = json.dumps(response_model.model_json_schema(), indent=2)
    full_system_prompt = (
        f"{system_prompt}\n\n"
        "Respond with ONLY a JSON object matching this schema. "
        "No prose, no markdown fences.\n"
        f"{schema_hint}"
    )

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            client = _client()
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt if attempt == 0 else
                        f"{user_prompt}\n\nYour previous response failed validation: {last_error}. "
                        "Return corrected JSON only."},
                ],
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
            return response_model.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            logger.warning("AI response failed validation (attempt %d): %s", attempt + 1, e)
            continue
        except Exception as e:  # network / API errors — don't retry those
            logger.error("AI provider call failed: %s", e)
            raise AIGenerationError(f"AI provider call failed: {e}") from e

    raise AIGenerationError(f"AI response failed validation after retry: {last_error}")
