"""
Trigram Language Model for Urdu Story Generation
Phase III - Built from scratch without any pre-built models
Uses BPE tokenization from Phase II (subword-level, not character-level).

Usage:
    from trigram_model import TrigramLanguageModel, UrduStoryGenerator, StoryGeneratorAPI

    # Load pre-trained model
    api = StoryGeneratorAPI(model_path="trigram_model.pkl")

    # Generate story
    result = api.generate(prefix="ایک دن", max_length=1000)
    print(result["story"])
"""

import os
import re
import random
import pickle
import math
import json
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional

# Set random seed
random.seed(42)

# Special tokens - text-based tokens matching preprocessing output
EOS_TOKEN = "<EOS>"   # End of Sentence
EOP_TOKEN = "<EOP>"   # End of Paragraph
EOT_TOKEN = "<EOT>"   # End of Text/Story
START_TOKEN = "<START>"  # Start token for padding

SPECIAL_TOKENS = {EOS_TOKEN, EOP_TOKEN, EOT_TOKEN, START_TOKEN}


# ============================================
# BPE TOKENIZER (Phase II Integration)
# ============================================

class BPETokenizer:
    """
    BPE (Byte Pair Encoding) Tokenizer.
    Loads pre-trained vocabulary and merges from Phase II.
    Properly handles special tokens (<EOS>, <EOP>, <EOT>).
    """

    def __init__(self, vocab_path: str = None, merges_path: str = None):
        # Resolve default paths relative to this file
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if vocab_path is None:
            vocab_path = os.path.join(base, "Tokenization", "vocab.json")
        if merges_path is None:
            merges_path = os.path.join(base, "Tokenization", "merges.txt")

        self.vocab = self._load_vocab(vocab_path)
        self.merges = self._load_merges(merges_path)

        # Add special tokens to vocab if not present
        for token in SPECIAL_TOKENS:
            if token not in self.vocab:
                self.vocab.add(token)

    def _load_vocab(self, vocab_path: str) -> set:
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()

    def _load_merges(self, merges_path: str) -> List[Tuple[str, str]]:
        merges = []
        try:
            with open(merges_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(' ')
                    if len(parts) == 2:
                        merges.append((parts[0], parts[1]))
        except FileNotFoundError:
            pass
        return merges

    def _apply_merges(self, word: str) -> List[str]:
        if word in SPECIAL_TOKENS:
            return [word]
        tokens = list(word)
        for merge_pair in self.merges:
            i = 0
            while i < len(tokens) - 1:
                if tokens[i] == merge_pair[0] and tokens[i + 1] == merge_pair[1]:
                    tokens = tokens[:i] + [merge_pair[0] + merge_pair[1]] + tokens[i + 2:]
                else:
                    i += 1
        return tokens

    def tokenize(self, text: str) -> List[str]:
        tokens = []
        for word in text.split():
            word_tokens = self._apply_merges(word)
            # Mark the first subword of each non-special word with ▁ prefix
            # so we can reconstruct word boundaries during detokenization
            if word not in SPECIAL_TOKENS and word_tokens:
                word_tokens[0] = '▁' + word_tokens[0]
            tokens.extend(word_tokens)
        return tokens

    def detokenize(self, tokens: List[str]) -> str:
        """Reconstruct text from BPE tokens using ▁ word-boundary markers."""
        parts = []
        for token in tokens:
            if token in SPECIAL_TOKENS:
                parts.append(' ' + token + ' ')
            elif token.startswith('▁'):
                parts.append(' ' + token[1:])  # new word
            else:
                parts.append(token)  # continuation of previous word
        return re.sub(r' +', ' ', ''.join(parts)).strip()


class TrigramLanguageModel:
    """Trigram Language Model using MLE with Interpolation and BPE tokenization."""

    def __init__(self, lambda1: float = 0.1, lambda2: float = 0.3, lambda3: float = 0.6):
        assert abs(lambda1 + lambda2 + lambda3 - 1.0) < 1e-6
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.lambda3 = lambda3
        self.unigram_counts = Counter()
        self.bigram_counts = defaultdict(Counter)
        self.trigram_counts = defaultdict(Counter)
        self.total_unigrams = 0
        self.bigram_context_counts = Counter()
        self.trigram_context_counts = Counter()
        self.vocabulary = set()
        self.is_trained = False
        self.tokenizer = None  # BPE tokenizer set during training or loading

    def train(self, corpus: List[str], bpe_tokenizer: BPETokenizer = None):
        """Train on corpus using BPE tokenization (subword-level)."""
        self.tokenizer = bpe_tokenizer if bpe_tokenizer else BPETokenizer()
        for document in corpus:
            tokens = self.tokenizer.tokenize(document)
            padded = [START_TOKEN, START_TOKEN] + tokens
            self.vocabulary.update(tokens)
            for token in tokens:
                self.unigram_counts[token] += 1
                self.total_unigrams += 1
            for i in range(len(padded) - 1):
                ctx = padded[i]
                nxt = padded[i + 1]
                self.bigram_counts[ctx][nxt] += 1
                self.bigram_context_counts[ctx] += 1
            for i in range(len(padded) - 2):
                ctx = (padded[i], padded[i + 1])
                nxt = padded[i + 2]
                self.trigram_counts[ctx][nxt] += 1
                self.trigram_context_counts[ctx] += 1
        self.is_trained = True

    def get_interpolated_probability(self, context: Tuple[str, str], token: str) -> float:
        p1 = self.unigram_counts[token] / self.total_unigrams if self.total_unigrams > 0 else 0
        ctx_count = self.bigram_context_counts[context[1]]
        p2 = self.bigram_counts[context[1]][token] / ctx_count if ctx_count > 0 else 0
        tri_count = self.trigram_context_counts[context]
        p3 = self.trigram_counts[context][token] / tri_count if tri_count > 0 else 0
        return self.lambda1 * p1 + self.lambda2 * p2 + self.lambda3 * p3

    def sample_next_token(self, context: Tuple[str, str], temperature: float = 1.0) -> str:
        probs = {}
        for token in self.vocabulary:
            p = self.get_interpolated_probability(context, token)
            if p > 0:
                probs[token] = p ** (1.0 / temperature)
        if not probs:
            return random.choice(list(self.vocabulary))
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}
        return random.choices(list(probs.keys()), weights=list(probs.values()))[0]


