"""
config.py – Central Configuration
===================================
All hyperparameters and paths for the Deep Sequence Model pipeline.
"""

import os

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_DATA_DIR = "data/raw/cornell_movie_dialogs_corpus"
PROCESSED_DATA_DIR = "data/processed"
CHECKPOINT_DIR = "model/checkpoints"
RESULTS_DIR = "evaluation/results"

# ── Dataset ───────────────────────────────────────────────────────────────────
CORNELL_URL = "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"
MAX_PAIRS = 25000          # Number of conversation pairs to use
MAX_SEQ_LENGTH = 20        # Maximum tokens per sentence
MIN_WORD_FREQ = 3          # Minimum word frequency to include in vocab

# ── Preprocessing ─────────────────────────────────────────────────────────────
MAX_VOCAB_SIZE = 15000     # Maximum vocabulary size
USE_STEMMING = False       # Whether to apply Porter Stemming
USE_LEMMATIZATION = True   # Whether to apply WordNet Lemmatization

# ── Model Architecture ───────────────────────────────────────────────────────
EMBEDDING_DIM = 256        # Word embedding dimension
ENCODER_UNITS = 256        # LSTM hidden units (encoder)
DECODER_UNITS = 256        # LSTM hidden units (decoder)
ATTENTION_UNITS = 256      # Bahdanau attention units
DROPOUT_RATE = 0.2         # Dropout rate

# ── Training ──────────────────────────────────────────────────────────────────
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.001
GRADIENT_CLIP_NORM = 5.0
TEACHER_FORCING_RATIO = 1.0   # 1.0 = always use teacher forcing
VALIDATION_SPLIT = 0.1
TEST_SPLIT = 0.05
EARLY_STOPPING_PATIENCE = 5

# ── Inference ─────────────────────────────────────────────────────────────────
BEAM_WIDTH = 3             # Beam search width (1 = greedy decoding)
TEMPERATURE = 0.7          # Sampling temperature

# ── Special Tokens ────────────────────────────────────────────────────────────
START_TOKEN = "<start>"
END_TOKEN = "<end>"
PAD_TOKEN = "<pad>"

# ── Create directories ───────────────────────────────────────────────────────
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CHECKPOINT_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)
