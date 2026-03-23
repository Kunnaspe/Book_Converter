import re
from collections import Counter

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk import ne_chunk, pos_tag

# download the required NLTK data packages on first import so the app
# works on a fresh server without a separate setup step
for _pkg in ('punkt', 'punkt_tab', 'stopwords', 'averaged_perceptron_tagger',
             'averaged_perceptron_tagger_eng', 'maxent_ne_chunker',
             'maxent_ne_chunker_tab', 'words'):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass

# compile the Gutenberg header and footer patterns once at module level
# so they are not recompiled on every call
_HEADER_PATTERN = re.compile(
    r'^\*{3}\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*{3}',
    re.IGNORECASE | re.DOTALL,
)
_FOOTER_PATTERN = re.compile(
    r'\*{3}\s*END OF (THE|THIS) PROJECT GUTENBERG.*',
    re.IGNORECASE | re.DOTALL,
)


def strip_gutenberg_header_footer(text):
    """remove the standard Project gutenberg header and footer from a text
    string and then return the cleaned body so NLP runs only on the actual novel
    content rather than the base template."""
    # split on the START marker and take everything after it
    start_match = re.search(
        r'\*{3}\s*START OF (THE|THIS) PROJECT GUTENBERG[^\*]*\*{3}',
        text,
        re.IGNORECASE,
    )
    if start_match:
        text = text[start_match.end():]

    # Then cut off anything after the END marker
    end_match = re.search(
        r'\*{3}\s*END OF (THE|THIS) PROJECT GUTENBERG[^\*]*\*{3}',
        text,
        re.IGNORECASE,
    )
    if end_match:
        text = text[:end_match.start()]

    return text.strip()


def tokenize_text(text):
    """tokenize the text into sentences and words and return a summary dict
    with sentence_count, total_tokens and alpha_tokens so the template can
    display basic statistics without extra computation."""
    try:
        sentences = sent_tokenize(text)
        tokens = word_tokenize(text)
        alpha_tokens = [t for t in tokens if t.isalpha()]
        return {
            'sentence_count': len(sentences),
            'total_tokens': len(tokens),
            'alpha_tokens': len(alpha_tokens),
        }
    except Exception as e:
        print(f'nlp_utils tokenize_text error: {e}')
        return {
            'sentence_count': 0,
            'total_tokens': 0,
            'alpha_tokens': 0,
        }


def word_frequency(text, top_n=30, exclude_stopwords=True):
    """Count word frequencies across the text and return the top_n words
    as a list of (word, count) tuples sorted from most to least frequent.
    Lowercases everything and optionally strips English stopwords so common
    function words do not dominate the results."""
    try:
        tokens = word_tokenize(text.lower())
        alpha_tokens = [t for t in tokens if t.isalpha()]
        if exclude_stopwords:
            stop_words = set(stopwords.words('english'))
            alpha_tokens = [t for t in alpha_tokens if t not in stop_words]
        counter = Counter(alpha_tokens)
        return counter.most_common(top_n)
    except Exception as e:
        print(f'nlp_utils word_frequency error: {e}')
        return []


def extract_named_entities(text, max_sentences=100):
    """Run NLTK named entity recognition on up to max_sentences sentences
    and return a dict mapping entity type labels such as PERSON and
    ORGANIZATION to lists of entity name strings. Caps the sentence count
    to keep response times reasonable for very long novels."""
    entities = {}
    try:
        sentences = sent_tokenize(text)[:max_sentences]
        for sentence in sentences:
            tokens = word_tokenize(sentence)
            tagged = pos_tag(tokens)
            tree = ne_chunk(tagged, binary=False)
            for subtree in tree:
                if hasattr(subtree, 'label'):
                    entity_type = subtree.label()
                    entity_name = ' '.join(leaf[0] for leaf in subtree.leaves())
                    entities.setdefault(entity_type, []).append(entity_name)
    except Exception as e:
        print(f'nlp_utils extract_named_entities error: {e}')
    return entities


def extract_entity_counts(text, max_sentences=100):
    """Extract named entities and then count how often each unique name
    appears across the sentences. Returns a list of dicts each with name,
    type and count keys sorted by count descending so the most prominent
    characters and places appear first in the template."""
    try:
        raw = extract_named_entities(text, max_sentences=max_sentences)
        # Build a flat counter keyed by (name, type) so duplicates across
        # sentence boundaries are merged correctly
        counter = Counter()
        for entity_type, names in raw.items():
            for name in names:
                counter[(name, entity_type)] += 1
        results = [
            {'name': name, 'type': etype, 'count': count}
            for (name, etype), count in counter.items()
        ]
        results.sort(key=lambda x: x['count'], reverse=True)
        return results
    except Exception as e:
        print(f'nlp_utils extract_entity_counts error: {e}')
        return []


def analyze_novel(text, top_n_words=30, ner_sentences=100):
    """Run the full NLP pipeline on the given text and return one dict
    that contains tokenization stats, word frequency and entity counts so
    views only need a single call to get everything for the analyze page."""
    try:
        cleaned = strip_gutenberg_header_footer(text)
        stats = tokenize_text(cleaned)
        top_words = word_frequency(cleaned, top_n=top_n_words)
        entity_counts = extract_entity_counts(cleaned, max_sentences=ner_sentences)
        return {
            'stats': stats,
            'top_words': top_words,
            'entity_counts': entity_counts,
        }
    except Exception as e:
        print(f'nlp_utils analyze_novel error: {e}')
        return {
            'stats': {'sentence_count': 0, 'total_tokens': 0, 'alpha_tokens': 0},
            'top_words': [],
            'entity_counts': [],
        }
