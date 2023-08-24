"""Settings for the anonymization verification application."""
import functools
import pathlib

import pydantic

JSON_DATA_DIR = pathlib.Path(__file__).parent / "jsons"


class Settings(pydantic.BaseModel):
    """
    A Pydantic model representing the settings for the anonymization verification application.

    """

    logger_name: str = pydantic.Field(
        "anonymization_verification",
        json_schema_extra={
            "env": "LOGGER_NAME",
            "description": "The name of the logger to use.",
        },
    )

    spacy_model: str = pydantic.Field(
        "en_core_web_trf",
        json_schema_extra={
            "env": "SPACY_MODEL",
            "description": "The name of the spaCy model to use for named entity recognition.",
        },
    )

    disallowed_words_file: pathlib.Path = pydantic.Field(
        JSON_DATA_DIR / "disallowed_words.json",
        json_schema_extra={
            "env": "DISALLOWED_WORDS_FILE",
            "description": "The path to the JSON file containing the disallowed words.",
        },
    )
    allowed_entities_file: pathlib.Path = pydantic.Field(
        JSON_DATA_DIR / "allowed_entities.json",
        json_schema_extra={
            "env": "ALLOWED_ENTITIES_FILE",
            "description": "The path to the JSON file containing the allowed named entities.",
        },
    )


@functools.lru_cache()
def get_settings() -> Settings:
    """Cached call that returns the settings for the anonymization
    verification application.
    """
    return Settings()
