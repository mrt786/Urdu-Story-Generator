import os
import re
from collections import Counter, defaultdict
import json

base_dir = os.path.dirname(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(
    base_dir,
    "Preprocessing",
    "Preprocessed_documents"
)

# Special tokens that should NOT be split into characters
SPECIAL_TOKENS = {"<EOS>", "<EOP>", "<EOT>"}

def load_dataset():
    corpus = []

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".txt"):
            with open(os.path.join(DATA_FOLDER, file),
                      "r", encoding="utf-8") as f:
                corpus.append(f.read())

    return corpus


def tokenize_word(word):
    """
    Convert a word into tuple of characters,
    but keep special tokens intact (not split).
    """
    # Check if this is a special token
    if word in SPECIAL_TOKENS:
        return (word,)  # Keep as single token tuple
    
    # Otherwise, split into characters
    return tuple(word)


def split_special_tokens(token):
    """
    Split a token that might have special tokens attached.
    E.g., '<EOS>word' -> ['<EOS>', 'word']
    """
    result = []
    remaining = token
    
    while remaining:
        found_special = False
        for special in SPECIAL_TOKENS:
            if remaining.startswith(special):
                result.append(special)
                remaining = remaining[len(special):]
                found_special = True
                break
            elif special in remaining:
                # Special token is in the middle
                idx = remaining.index(special)
                if idx > 0:
                    result.append(remaining[:idx])
                result.append(special)
                remaining = remaining[idx + len(special):]
                found_special = True
                break
        
        if not found_special:
            result.append(remaining)
            break
    
    return [r for r in result if r]  # Filter empty strings


def get_word_freqs(corpus):
    """
    Get word frequencies from corpus.
    Returns dict: word_tuple -> frequency count
    """
    word_freqs = Counter()

    for story in corpus:
        # Split by whitespace
        tokens = story.split()
        
        for token in tokens:
            # First, split any attached special tokens
            parts = split_special_tokens(token)
            
            for part in parts:
                # Tokenize each part (special tokens stay intact)
                tokenized = tokenize_word(part)
                word_freqs[tokenized] += 1

    return word_freqs


def get_pair_counts(word_freqs):
    """
    Count pairs of adjacent symbols weighted by word frequency.
    Skip special tokens.
    """
    pairs = Counter()

    for word, freq in word_freqs.items():
        # Skip special tokens entirely
        if len(word) == 1 and word[0] in SPECIAL_TOKENS:
            continue
            
        for i in range(len(word) - 1):
            # Don't count pairs involving special tokens
            if word[i] in SPECIAL_TOKENS or word[i+1] in SPECIAL_TOKENS:
                continue
            pairs[(word[i], word[i+1])] += freq

    return pairs


def merge_pair_in_word(word, pair):
    """
    Merge a pair of symbols in a word tuple.
    Returns new tuple with the pair merged.
    """
    if len(word) < 2:
        return word
    
    new_word = []
    i = 0
    while i < len(word):
        if i < len(word) - 1 and word[i] == pair[0] and word[i+1] == pair[1]:
            new_word.append(pair[0] + pair[1])
            i += 2
        else:
            new_word.append(word[i])
            i += 1
    
    return tuple(new_word)


def merge_pair(pair, word_freqs):
    """
    Merge a pair of symbols in all words.
    Returns new word_freqs dict.
    """
    new_word_freqs = Counter()

    for word, freq in word_freqs.items():
        # Don't modify special tokens
        if len(word) == 1 and word[0] in SPECIAL_TOKENS:
            new_word_freqs[word] = freq
        else:
            new_word = merge_pair_in_word(word, pair)
            new_word_freqs[new_word] += freq

    return new_word_freqs


def train_bpe(vocab_size=1000):
    """
    Train BPE tokenizer with specified vocabulary size.
    Uses word frequencies for efficient training.
    """
    corpus = load_dataset()
    word_freqs = get_word_freqs(corpus)

    print(f"Loaded {len(word_freqs)} unique words")

    # Build initial vocabulary from all characters
    all_chars = set()
    for word in word_freqs.keys():
        if len(word) == 1 and word[0] in SPECIAL_TOKENS:
            all_chars.add(word[0])
        else:
            all_chars.update(word)
    
    vocab = all_chars.copy()
    merges = []

    print(f"Initial vocab size: {len(vocab)}")
    print(f"Target vocab size: {vocab_size}")

    while len(vocab) < vocab_size:
        pairs = get_pair_counts(word_freqs)

        if not pairs:
            print("No more pairs to merge")
            break

        best = pairs.most_common(1)[0][0]

        word_freqs = merge_pair(best, word_freqs)
        merges.append(best)

        new_token = "".join(best)
        vocab.add(new_token)

        if len(merges) % 100 == 0:
            print(f"Merged: {best} | vocab: {len(vocab)}")

    print(f"Final vocab size: {len(vocab)}")
    
    # Return word_freqs directly - save_encoded_dataset will handle it
    return vocab, merges, word_freqs





def save_results(vocab, merges):
    """Save vocabulary and merges to files."""
    with open("Tokenization/vocab.json", "w", encoding="utf-8") as f:
        json.dump(list(vocab), f, ensure_ascii=False, indent=2)

    with open("Tokenization/merges.txt", "w", encoding="utf-8") as f:
        for m in merges:
            f.write(f"{m[0]} {m[1]}\n")


def save_encoded_dataset(word_freqs):
    """Save the encoded dataset (unique words with frequencies)."""
    with open("Tokenization/encoded_dataset.txt",
              "w", encoding="utf-8") as f:

        for word, freq in word_freqs.items():
            word_str = " ".join(word)
            f.write(f"{word_str}\t{freq}\n")



if __name__ == "__main__":
    # Train BPE with vocabulary size = 250 as per assignment requirement
    vocab, merges, word_freqs = train_bpe(250)
    save_results(vocab, merges)
    save_encoded_dataset(word_freqs)
    print("BPE training complete!")
    print("BPE training complete!")
