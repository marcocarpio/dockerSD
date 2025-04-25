from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.api.models.user import User
from app.api.utils.security import hash_password, verify_password
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({'message': 'Login successful'})
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    token = jwt.encode({
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Password reset link sent', 'token': token}), 200

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400

    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.filter_by(username=payload['username']).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({'message': 'Password reset successful'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 400
