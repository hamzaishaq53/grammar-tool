# ============================================================
#  Grammar Feedback Tool - Flask Backend

#     python app.py
#     Then open browser: http://127.0.0.1:5000
# ============================================================

from flask import Flask, render_template, request, jsonify
import pickle
import re
import os
import numpy as np
from spellchecker import SpellChecker
from scipy.sparse import hstack, csr_matrix

app   = Flask(__name__)
spell = SpellChecker()

# ============================================================
# FEATURE ENGINEERING (same as train_model.py - MUST match)
# ============================================================

WRONG_WORDS = [
    'goed','buyed','runned','drived','plaied','readed','writed',
    'helpped','submited','completted','celebratted','enjoyied',
    'beautifull','delicous','intresting','succesfull','succesfully',
    'excelent','diffcult','pleasent','dedicatted','hardworkng',
    'universty','librery','markit','stashun','tomorow','tonights',
    'mornng','evenng','afternon','weekends','familys','childrens',
    'proyect','laptob','computor','proffesor','docter','goverment',
    'compeny','intervew','confedence','experince','developement',
    'artficail','inteligence','algorythms','competetion','presentashun',
    'smartfone','fetures','sience','theary','polcy','educashun',
    'programes','enginering','examinashuns','resultes','trane',
    'problam','quickely','organizd','cleanned','doneted','winned',
    'builded','prepard','attendd','launche','honests','hapy',
    'happpy','clearely','delcious','wether','thier','freind',
    'recieved','beleive','occured','neccessary','accidentaly'
]

WRONG_PATTERNS = [
    r'\b(he|she|it)\s+are\b',
    r'\b(he|she|it)\s+were\b(?!\s+\w+ing)',
    r'\b(they|we|you)\s+is\b',
    r'\b(i)\s+are\b',
    r'\bam\s+go\b',
    r'\bwill\s+visited\b',
    r'\bwill\s+finishes\b',
    r'\bare\s+(run|play|sleep|go|come)\b',
    r'\ba\s+[aeiou]\w{2,}\b',
]

def extract_features(texts):
    result = []
    for text in texts:
        tl = text.lower()
        words = tl.split()
        f = []
        mc = sum(1 for w in WRONG_WORDS if w in tl)
        f.append(mc / max(len(words), 1))
        f.append(min(mc, 5))
        gc = sum(1 for p in WRONG_PATTERNS if re.search(p, tl))
        f.append(gc)
        f.append(np.mean([len(w) for w in words]) if words else 0)
        op = sum(1 for w in words if w.endswith('ys') and len(w) > 4
                 and w not in ['days','says','plays','stays','ways','pays','rays'])
        f.append(op)
        rep = sum(1 for w in words if re.search(r'(.)\1{2,}', w))
        f.append(rep)
        typo = sum(1 for w in words if re.search(r'[^aeiou]{4,}', w))
        f.append(typo)
        f.append(1 if text and text[0].isupper() else 0)
        f.append(1 if text and text[-1] in '.!?' else 0)
        result.append(f)
    return np.array(result)

# ============================================================
# LOAD MODEL (Pickle)
# ============================================================
MODEL_PATH = os.path.join('model', 'grammar_model.pkl')
VEC_PATH   = os.path.join('model', 'vectorizer.pkl')
CHAR_PATH  = os.path.join('model', 'vectorizer_char.pkl')

try:
    with open(MODEL_PATH, 'rb') as f: model          = pickle.load(f)
    with open(VEC_PATH,   'rb') as f: vectorizer      = pickle.load(f)
    with open(CHAR_PATH,  'rb') as f: vectorizer_char = pickle.load(f)
    print("[OK] ML Model & Vectorizers loaded successfully.")
except FileNotFoundError:
    print("[ERROR] Model not found! Run: python model/train_model.py")
    model = vectorizer = vectorizer_char = None

# ============================================================
# HELPER: ML PREDICTION
# ============================================================
def ml_predict(text):
    if model is None:
        return None
    hand  = csr_matrix(extract_features([text]))
    word  = vectorizer.transform([text])
    char  = vectorizer_char.transform([text])
    vec   = hstack([word, char, hand])
    pred  = int(model.predict(vec)[0])
    proba = model.predict_proba(vec)[0]
    return {
        'prediction' : pred,
        'label'      : 'Grammatically Acceptable' if pred == 1 else 'Grammatically Questionable',
        'confidence' : round(float(max(proba)) * 100, 1)
    }

# ============================================================
# HELPER: SPELL CHECK
# ============================================================
def check_spelling(text):
    raw   = re.findall(r"\b[a-zA-Z']+\b", text)
    words = [w for w in raw if len(w) > 2 and w.lower() not in {
        'the','and','for','are','was','were','has','had','have',
        'its','you','your','our','their','there','they','this',
        'that','with','from','not','but','can','will','been',
        'him','her','his','she','who','did','let','all','one',
        'than','then','too','very','just','now','may','any',
        'also','each','when','what','some','into','how','own',
        'use','get','new','day','two','way','see','out','did'
    }]
    misspelled = spell.unknown(words)
    errors = []
    for word in misspelled:
        correction = spell.correction(word)
        candidates = list(spell.candidates(word) or [])[:4]
        errors.append({
            'word'       : word,
            'suggestion' : correction if correction else 'No suggestion',
            'candidates' : candidates
        })
    return errors

