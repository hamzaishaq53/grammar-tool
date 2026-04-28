# Grammar & Spelling Feedback Tool

---

## PROJECT STRUCTURE

```
grammar_tool/
│
├── app.py                    ← STEP 2: Run this (Flask server)
├── requirements.txt          ← Libraries list
├── README.md                 ← This file
│
├── model/
│   ├── train_model.py        ← STEP 1: Run this FIRST
│   ├── grammar_model.pkl     ← Created after training
│   ├── vectorizer.pkl        ← Created after training
│   └── vectorizer_char.pkl   ← Created after training
│
├── data/
│   └── dataset.csv           ← 140 training sentences
│
├── templates/
│   └── index.html            ← Web page
│
└── static/
    ├── css/style.css         ← Styling
    └── js/main.js            ← Frontend logic
```

---

## TECH STACK

| Tool         | Purpose                              |
|--------------|--------------------------------------|
| Python       | Main programming language            |
| Flask        | Web server / Backend API             |
| Scikit-learn | TF-IDF + Logistic Regression (ML)    |
| Pandas       | Load and manage dataset              |
| Pickle       | Save and load trained model          |
| pyspellchecker | Spell checking                     |
| scipy        | Sparse matrix operations             |

---

## HOW TO RUN

### Step 1 — Install libraries (run once)
```
pip install flask scikit-learn pandas numpy pyspellchecker scipy
```

### Step 2 — Train the ML model (run once)
```
python model/train_model.py
```
Wait for "TRAINING COMPLETE!" — accuracy will show ~89%

### Step 3 — Start the server
```
python app.py
```

### Step 4 — Open in browser
```
http://127.0.0.1:5000
```

---

## NLP TOPICS COVERED

1. TF-IDF Vectorization (Scikit-learn)
2. Logistic Regression Classification (Scikit-learn)
3. Feature Engineering (linguistic features)
4. Spell Checking (pyspellchecker)
5. Grammar Rule Detection (regex patterns)
6. Text Scoring & Grading

---

*Project: [Your Name] | Roll No: [Your Roll No] | NLP — 6th Semester*
