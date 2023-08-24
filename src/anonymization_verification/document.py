"""This module provides a class for representing a Word document and checking if
it contains gendered language or named entities."""

import json
import pathlib
from typing import Callable

import docx
import spacy

from anonymization_verification import config

settings = config.get_settings()


nlp = spacy.load(settings.spacy_model)


class WordDocument:
    """A class representing a Word document.

    This class extends the `docx.Document` class and provides additional functionality for checking
    if the document contains gendered language or named entities.

    Args:
        filename: The path to the Word document file.

    Attributes:
        filename: The path to the Word document file.
    """

    def __init__(self, filename: str | pathlib.Path):
        self.filename = pathlib.Path(filename)
        self.document = docx.Document(str(filename))

    def check_fun(self, fun: Callable[[str], bool]) -> bool:
        """Check if the document returns True for an arbitrary function.

        Args:
            fun: A function that takes a string and returns a boolean.

        Returns:
            True if all paragraphs in the document return True for the function, False otherwise.
        """
        return all(fun(paragraph.text) for paragraph in self.document.paragraphs)

    def check_disallowed_words(self) -> bool:
        """Check if the document contains gendered language.

        Returns:
            True if the document contains gendered language, False otherwise.
        """
        with open(settings.disallowed_words_file, "r", encoding="utf-8") as file_buffer:
            disallowed_words = json.load(file_buffer)

        def check_disallowed_words(text: str) -> bool:
            text_split = text.lower().split()
            return all(word.lower() not in text_split for word in disallowed_words)

        return self.check_fun(check_disallowed_words)

    def check_named_entities(self) -> bool:
        """Check if the document contains named entities.

        Returns:
            True if the document contains named entities, False otherwise.
        """
        with open(settings.allowed_entities_file, "r", encoding="utf-8") as file_buffer:
            allowed_entities = json.load(file_buffer)

        def named_entity_check(text: str) -> bool:
            doc = nlp(text)
            return all(ent.text in allowed_entities for ent in doc.ents)

        return self.check_fun(named_entity_check)