# ============================================================
# HELPER: GRAMMAR RULES
# ============================================================
def check_grammar_rules(text):
    issues = []

    if re.search(r"\b(don't|doesn't|didn't|won't|can't|isn't|aren't|haven't|hadn't|wouldn't|couldn't|shouldn't)\b.{0,50}\b(nothing|nobody|nowhere|never|no\s+one|none)\b", text, re.IGNORECASE):
        issues.append({'type': 'Double Negative', 'message': "Double negative detected. Use only ONE negative in a sentence.", 'example': 'Wrong: "I don\'t know nothing." → Correct: "I don\'t know anything."'})

    if re.search(r"\b(he|she|it)\s+(are|were)\b", text, re.IGNORECASE):
        issues.append({'type': 'Subject-Verb Agreement', 'message': "'he/she/it' must use 'is/was', not 'are/were'.", 'example': 'Wrong: "He are happy." → Correct: "He is happy."'})

    if re.search(r"\b(they|we|you)\s+is\b", text, re.IGNORECASE):
        issues.append({'type': 'Subject-Verb Agreement', 'message': "'they/we/you' must use 'are', not 'is'.", 'example': 'Wrong: "They is coming." → Correct: "They are coming."'})

    if re.search(r"\ba\s+[aeiouAEIOU]\w{2,}", text):
        issues.append({'type': 'Article Error', 'message': "Use 'an' before words starting with a vowel sound.", 'example': 'Wrong: "a apple" → Correct: "an apple"'})

    if re.search(r"\ban\s+[^aeiouAEIOU\s\d]\w{2,}", text, re.IGNORECASE):
        issues.append({'type': 'Article Error', 'message': "Use 'a' before words starting with a consonant sound.", 'example': 'Wrong: "an book" → Correct: "a book"'})

    words_lower = text.lower().split()
    for i in range(len(words_lower) - 1):
        if words_lower[i] == words_lower[i+1] and words_lower[i].isalpha() and len(words_lower[i]) > 2:
            issues.append({'type': 'Repeated Word', 'message': f"Word '{words_lower[i]}' appears twice in a row.", 'example': f'Remove the extra "{words_lower[i]}".'})
            break

    for sent in re.split(r'(?<=[.!?])\s+', text.strip()):
        s = sent.strip()
        if s and s[0].islower() and len(s) > 3:
            issues.append({'type': 'Capitalization', 'message': 'Every sentence must start with a capital letter.', 'example': f'Capitalize: "{s[:25]}..."'})
            break

    if re.search(r'\s{2,}', text):
        issues.append({'type': 'Extra Spaces', 'message': 'Multiple consecutive spaces found.', 'example': 'Remove extra spaces between words.'})

    if re.search(r"\byour\s+(is|are|was|were|going|coming|doing)\b", text, re.IGNORECASE):
        issues.append({'type': 'Wrong Word', 'message': "Misuse of 'your'. Did you mean 'you're' (you are)?", 'example': 'Wrong: "your going" → Correct: "you\'re going"'})

    if re.search(r'[.!?,]{3,}', text):
        issues.append({'type': 'Punctuation', 'message': 'Avoid using multiple punctuation marks together.', 'example': 'Use just one punctuation mark at sentence end.'})

    return issues

# ============================================================
# HELPER: SCORE & GRADE
# ============================================================
def compute_score(spell_errors, gram_issues, ml_pred):
    score  = 100
    score -= len(spell_errors) * 8
    score -= len(gram_issues)  * 12
    if ml_pred is not None and ml_pred['prediction'] == 0:
        score -= 15
    return max(0, min(100, score))

def get_grade(score):
    if score >= 90: return ('Excellent ✨', '#22c55e', '🟢')
    if score >= 75: return ('Good 👍',      '#3b82f6', '🔵')
    if score >= 60: return ('Fair 📝',      '#f59e0b', '🟡')
    return              ('Needs Work ⚠️', '#ef4444', '🔴')

# ============================================================
# ROUTES
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if model is None:
        return jsonify({'error': 'Model not loaded. Run: python model/train_model.py'}), 500

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided.'}), 400

    text = data['text'].strip()
    if len(text) < 3:
        return jsonify({'error': 'Text is too short. Enter at least 3 characters.'}), 400
    if len(text) > 2000:
        return jsonify({'error': 'Text too long. Max 2000 characters.'}), 400

    spell_errors = check_spelling(text)
    gram_issues  = check_grammar_rules(text)
    ml           = ml_predict(text)
    score        = compute_score(spell_errors, gram_issues, ml)
    grade, color, dot = get_grade(score)

    words     = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

    return jsonify({
        'score'          : score,
        'grade'          : grade,
        'grade_color'    : color,
        'grade_dot'      : dot,
        'spelling_errors': spell_errors,
        'grammar_issues' : gram_issues,
        'ml_label'       : ml['label'] if ml else 'N/A',
        'ml_confidence'  : ml['confidence'] if ml else 0,
        'word_count'     : len(words),
        'char_count'     : len(text),
        'sentence_count' : len(sentences),
        'avg_word_len'   : round(sum(len(w) for w in words) / max(len(words), 1), 1),
        'error_count'    : len(spell_errors) + len(gram_issues)
    })

@app.route('/examples', methods=['GET'])
def examples():
    return jsonify({
        'correct'  : [
            "She has been studying computer science for three years.",
            "The students submitted their assignments on time.",
            "Mathematics is an important subject for engineers."
        ],
        'incorrect': [
            "He don't know nothing about the project.",
            "She goed to the store and buyed a apple.",
            "They was playing when the teacher are came."
        ]
    })

# ============================================================
# START SERVER
# ============================================================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Grammar Feedback Tool - Flask Server")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
