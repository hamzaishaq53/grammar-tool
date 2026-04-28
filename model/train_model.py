# ============================================================
#  Grammar Feedback Tool - Model Training Script    
#
# ============================================================

import pandas as pd
import numpy as np
import pickle
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from scipy.sparse import hstack, csr_matrix

print("=" * 60)
print("   Grammar Feedback Tool  -  Model Training")
print("   BS Computer Science    -  NLP Project")
print("=" * 60)

# ============================================================
# STEP 1: LOAD DATASET WITH PANDAS
# ============================================================
print("\n[STEP 1] Loading dataset with Pandas...")

data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.csv')
df = pd.read_csv(data_path)

print(f"   Total sentences   : {len(df)}")
print(f"   Correct  (1)      : {df[df['label']==1].shape[0]}")
print(f"   Incorrect (0)     : {df[df['label']==0].shape[0]}")

# ============================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================
print("\n[STEP 2] Building linguistic features...")

# Common misspelling patterns in incorrect English
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

# Grammar error patterns
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
    """
    Hand-crafted features that distinguish correct from incorrect text.
    This is Feature Engineering - an important NLP/ML concept.
    """
    result = []
    for text in texts:
        tl = text.lower()
        words = tl.split()
        f = []

        # F1: Ratio of known misspelled words
        mc = sum(1 for w in WRONG_WORDS if w in tl)
        f.append(mc / max(len(words), 1))
        f.append(min(mc, 5))

        # F2: Grammar error pattern count
        gc = sum(1 for p in WRONG_PATTERNS if re.search(p, tl))
        f.append(gc)

        # F3: Average word length
        f.append(np.mean([len(w) for w in words]) if words else 0)

        # F4: Odd plural endings (familys, childrens)
        op = sum(1 for w in words
                 if w.endswith('ys') and len(w) > 4
                 and w not in ['days','says','plays','stays','ways','pays','rays'])
        f.append(op)

        # F5: Repeated letter typos (happpy, beautifull)
        rep = sum(1 for w in words if re.search(r'(.)\1{2,}', w))
        f.append(rep)

        # F6: Consonant cluster typos (mornng, evenng)
        typo = sum(1 for w in words if re.search(r'[^aeiou]{4,}', w))
        f.append(typo)

        # F7: Sentence starts with capital
        f.append(1 if text and text[0].isupper() else 0)

        # F8: Ends with punctuation
        f.append(1 if text and text[-1] in '.!?' else 0)

        result.append(f)
    return np.array(result)

hand_features = extract_features(df['sentence'].tolist())
print(f"   Feature dimensions: {hand_features.shape[1]} linguistic features")

# ============================================================
# STEP 3: TRAIN / TEST SPLIT
# ============================================================
print("\n[STEP 3] Splitting data (80% train / 20% test)...")

X_text = df['sentence']
y      = df['label']

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42, stratify=y
)
train_idx, test_idx = X_train_text.index.tolist(), X_test_text.index.tolist()

X_hand_train = hand_features[train_idx]
X_hand_test  = hand_features[test_idx]

print(f"   Training : {len(X_train_text)}  |  Testing : {len(X_test_text)}")

# ============================================================
# STEP 4: TF-IDF VECTORIZATION (Scikit-learn)
# ============================================================
print("\n[STEP 4] Building TF-IDF features (Scikit-learn)...")

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3), max_features=5000,
    sublinear_tf=True, analyzer='word'
)
vectorizer_char = TfidfVectorizer(
    ngram_range=(2, 5), max_features=5000,
    sublinear_tf=True, analyzer='char_wb'
)

X_tr_word = vectorizer.fit_transform(X_train_text)
X_te_word = vectorizer.transform(X_test_text)
X_tr_char = vectorizer_char.fit_transform(X_train_text)
X_te_char = vectorizer_char.transform(X_test_text)

# Combine: TF-IDF word + TF-IDF char + hand-crafted features
X_train_all = hstack([X_tr_word, X_tr_char, csr_matrix(X_hand_train)])
X_test_all  = hstack([X_te_word, X_te_char, csr_matrix(X_hand_test)])

print(f"   Word TF-IDF features : {len(vectorizer.vocabulary_)}")
print(f"   Char TF-IDF features : {len(vectorizer_char.vocabulary_)}")
print(f"   Linguistic features  : {X_hand_train.shape[1]}")

# ============================================================
# STEP 5: TRAIN LOGISTIC REGRESSION (Scikit-learn)
# ============================================================
print("\n[STEP 5] Training Logistic Regression model...")

model = LogisticRegression(
    max_iter=3000, C=10.0,
    solver='lbfgs', class_weight='balanced', random_state=42
)
model.fit(X_train_all, y_train)

# ============================================================
# STEP 6: EVALUATE
# ============================================================
print("\n[STEP 6] Evaluating model...")

y_pred = model.predict(X_test_all)
acc    = accuracy_score(y_test, y_pred)
cv     = cross_val_score(model, X_train_all, y_train, cv=5)

print(f"   Test Accuracy         : {acc*100:.1f}%")
print(f"   Cross-Validation Avg  : {cv.mean()*100:.1f}%")
print(f"\n{classification_report(y_test, y_pred, target_names=['Incorrect','Correct'])}")

# ============================================================
# STEP 7: SAVE WITH PICKLE
# ============================================================
print("[STEP 7] Saving model with Pickle...")

model_dir = os.path.dirname(__file__)
saves = [
    ('grammar_model.pkl',    model),
    ('vectorizer.pkl',       vectorizer),
    ('vectorizer_char.pkl',  vectorizer_char),
]
for fname, obj in saves:
    path = os.path.join(model_dir, fname)
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    print(f"   Saved: model/{fname}")

print("\n" + "=" * 60)
print(f"   TRAINING COMPLETE!  Accuracy: {acc*100:.1f}%")
print("   Now run:  python app.py")
print("=" * 60 + "\n")
