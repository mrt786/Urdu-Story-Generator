<<<<<<< HEAD
"""
Trigram Language Model for Urdu Story Generation
Phase III - Built from scratch without any pre-built models

Usage:
    from trigram_model import TrigramLanguageModel, UrduStoryGenerator, StoryGeneratorAPI

    # Load pre-trained model
    api = StoryGeneratorAPI(model_path="trigram_model.pkl")

    # Generate story
    result = api.generate(prefix="ایک دن", max_length=1000)
    print(result["story"])
"""

=======
>>>>>>> 094499a (frontend And backend done)
import os
import random
import pickle
import math
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional

<<<<<<< HEAD
# Set random seed
random.seed(42)

# Special tokens
EOS_TOKEN = "\ue000"  # End of Sentence
EOP_TOKEN = "\ue001"  # End of Paragraph
EOT_TOKEN = "\ue002"  # End of Text/Story
START_TOKEN = "\ue003"  # Start token


class TrigramLanguageModel:
    """Trigram Language Model using MLE with Interpolation."""

=======
random.seed(42)

EOS_TOKEN = "\ue000"
EOP_TOKEN = "\ue001"
EOT_TOKEN = "\ue002"
START_TOKEN = "\ue003"


class TrigramLanguageModel:
>>>>>>> 094499a (frontend And backend done)
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

    def train(self, corpus: List[str]):
        for document in corpus:
            tokens = list(document)
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
<<<<<<< HEAD
    """Story generator using Trigram model."""

=======
>>>>>>> 094499a (frontend And backend done)
    def __init__(self, model: TrigramLanguageModel):
        self.model = model

    def generate(self, prefix: str = "", max_length: int = 1000, temperature: float = 0.8) -> str:
        tokens = list(prefix) if prefix else []
        padded = [START_TOKEN, START_TOKEN] + tokens
        for _ in range(max_length):
            ctx = (padded[-2], padded[-1])
            nxt = self.model.sample_next_token(ctx, temperature)
            padded.append(nxt)
            if nxt == EOT_TOKEN:
                break
        text = ''.join(padded[2:])
        return text.replace(EOS_TOKEN, '').replace(EOP_TOKEN, '\n\n').replace(EOT_TOKEN, '').strip()


class StoryGeneratorAPI:
<<<<<<< HEAD
    """API interface for FastAPI integration."""

=======
>>>>>>> 094499a (frontend And backend done)
    def __init__(self, model_path: str = None):
        if model_path and os.path.exists(model_path):
            self.model = self._load_model(model_path)
        else:
            self.model = TrigramLanguageModel()
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
