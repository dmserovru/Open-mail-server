from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import db, User, Mailbox
from ..auth.ad_auth import ADAuth

api = Blueprint('api', __name__)

@api.route('/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return jsonify({'error': 'Недостаточно прав'}), 403
        
    data = request.get_json()
    
    user = User(
        username=data['username'],
        email=data['email'],
        auth_type=data.get('auth_type', 'local')
    )
    
    if user.auth_type == 'local':
        user.set_password(data['password'])
    
    db.session.add(user)
    
    # Создаем почтовый ящик для пользователя
    mailbox = Mailbox(
        user=user,
        path=f"/var/mail/{user.email}",
        quota=1024 * 1024 * 1024  # 1GB по умолчанию
    )
    
    db.session.add(mailbox)
    db.session.commit()
    
    return jsonify({'message': 'Пользователь успешно создан'}), 201 