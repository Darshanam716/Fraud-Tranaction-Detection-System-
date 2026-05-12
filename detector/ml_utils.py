import pickle
import numpy as np
from django.conf import settings


_model = None

def get_model():
    global _model
    if _model is None:
        with open(settings.ML_MODEL_PATH, 'rb') as f:
            _model = pickle.load(f)
    return _model


def predict_transaction(features: list) -> dict:
    """
    features: list of 30 floats in order [Time, V1..V28, Amount]
    Returns dict with prediction (0/1), confidence, and label.
    """
    model = get_model()
    X = np.array(features).reshape(1, -1)
    prediction = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]
    confidence = float(proba[prediction]) * 100

    return {
        'prediction': prediction,
        'label': 'FRAUDULENT' if prediction == 1 else 'LEGITIMATE',
        'confidence': round(confidence, 2),
        'fraud_probability': round(float(proba[1]) * 100, 2),
        'legit_probability': round(float(proba[0]) * 100, 2),
    }
