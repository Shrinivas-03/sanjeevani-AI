import joblib
import numpy as np
from typing import List, Dict

class MLService:
    def __init__(self):
        # Load pre-trained model (adjust path as needed)
        try:
            # self.model = joblib.load('models/disease_prediction_model.pkl')
            # self.symptom_encoder = joblib.load('models/symptom_encoder.pkl')
            # For now, use mock model
            self.model = None
            self.symptom_encoder = None
        except:
            self.model = None
            self.symptom_encoder = None
    
    def predict_disease(self, symptoms: List[str]) -> Dict:
        try:
            if not symptoms:
                return {'error': 'No symptoms provided'}, 400
            
            # Mock prediction - replace with actual model inference
            if self.model is None:
                return self._mock_prediction(symptoms)
            
            # Actual model prediction would go here
            # encoded_symptoms = self.symptom_encoder.transform(symptoms)
            # prediction = self.model.predict(encoded_symptoms)
            # probability = self.model.predict_proba(encoded_symptoms)
            
            return self._mock_prediction(symptoms)
            
        except Exception as e:
            return {'error': 'Prediction failed'}, 500
    
    def _mock_prediction(self, symptoms: List[str]) -> tuple:
        # Mock prediction logic
        symptom_disease_map = {
            'fever': ['Common Cold', 'Flu', 'Viral Infection'],
            'cough': ['Common Cold', 'Bronchitis', 'Pneumonia'],
            'headache': ['Migraine', 'Tension Headache', 'Sinusitis'],
            'fatigue': ['Anemia', 'Depression', 'Chronic Fatigue'],
            'nausea': ['Food Poisoning', 'Gastritis', 'Motion Sickness']
        }
        
        possible_diseases = set()
        for symptom in symptoms:
            if symptom.lower() in symptom_disease_map:
                possible_diseases.update(symptom_disease_map[symptom.lower()])
        
        if not possible_diseases:
            possible_diseases = ['General Consultation Recommended']
        
        predictions = []
        for i, disease in enumerate(list(possible_diseases)[:3]):
            confidence = max(0.3, 0.9 - (i * 0.2))
            predictions.append({
                'disease': disease,
                'confidence': round(confidence, 2)
            })
        
        return {
            'predictions': predictions,
            'symptoms_analyzed': symptoms,
            'disclaimer': 'This is a preliminary assessment. Please consult a healthcare professional for proper diagnosis.'
        }, 200
