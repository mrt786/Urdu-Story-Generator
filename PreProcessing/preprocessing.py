import os
import re
import unicodedata

# ===== PATHS =====
base_dir = os.path.dirname(os.path.dirname(__file__))
input_folder = os.path.join(base_dir, "Scraping", "Documents")
output_folder = os.path.join(base_dir, "Preprocessing", "Preprocessed_documents")

os.makedirs(output_folder, exist_ok=True)


urdu_range = r"\u0600-\u06FF"

# Keep Urdu chars + punctuation
allowed_pattern = rf"[^{urdu_range}\s۔،؟!]+"

# Sentence ending punctuation
sentence_end_characters = r"[۔؟!]"


# Some functions for cleaning
def remove_writer_name(text):
    """
        Get's the text, and removes the author name
        which is in the first line
    """
    lines = text.splitlines()

    # remove empty lines at start
    while lines and lines[0].strip() == "":
        lines.pop(0)

    # remove first line (author name)
    if lines:
        lines = lines[1:]

    return "\n".join(lines)



def normalize_unicode(text):
    """Normalize Urdu unicode forms"""
    return unicodedata.normalize("NFC", text)


def remove_unwanted_chars(text):
    """Remove English, numbers, special symbols if any"""
    text = re.sub(allowed_pattern, "", text)
    return text


def normalize_spaces(text):
    """
    Normalize spaces WITHOUT removing line breaks
    """

    # remove extra spaces inside lines only
    text = re.sub(r"[ \t]+", " ", text)

    # remove extra blank lines (keep paragraph structure)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()



def add_special_tokens(text):
    """
    Add:
    <EOS> sentence end
    <EOP> paragraph end
    <EOT> story end
    """

    # Add EOS after sentence endings
    text = re.sub(sentence_end_characters, lambda m: m.group() + " <EOS>", text)

    # Paragraph splitting
    paragraphs = text.split("\n\n")
    paragraphs = [p.strip() + " <EOP>" for p in paragraphs if p.strip()]

    final_text = "\n".join(paragraphs)
    final_text += " <EOT>"

    return final_text


def preprocess_text(text):
    text = remove_writer_name(text)
    text = normalize_unicode(text)
    text = remove_unwanted_chars(text)
    text = normalize_spaces(text)
    text = add_special_tokens(text)
    return text


def process_files():
    """
        Main function which will call all the functions,
        for each of the document.
    """
    files = sorted(os.listdir(input_folder))
    for file in files:
        if not file.endswith(".txt"):
            continue

        input_path = os.path.join(input_folder, file)
        output_path = os.path.join(output_folder, file)

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        processed_text = preprocess_text(text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(processed_text)

        print(f"Processed: {file}")


if __name__ == "__main__":
    process_files()
    output_path = os.path.join(output_folder, 'doc1.txt')