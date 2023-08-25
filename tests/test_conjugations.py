# pylint: disable=protected-access, redefined-outer-name
import pytest

from anonymization_verification import conjugations


@pytest.fixture
def conjugator() -> conjugations.CorrectConjugations:
    """Return a conjugator."""
    return conjugations.CorrectConjugations()


@pytest.mark.parametrize("is_question", [True, False])
def test_subject_verb_pair(is_question: bool):
    """Test the SubjectVerbPair class."""
    subject = "subject"
    verb = "verb"

    pair = conjugations.SubjectVerbPair(subject, verb, is_question)

    assert pair.subject == subject
    assert pair.verb == verb
    assert pair.is_question == is_question
    if is_question:
        assert pair.phrase == f"{verb} {subject}"
    else:
        assert pair.phrase == f"{subject} {verb}"


@pytest.mark.parametrize(
    "sentence, expected",
    [
        [
            "We are an extensive test.",
            [conjugations.SubjectVerbPair("We", "are", False)],
        ],
        [
            "He/she/they is/are allowed.",
            [conjugations.SubjectVerbPair("He/she/they", "is/are", False)],
        ],
        [
            "Are they allowed?",
            [conjugations.SubjectVerbPair("they", "Are", True)],
        ],
        [
            "He is allowed and she is allowed.",
            [
                conjugations.SubjectVerbPair("He", "is", False),
                conjugations.SubjectVerbPair("she", "is", False),
            ],
        ],
    ],
)
def test_detect_subject_and_verb(
    conjugator: conjugations.CorrectConjugations,
    sentence: str,
    expected: conjugations.SubjectVerbPair,
) -> None:
    """Test the detect_subject_and_verb method."""
    actual = conjugator._detect_subject_and_verb(sentence)

    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        [
            "This is a test.",
            ["This is a test."],
        ],
        [
            "This is a test. This is a test.",
            ["This is a test.", "This is a test."],
        ],
        [
            "Is this a test? You bet it is.",
            ["Is this a test?", "You bet it is."],
        ],
        [
            "This is a test.\nYou bet it is.",
            ["This is a test.", "You bet it is."],
        ],
    ],
)
def test_split_by_sentences(
    conjugator: conjugations.CorrectConjugations,
    text: str,
    expected: list[str],
) -> None:
    """Test the split_by_sentences method."""
    actual = conjugator._split_by_sentences(text)

    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        [
            "She is a test.",
            set(),
        ],
        [
            "He/she/they is/are happy.",
            set(),
        ],
        [
            "He are a pronoun.",
            {"He are"},
        ],
        [
            "He/she/they is happy.",
            {"He/she/they is"},
        ],
        [
            "He is a test. Is she a test?",
            set(),
        ],
        [
            "He are a test. Are she a test?",
            {"He are", "Are she"},
        ],
        [
            "He are bright and she are bright.",
            {"He are", "she are"},
        ],
    ],
)
def test_find_faulty_conjugation(
    conjugator: conjugations.CorrectConjugations, text: str, expected: str
) -> None:
    """Test the find_faulty_conjugation method."""
    actual = conjugator.find_faulty_conjugation(text)

    assert actual == expected
