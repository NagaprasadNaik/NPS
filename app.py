from flask import Flask, request, jsonify, render_template, send_from_directory
import joblib
import numpy as np
import numpy as np
import string
from flask_cors import CORS
import os



# Load trained model and scaler
model = joblib.load("domain_model.pkl")
scaler = joblib.load("domain_scaler.pkl")

app = Flask(__name__)
CORS(app)

def extract_domain_features(domain):
    domain = domain.lower()
    length = len(domain)
    digits = [c for c in domain if c.isdigit()]
    unique_digits = set(digits)
    chars = [c for c in domain if c.isalpha()]
    unique_chars = set(chars)
    alnum = [c for c in domain if c.isalnum()]
    consonants = [c for c in domain if c.isalpha() and c not in 'aeiou']
    symbols = [c for c in domain if c in string.punctuation and c not in ['.', '_']]
    
    features = [
        length,
        len(digits),
        len(unique_digits),
        len(chars),
        len(unique_chars),
        len(symbols),
        len([c for c in domain if c in 'aeiou']),
        len(consonants),
        len(alnum),
        domain.count('.'),
        domain.count('_'),
        len(set(domain)),
        len(chars) / length if length else 0,
        len(unique_chars) / length if length else 0,
        len(unique_chars) / len(set(domain)) if len(set(domain)) else 0,
        len(unique_digits) / len(set(domain)) if len(set(domain)) else 0,
        len(set(chars)) / len(set(domain)) if len(set(domain)) else 0
    ]
    return np.array(features)



@app.route('/')
def home():
    return "✅ Domain Detection API is running."

@app.route('/web')
def web_interface():
    return render_template('index.html')

@app.route('/rv.png')
def serve_logo():
    return send_from_directory('templates', 'rv.png')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        domain = request.json["domain"]
        features = extract_domain_features(domain).reshape(1, -1)
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        label = "malicious" if prediction == 1 else "safe"
        return jsonify({"domain": domain, "prediction": int(prediction), "label": label})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
