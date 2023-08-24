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
        [["This is a test."], True],
        [["He/she/they is allowed."], True],
        [["He is a pronoun."], False],
        [["Mr. is not allowed"], False],
        [["Ms. is not allowed"], False],
        [["First sentence allowed", "Himself second is not"], False],
    ],
)
def test_check_disallowed_words(word_document: str, expected: bool) -> None:
    """Test the check_disallowed_words method."""
    word_document = document.WordDocument(word_document)

    assert word_document.check_disallowed_words() == expected
