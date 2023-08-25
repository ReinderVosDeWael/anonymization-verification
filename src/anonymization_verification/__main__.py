"""Entry point for the anonymization verification module."""
# Disable wrong imports so argparse can fail fast.
# pylint: disable=wrong-import-position
import argparse

parser = argparse.ArgumentParser(
    description="Anonymization verification of Word documents.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog="Copyright 2023, Child Mind Institute",
)
parser.add_argument(
    "document_path",
    type=str,
    help="Path to the word document.",
)
parser.add_argument(
    "--spacy_model",
    type=str,
    default="en_core_web_trf",
    help="Name of the spaCy model to use for named entity recognition.",
)

from anonymization_verification import document

args = parser.parse_args()

doc = document.WordDocument(args.document_path, args.spacy_model)
disallowed = doc.find_any_disallowed()

if disallowed:
    print(f"Disallowed words: {' '.join(disallowed)}")
