"""Customer Input Data Cleaning Pipeline.

Usage:
    python clean_comments.py input.csv [output.csv]

The input file (CSV or Excel) must contain a "Comment" column.
The output file contains the original and cleaned comments, word counts
before and after cleaning, and a flag showing whether cleaning succeeded.
"""

import html
import re
import sys
import time

import contractions
import nltk
import pandas as pd
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)

# Precompiled patterns (compiled once, reused for every row)
HTML_TAG = re.compile(r"<[^>]+>")
NON_ASCII = re.compile(r"[^\x00-\x7F]+")
REPEATS = re.compile(r"(.)\1{2,}")
NON_ALPHA = re.compile(r"[^a-z\s]")

# Stopword set (fast lookups); negations are kept because they change meaning
STOP_WORDS = set(stopwords.words("english")) - {"no", "nor", "not"}


def clean_text(text):
    """Clean one comment and return the cleaned string."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = HTML_TAG.sub(" ", text)
    text = text.replace("\u2019", "'")           # curly apostrophe -> straight
    text = NON_ASCII.sub(" ", text)              # emojis and other symbols
    text = contractions.fix(text)                # don't -> do not
    text = REPEATS.sub(r"\1\1", text)            # sooo -> soo
    text = text.lower()
    text = NON_ALPHA.sub(" ", text)              # keep letters only
    words = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(words)


def count_words(text):
    """Number of words in a string (0 for missing or non-text values)."""
    return len(text.split()) if isinstance(text, str) else 0


def process(df, column="Comment"):
    """Clean a DataFrame and add word counts and a success flag.

    Cleaning_Success is True when the cleaned comment still contains text.
    It is False for comments that become empty (for example emoji-only,
    numbers-only, or non-English comments).
    """
    if column not in df.columns:
        raise KeyError(f'Column "{column}" not found. Available columns: {list(df.columns)}')
    out = df[[column]].rename(columns={column: "Comment"}).copy()
    out["Cleaned_Comment"] = out["Comment"].apply(clean_text)
    out["Words_Before"] = out["Comment"].apply(count_words)
    out["Words_After"] = out["Cleaned_Comment"].apply(count_words)
    out["Cleaning_Success"] = out["Cleaned_Comment"].str.len() > 0
    return out


def summary(out, elapsed=None):
    """Return a short text summary of a processed DataFrame."""
    before, after = out["Words_Before"].sum(), out["Words_After"].sum()
    ok = int(out["Cleaning_Success"].sum())
    reduction = (1 - after / before) * 100 if before else 0
    lines = [
        f"Rows cleaned: {len(out)}",
        f"Successful: {ok}  |  Empty after cleaning: {len(out) - ok}",
        f"Total words before: {before}",
        f"Total words after: {after}  ({reduction:.1f}% fewer)",
    ]
    if elapsed is not None:
        lines.append(f"Time taken: {elapsed:.2f} seconds")
    return "\n".join(lines)


def load(path):
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    return pd.read_csv(path, on_bad_lines="skip")


def main(in_path, out_path="cleaned_output.csv"):
    df = load(in_path)
    start = time.time()
    out = process(df)
    elapsed = time.time() - start
    out.to_csv(out_path, index=False)
    print(summary(out, elapsed))
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python clean_comments.py input.csv [output.csv]")
    main(*sys.argv[1:3])
