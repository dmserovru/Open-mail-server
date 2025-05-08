from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db
from .ad_auth import ADAuth

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mail.inbox'))
        
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.auth_type == 'local':
            if user.check_password(data['password']):
                login_user(user)
                return redirect(url_for('mail.inbox'))
        elif user and user.auth_type == 'ad':
            ad_auth = ADAuth(current_app.config)
            if ad_auth.authenticate(data['username'], data['password']):
                login_user(user)
                return redirect(url_for('mail.inbox'))
                
        flash('Неверное имя пользователя или пароль')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        user = User(
            username=data['username'],
            email=data['email'],
            auth_type='local'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('mail.inbox'))
        
    return render_template('register.html')

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Обработка изменения настроек
        if 'password' in request.form:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                db.session.commit()
                flash('Пароль успешно изменен', 'success')
            else:
                flash('Неверный текущий пароль', 'error')
                
        # Другие настройки
        current_user.email_signature = request.form.get('email_signature', '')
        current_user.notifications_enabled = 'notifications_enabled' in request.form
        db.session.commit()
        flash('Настройки сохранены', 'success')
        
    return render_template('auth/settings.html') 