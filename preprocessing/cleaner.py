import re
from pathlib import Path

# Correct import (since we're inside preprocessing folder)
from preprocessing.io_utils import list_documents, read_markdown, read_csv

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Absolute path to raw data
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def clean_text(text: str) -> str:
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove non-ASCII characters
    text = re.sub(r"[^\x20-\x7E]", " ", text)

    # Remove common junk symbols (but keep sentence punctuation)
    text = re.sub(r"[\/\\\|\*\~\`\@\#\$\%\^\&\_\=\+\[\]\{\}\<\>]", " ", text)

    # Remove multiple punctuation runs (e.g., "??", "!!", "--")
    text = re.sub(r"([!?.,\-]){2,}", r"\1", text)

    # Remove leftover HTML entities
    text = re.sub(r"&[a-z]+;", " ", text)

    # Final whitespace cleanup
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    print("Cleaning documents...\n")

    documents = list_documents(str(RAW_DATA_DIR))

    for doc in documents:
        if doc.endswith(".md"):
            raw_content = read_markdown(doc)
        elif doc.endswith(".csv"):
            raw_content = read_csv(doc)
        else:
            continue

        cleaned_content = clean_text(raw_content)

        print(f"Cleaned: {doc}")
        print(f"Raw length: {len(raw_content)} chars")
        print(f"Cleaned length: {len(cleaned_content)} chars\n")


if __name__ == "__main__":
    main()
