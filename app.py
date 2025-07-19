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
def web_interface():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/rv.png')
def serve_logo():
    return send_from_directory('templates', 'rv.png')

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('templates', 'logo.avif', mimetype='image/avif')

@app.route('/logo.avif')
def serve_logo_avif():
    return send_from_directory('templates', 'logo.avif')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        domain = request.json["domain"]
        features = extract_domain_features(domain).reshape(1, -1)
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        
        # Add prediction probability for confidence
        prediction_proba = model.predict_proba(features_scaled)[0]
        confidence = float(max(prediction_proba))
        
        label = "malicious" if prediction == 1 else "safe"
        
        # Store prediction history for analytics
        from time import time
        prediction_data = {
            "domain": domain,
            "prediction": int(prediction),
            "label": label,
            "confidence": confidence,
            "timestamp": time()
        }
        prediction_history.append(prediction_data)
        
        # Keep only last 1000 predictions to avoid memory issues
        if len(prediction_history) > 1000:
            prediction_history.pop(0)
        
        return jsonify(prediction_data)
    except Exception as e:
        return jsonify({"error": str(e)})

# Security Analytics - Track predictions for dashboard
prediction_history = []

@app.route('/security-analytics', methods=['GET'])
def get_security_analytics():
    """Get security analytics for dashboard"""
    try:
        total_predictions = len(prediction_history)
        malicious_count = sum(1 for p in prediction_history if p['prediction'] == 1)
        safe_count = total_predictions - malicious_count
        
        # Get recent predictions (last 20)
        recent_predictions = prediction_history[-20:] if len(prediction_history) >= 20 else prediction_history
        
        return jsonify({
            'total_analyzed': total_predictions,
            'malicious_domains': malicious_count,
            'safe_domains': safe_count,
            'threat_percentage': (malicious_count / total_predictions * 100) if total_predictions > 0 else 0,
            'recent_predictions': recent_predictions
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/threat-feed', methods=['GET'])
def get_threat_feed():
    """Get live threat feed"""
    try:
        # Get only malicious predictions
        threats = [p for p in prediction_history if p['prediction'] == 1]
        # Sort by timestamp (newest first)
        threats.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(threats[:10])  # Return last 10 threats
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