class UrduStoryGenerator:
    """Story generator using Trigram model with BPE tokenization."""

    def __init__(self, model: TrigramLanguageModel):
        self.model = model

    def generate(self, prefix: str = "", max_length: int = 1000, temperature: float = 0.8) -> str:
        tokenizer = self.model.tokenizer
        if prefix and tokenizer:
            tokens = tokenizer.tokenize(prefix)
        elif prefix:
            tokens = prefix.split()
        else:
            tokens = []

        padded = [START_TOKEN, START_TOKEN] + tokens
        for _ in range(max_length):
            ctx = (padded[-2], padded[-1])
            nxt = self.model.sample_next_token(ctx, temperature)
            padded.append(nxt)
            if nxt == EOT_TOKEN:
                break

        output_tokens = padded[2:]
        if tokenizer:
            text = tokenizer.detokenize(output_tokens)
        else:
            text = ' '.join(output_tokens)

        # Clean special tokens for display
        text = text.replace(EOS_TOKEN, ' ')
        text = text.replace(EOP_TOKEN, '\n\n')
        text = text.replace(EOT_TOKEN, '')
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n +', '\n', text)
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        return text.strip()


class StoryGeneratorAPI:
    """API interface for FastAPI integration."""

    def __init__(self, model_path: str = None):
        self.bpe_tokenizer = BPETokenizer()
        if model_path and os.path.exists(model_path):
            self.model = self._load_model(model_path)
        else:
            self.model = TrigramLanguageModel()
            self.model.tokenizer = self.bpe_tokenizer
        self.generator = UrduStoryGenerator(self.model)

    def _load_model(self, path: str) -> TrigramLanguageModel:
        with open(path, 'rb') as f:
            data = pickle.load(f)
        model = TrigramLanguageModel(data['lambda1'], data['lambda2'], data['lambda3'])
        model.unigram_counts = Counter(data['unigram_counts'])
        model.bigram_counts = defaultdict(Counter)
        for k, v in data['bigram_counts'].items():
            model.bigram_counts[k] = Counter(v)
        model.trigram_counts = defaultdict(Counter)
        for k, v in data['trigram_counts'].items():
            model.trigram_counts[k] = Counter(v)
        model.total_unigrams = data['total_unigrams']
        model.bigram_context_counts = Counter(data['bigram_context_counts'])
        model.trigram_context_counts = Counter(data['trigram_context_counts'])
        model.vocabulary = data['vocabulary']
        model.is_trained = True
        model.tokenizer = self.bpe_tokenizer
        return model

    def generate(self, prefix: str = "", max_length: int = 1000, temperature: float = 0.8) -> dict:
        try:
            story = self.generator.generate(prefix, max_length, temperature)
            return {"success": True, "story": story, "prefix": prefix}
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    api = StoryGeneratorAPI(model_path="trigram_model.pkl")
    result = api.generate(prefix="ایک دن", max_length=500)
    print(result["story"] if result["success"] else result["error"])
