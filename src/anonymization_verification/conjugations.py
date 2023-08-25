"""Module for checking whether verbs are conjugated properly."""
import dataclasses
import itertools
import re

import mlconjug3

PRONOUNS = {
    "I",
    "you",
    "he",
    "she",
    "we",
    "they",
    "it",
}

# Add all permutations of pronouns to the set.
permutation_pronouns = ("he", "she", "they", "it")
for ii in range(2, len(permutation_pronouns) + 1):
    permutations = list(itertools.permutations(permutation_pronouns, ii))
    combined_permutations = ["/".join(permutation) for permutation in permutations]
    PRONOUNS.update(combined_permutations)


@dataclasses.dataclass
class SubjectVerbPair:
    """
    A class representing a subject-verb pair, with an optional flag indicating whether it is a question.

    Attributes:
        subject (str): The subject of the pair.
        verb (str): The verb of the pair.
        is_question (bool): Whether the pair represents a question.

    Properties:
        phrase (str): The phrase represented by the pair, with the subject and verb in the correct order.
    """

    subject: str
    verb: str
    is_question: bool

    @property
    def phrase(self) -> str:
        """Returns a phrase with the subject and verb in the correct order,
        depending on whether the Conjugation instance represents a question
        or not.

        If the Conjugation instance represents a question, the phrase will
        be in the form of "<verb> <subject>". Otherwise, the phrase will be
        in the form of "<subject> <verb>".

        Returns:
            A string representing the phrase.

        """
        if self.is_question:
            return f"{self.verb} {self.subject}"
        return f"{self.subject} {self.verb}"


class CorrectConjugations:
    """A class for detecting faulty verb conjugations in a piece of text.

    Attributes:
        conjugator: A Conjugator instance from the mlconjug3 library.
    """

    def __init__(self, language="en") -> None:
        """Initialize the CorrectConjugations object.

        Args:
            language: The language to use for conjugation. Defaults to "en".

        """
        self.conjugator = mlconjug3.Conjugator(language=language)

    def find_faulty_conjugation(self, text: str):
        """Check if the string contains verbs that are not conjugated properly.
        Only works on pronouns.

        Args:
            A piece of natural language.

        Returns:
            The verbs that are not conjugated properly.

        """
        sentences = self._split_by_sentences(text)
        faulty_conjugations = set()
        for sentence in sentences:
            subject_verb = self._detect_subject_and_verb(sentence)
            for sub_verbs in subject_verb:
                verb_conjugators = [
                    self.conjugator.conjugate(verb)
                    for verb in sub_verbs.verb.split("/")
                ]
                for subject in sub_verbs.subject.split("/"):
                    if subject.lower() in ("he", "she", "it"):
                        subject = "he/she/it"
                    verbs = sub_verbs.verb.split("/")
                    phrases = [
                        f"{subject.lower()} {conjugated_verb.lower()}"
                        for conjugated_verb in verbs
                    ]

                    if not any(
                        phrase in verb  # type: ignore[operator]
                        for verb in verb_conjugators
                        for phrase in phrases
                    ):
                        faulty_conjugations.add(sub_verbs.phrase)
                        break
        return faulty_conjugations

    @staticmethod
    def _detect_subject_and_verb(sentence: str) -> list[SubjectVerbPair]:
        """Detect the subject and verb of a sentence. Note, this only
        works for formal written English. It assumes that verbs occur
        before the subject if and only if the sentence is a question.
        It also assumes that the subject is a pronoun.

        Args:
            sentence: An English sentence.

        Returns:
            A list of tuples containing subjects and verbs.
        """
        words = sentence.split()
        is_question = sentence[-1] == "?"
        pairings = []
        for index, subject in enumerate(words):
            if subject.lower() not in PRONOUNS:
                continue
            verb = words[index - 1] if is_question else words[index + 1]
            pairings.append(SubjectVerbPair(subject, verb, is_question))

        if pairings:
            return pairings
        raise ValueError("No subject found.")

    @staticmethod
    def _split_by_sentences(text: str) -> list[str]:
        """Split a string into a list of sentences.

        Args:
            text: A piece of text.

        Returns:
            A list of sentences.
        """
        return re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\n)\s", text)
