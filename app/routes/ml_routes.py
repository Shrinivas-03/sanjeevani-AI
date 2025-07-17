from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ml_service import MLService

ml_bp = Blueprint('ml', __name__)
ml_service = MLService()

@ml_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict_disease():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'symptoms' not in data:
        return jsonify({'error': 'Symptoms are required'}), 400
    
    symptoms = data['symptoms']
    
    if not isinstance(symptoms, list) or not symptoms:
        return jsonify({'error': 'Symptoms must be a non-empty list'}), 400
    
    result, status_code = ml_service.predict_disease(symptoms)
    return jsonify(result), status_code

@ml_bp.route('/symptoms', methods=['GET'])
def get_available_symptoms():
    # Return list of available symptoms for the frontend
    symptoms = [
        'fever', 'cough', 'headache', 'fatigue', 'nausea', 'vomiting',
        'diarrhea', 'abdominal_pain', 'chest_pain', 'shortness_of_breath',
        'dizziness', 'muscle_pain', 'joint_pain', 'rash', 'sore_throat'
    ]
    
    return jsonify({
        'symptoms': symptoms,
        'message': 'Available symptoms retrieved successfully'
    }), 200
