import functools
import pathlib
from typing import Iterable

import pydantic

JSON_DATA_DIR = pathlib.Path(__file__).parent / "jsons"


@pydantic.dataclasses.dataclass
class Replacement:
    """A replacement for a word or phrase.

    Attributes:
        find: The words or phrases to replace.
        replacement: The replacement word or phrase.
    """

    find: Iterable[str]
    replace: str


class Settings(pydantic.BaseModel):
    spacy_model: str = "en_core_web_trf"

    disallowed_words_file: str | pathlib.Path = pydantic.Field(
        JSON_DATA_DIR / "disallowed_words.json"
    )
    allowed_entities_file: str | pathlib.Path = pydantic.Field(
        JSON_DATA_DIR / "allowed_entities.json"
    )


@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()
