"""This module provides a class for representing a Word document and checking if
it contains gendered language or named entities."""

import json
import logging
import pathlib
from typing import Callable, Iterable

import docx
import spacy

from anonymization_verification import config

settings = config.get_settings()
SPACY_MODEL = settings.spacy_model
LOGGER_NAME = settings.logger_name

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class AnoynimityVerifier:
    """Class for verifying anonymity of (an iterable of) string(s).

    Attributes:
        text: An iterable of strings or a string.
    """

    def __init__(
        self,
        text: str | Iterable[str],
        entity_recognition_model: str | None = SPACY_MODEL,
    ) -> None:
        """Initialize the AnoynimityVerifier object.

        Args:
            text: An iterable of strings or a string.
            ner_model: The name of the spaCy model to use for named entity recognition.
                If None, no model is loaded.
        """
        self.text = tuple(text) if isinstance(text, str) else text
        self.entity_recognition_model = (
            spacy.load(entity_recognition_model) if entity_recognition_model else None
        )

    def contains_any_disallowed(self) -> bool:
        """Check if the document passes all checks.

        Returns:
            True if the document passes all checks, False otherwise.
        """
        return self.contains_disallowed_words() or self.contains_named_entities()

    def check_fun(self, fun: Callable[[str], bool]) -> bool:
        """Check if the document returns True for an arbitrary function.

        Args:
            fun: A function that takes a string and returns a boolean.

        Returns:
            True if any paragraphs in the document return True for the function, False otherwise.
        """
        disallowed = [paragraph.text for paragraph in self.text if fun(paragraph.text)]
        if disallowed:
            print("Found the following disallowed paragraphs:")
            print(disallowed)
        return bool(disallowed)

    def contains_disallowed_words(self) -> bool:
        """Check if the document contains disallowed words.

        Returns:
            True if the document contains disallowed words, False otherwise.
        """
        with open(settings.disallowed_words_file, "r", encoding="utf-8") as file_buffer:
            disallowed_words = json.load(file_buffer)

        def any_disallowed_words(text: str) -> bool:
            text_split = text.lower().split()
            return any(word.lower() in text_split for word in disallowed_words)

        return self.check_fun(any_disallowed_words)

    def contains_named_entities(self) -> bool:
        """Check if the document contains named entities.

        Returns:
            True if the document contains named entities, False otherwise.
        """
        if not self.entity_recognition_model:
            raise ValueError(
                "No spaCy model loaded. Please provide a spaCy model name to the constructor."
            )

        with open(settings.allowed_entities_file, "r", encoding="utf-8") as file_buffer:
            allowed_entities = json.load(file_buffer)

        def any_named_entities(text: str) -> bool:
            doc = self.entity_recognition_model(text)
            return any(ent.text not in allowed_entities for ent in doc.ents)

        return self.check_fun(any_named_entities)


class WordDocument(AnoynimityVerifier):
    """A class representing a Word document that can be used to verify the anonymity of its contents.
    Inherits from `AnoynimityVerifier`.

    Args:
        filename: The path to the Word document file.

    Attributes:
        filename: The path to the Word document file.
        document: The Word document object.
    """

    def __init__(
        self,
        filename: str | pathlib.Path,
        entity_recognition_model: str | None = SPACY_MODEL,
    ) -> None:
        """Initialize the WordDocument object.

        Args:
            filename: The path to the Word document file.

        """
        self.filename = pathlib.Path(filename)
        self.document = docx.Document(str(filename))
        paragraphs = []
        for paragraph in self.document.paragraphs:
            if isinstance(paragraph, str):
                paragraphs.append(paragraph)
            else:
                paragraphs.append(paragraph.text)
        super().__init__(
            self.document.paragraphs, entity_recognition_model=entity_recognition_model
        )
