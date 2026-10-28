import re
import html
import unicodedata


EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
URL_REGEX = re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', re.IGNORECASE)
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')


def clean_text(text: str) -> str:
    """
    Cleans and normalizes raw job posting text while preserving readability.
    - Strips HTML tags
    - Unescapes HTML entities
    - Normalizes unicode characters
    - Cleans excessive whitespace
    """
    if not text or not isinstance(text, str):
        return ""

    # Unescape HTML entities
    text = html.unescape(text)
    
    # Strip HTML tags if any were pasted
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Normalize unicode (NFKC)
    text = unicodedata.normalize('NFKC', text)
    
    # Replace weird zero-width or non-breaking spaces
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    
    # Collapse multiple blank lines and spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove space before punctuation that may have been caused by tag removal
    text = re.sub(r'\s+([,.:;!?])', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def extract_emails(text: str) -> list[str]:
    """Extract all email addresses from text."""
    if not text:
        return []
    return list(set(EMAIL_REGEX.findall(text)))


def extract_urls(text: str) -> list[str]:
    """Extract all web links from text."""
    if not text:
        return []
    return list(set(URL_REGEX.findall(text)))


def extract_phone_numbers(text: str) -> list[str]:
    """Extract phone numbers from text."""
    if not text:
        return []
    return list(set(PHONE_REGEX.findall(text)))


def prepare_for_vectorizer(text: str) -> str:
    """
    Normalizes text for TF-IDF vectorization:
    - Lowercase
    - Replaces emails with generic token
    - Replaces URLs with generic token
    - Removes punctuation and non-alphanumeric chars
    """
    cleaned = clean_text(text).lower()
    cleaned = EMAIL_REGEX.sub(' token_email ', cleaned)
    cleaned = URL_REGEX.sub(' token_url ', cleaned)
    # Remove punctuation except underscores
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    # Collapse whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()
