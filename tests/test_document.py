""" Tests for the document module. """
# pylint: disable=redefined-outer-name
import pathlib
import tempfile
from typing import Generator

import docx
import pytest

from anonymization_verification import document


@pytest.fixture
def word_document(word_text: list[str]) -> Generator[str, None, None]:
    """Creates a Word document with the given text.

    Args:
        word_text: A list of strings representing the paragraphs to be added to
            the document.

    Returns:
        str: The path to the created Word document.
    """
    with tempfile.NamedTemporaryFile(suffix=".docx") as file_buffer:
        doc = docx.Document()
        for paragraph in word_text:
            doc.add_paragraph(paragraph)
        doc.save(file_buffer.name)
        yield str(pathlib.Path(file_buffer.name))


@pytest.mark.parametrize(
    "word_text, expected",
    [
        [["This is a test."], False],
        [["He/she/they is allowed."], False],
        [["He is a pronoun."], True],
        [["Mr. is not allowed"], True],
        [["Ms. is not allowed"], True],
        [["First sentence allowed", "Himself second is not"], True],
    ],
)
def test_check_disallowed_words(word_document: str, expected: bool) -> None:
    """Test the check_disallowed_words method."""
    word_document = document.WordDocument(word_document, None)

    assert word_document.contains_disallowed_words() == expected


@pytest.mark.parametrize(
    "word_text, expected",
    [
        [["This is a test."], False],
        [["He/she/they is allowed."], False],
        [["Mcdonalds is not allowed"], True],
        [["First sentence allowed", "Sir, this is a Wendy's"], True],
        [["Child Mind Institute is allowed"], False],
    ],
)
def test_check_named_entities(word_document: str, expected: bool) -> None:
    """Test the check_named_entities method."""
    word_document = document.WordDocument(word_document, "en_core_web_sm")

    assert word_document.contains_named_entities() == expected
