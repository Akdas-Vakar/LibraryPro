import os
import json
import math
import urllib.request
def get_embedding(text):
    """
    Fetches a 768-dimensional vector embedding for the input text using Gemini API.
    Returns None if no API key is set or if the request fails.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{
                "text": text
            }]
        }
    }
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['embedding']['values']
    except Exception as e:
        print(f"[AI Embeddings] Warning: API request failed. {e}")
        return None
def cosine_similarity(v1, v2):
    """
    Computes the cosine similarity between two float vectors.
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)
def get_sentiment(text):
    """
    Classifies the review sentiment as 'Positive', 'Negative', or 'Neutral'.
    Uses Gemini API if available, otherwise falls back to a custom local keyword heuristic.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        prompt = (
            f"Classify the sentiment of the following book review as exactly "
            f"'Positive', 'Negative', or 'Neutral'. Respond with only one word.\n\n"
            f"Review: \"{text}\""
        )
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode('utf-8'), 
                headers=headers, 
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                ans = res['candidates'][0]['content']['parts'][0]['text'].strip()
                ans = ans.replace('"', '').replace('.', '').strip()
                if ans in ['Positive', 'Negative', 'Neutral']:
                    return ans
        except Exception as e:
            print(f"[AI Sentiment] API error, using local fallback. {e}")
    pos_words = {
        'good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'liked', 
        'best', 'helpful', 'informative', 'perfect', 'must-read', 'interesting', 
        'fascinating', 'easy', 'enjoyed', 'brilliant', 'wonderful', 'beautiful'
    }
    neg_words = {
        'bad', 'worst', 'boring', 'terrible', 'awful', 'hate', 'dislike', 
        'useless', 'hard', 'difficult', 'poor', 'confusing', 'waste', 'disappointed',
        'unhelpful', 'slow', 'dry'
    }
    words = text.lower().split()
    pos_count = sum(1 for w in words if w.strip('.,!?;:"') in pos_words)
    neg_count = sum(1 for w in words if w.strip('.,!?;:"') in neg_words)
    if pos_count > neg_count:
        return 'Positive'
    elif neg_count > pos_count:
        return 'Negative'
    else:
        return 'Neutral'
def get_summary(title, author, category, description):
    """
    Generates a short structured summary or study guide using Gemini.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        prompt = (
            f"Provide a brief, structured, professional 3-sentence summary of the book "
            f"'{title}' by {author} in the category '{category}'. Include key takeaways."
        )
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode('utf-8'), 
                headers=headers, 
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"[AI Summarizer] API error, using local fallback. {e}")
    desc = description if description else "No detailed description available."
    return f"'{title}' is a notable book in the '{category}' category authored by {author}. Description: {desc}"
def determine_book_section_ai(title, author, category, description):
    """
    Uses Gemini API to determine the appropriate Category, Floor, and Section for a new book.
    Returns a dict: {'category': 'Fiction', 'floor': 'First Floor', 'section': 'Fiction Section'}
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {'category': 'General', 'floor': 'First Floor', 'section': 'General Section'}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    prompt = (
        f"You are a library classification assistant. Determine the best Category (e.g. Computer Science, Fiction, History), "
        f"Floor (First Floor, Second Floor, Third Floor, Fourth Floor), "
        f"and Section (e.g., Fiction Section, History Section, Science Fiction Section, Programming Section, etc.) for this book:\n"
        f"Title: {title}\nAuthor: {author}\nDescription: {description}\n"
        f"Respond ONLY with a valid JSON object in this exact format: {{ \"category\": \"Category Name\", \"floor\": \"Floor Name\", \"section\": \"Section Name\" }} "
    )
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            text = res['candidates'][0]['content']['parts'][0]['text'].strip()
            if text.startswith('```json'): text = text[7:]
            if text.endswith('```'): text = text[:-3]
            return json.loads(text.strip())
    except Exception as e:
        print(f"[AI Allocator] API error: {e}")
    return {'category': 'General', 'floor': 'First Floor', 'section': 'General Section'}
