from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Enhanced spam word list with categories and weights
SPAM_WORDS = {
    'financial': ['money', 'cash', 'prize', 'million', 'dollar', 'profit', 'rich', 'wealth'],
    'urgency': ['urgent', 'immediately', 'instant', 'limited time', 'act now', 'expire', 'last chance'],
    'free_offers': ['free', 'win', 'winner', 'award', 'bonus', 'gift', 'reward', 'no cost'],
    'shady': ['click', 'link', 'unsubscribe', 'congratulations', 'selected', 'guaranteed', 'risk-free'],
    'adult': ['viagra', 'pills', 'pharmacy', 'xxx', 'adult', 'dating', 'single']
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-spam', methods=['POST'])
def check_spam():
    subject = request.form.get('subject', '')
    body = request.form.get('body', '')
    content = f"{subject} {body}".lower()
    
    # Check for excessive capitalization
    excessive_caps = len(re.findall(r'[A-Z]', f"{subject}{body}")) / len(f"{subject}{body}") > 0.5
    
    # Check for excessive punctuation
    excessive_punct = len(re.findall(r'[!?]', content)) > 3
    
    # Check for URLs
    has_urls = bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
    
    # Check for spam words
    matched = {category: [] for category in SPAM_WORDS}
    total_matches = 0
    
    for category, words in SPAM_WORDS.items():
        for word in words:
            if re.search(r'\b' + re.escape(word) + r'\b', content):
                matched[category].append(word)
                total_matches += 1
    
    # Calculate score (weighted by category)
    score = min(1.0, total_matches * 0.1 + excessive_caps * 0.2 + excessive_punct * 0.1 + has_urls * 0.2)
    
    # Determine if spam (threshold = 0.4)
    is_spam = score > 0.4
    
    # Prepare matched words for display
    matched_words_display = []
    for category, words in matched.items():
        if words:
            matched_words_display.append(f"{category}: {', '.join(words)}")
    
    return jsonify({
        'is_spam': is_spam,
        'score': round(score, 2),
        'matched_keywords': matched_words_display,
        'flags': {
            'excessive_caps': excessive_caps,
            'excessive_punct': excessive_punct,
            'has_urls': has_urls
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
