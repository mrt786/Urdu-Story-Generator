import os
from collections import Counter, defaultdict
import json

base_dir = os.path.dirname(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(
    base_dir,
    "Preprocessing",
    "Preprocessed_documents"
)

def load_dataset():
    corpus = []

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".txt"):
            with open(os.path.join(DATA_FOLDER, file),
                      "r", encoding="utf-8") as f:
                corpus.append(f.read())

    return corpus


def get_words(corpus):
    words = []

    for story in corpus:
        words.extend(story.split())

    return [" ".join(list(word)) for word in words]


def get_pair_counts(words):
    pairs = Counter()

    for word in words:
        symbols = word.split()

        for i in range(len(symbols)-1):
            pairs[(symbols[i], symbols[i+1])] += 1

    return pairs

def merge_pair(pair, words):

    bigram = " ".join(pair)
    replacement = "".join(pair)

    new_words = []

    for word in words:
        new_words.append(word.replace(bigram, replacement))

    return new_words


def merge_pair(pair, words):

    bigram = " ".join(pair)
    replacement = "".join(pair)

    new_words = []

    for word in words:
        new_words.append(word.replace(bigram, replacement))

    return new_words




def train_bpe(vocab_size=250):

    corpus = load_dataset()
    words = get_words(corpus)

    vocab = set("→".join(words).replace(" ", ""))
    merges = []

    while len(vocab) < vocab_size:

        pairs = get_pair_counts(words)

        if not pairs:
            break

        best = pairs.most_common(1)[0][0]

        words = merge_pair(best, words)
        merges.append(best)

        vocab.add("".join(best))

        print("Merged:", best, "| vocab:", len(vocab))

    return vocab, merges, words





def save_results(vocab, merges):

    with open("Tokenization/vocab.json", "w", encoding="utf-8") as f:
        json.dump(list(vocab), f, ensure_ascii=False, indent=2)

    with open("Tokenization/merges.txt", "w", encoding="utf-8") as f:
        for m in merges:
            f.write(f"{m[0]} {m[1]}\n")

def save_encoded_dataset(words):

    with open("Tokenization/encoded_dataset.txt",
              "w", encoding="utf-8") as f:

        for w in words:
            f.write(w + "\n")



if __name__ == "__main__":
    vocab, merges, words = train_bpe(2000)
    save_results(vocab, merges)
    save_encoded_dataset(words)
