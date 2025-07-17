from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.rag_service import RAGService

rag_bp = Blueprint('rag', __name__)

@rag_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query = data['query']
    chat_history = data.get('chat_history', [])
    
    result, status_code = RAGService.process_chat_query(
        user_id=user_id,
        query=query,
        chat_history=chat_history
    )
    
    return jsonify(result), status_code

@rag_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 50, type=int)
    
    result, status_code = RAGService.get_chat_history(user_id, limit)
    return jsonify(result), status_code
