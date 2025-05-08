from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import User, Email, db
from datetime import datetime, timedelta
import psutil
import os

admin = Blueprint('admin', __name__)

def get_system_stats():
    # Статистика пользователей
    users_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Статистика писем
    today = datetime.now().date()
    today_emails = Email.query.filter(
        db.func.date(Email.received_at) == today
    ).count()
    total_emails = Email.query.count()
    
    # Использование диска
    disk = psutil.disk_usage('/')
    disk_total = disk.total // (1024 * 1024 * 1024)  # GB
    disk_used = disk.used // (1024 * 1024 * 1024)  # GB
    disk_usage = disk.percent
    
    return {
        'users_count': users_count,
        'active_users': active_users,
        'today_emails': today_emails,
        'total_emails': total_emails,
        'disk_total': f"{disk_total}GB",
        'disk_used': f"{disk_used}GB",
        'disk_usage': disk_usage,
        'queue_size': 0,  # Заглушка, нужно реализовать
        'active_deliveries': 0  # Заглушка, нужно реализовать
    }

def get_recent_actions():
    # Здесь будет логика получения последних действий
    return []

def get_system_alerts():
    alerts = []
    
    # Проверка свободного места
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        alerts.append({
            'type': 'danger',
            'title': 'Критически мало места на диске',
            'message': f'Использовано {disk.percent}% дискового пространства'
        })
    
    # Проверка нагрузки системы
    load = psutil.getloadavg()
    if load[0] > psutil.cpu_count() * 0.8:
        alerts.append({
            'type': 'warning',
            'title': 'Высокая нагрузка на систему',
            'message': f'Текущая нагрузка: {load[0]:.1f}'
        })
    
    return alerts

@admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Доступ запрещен')
        return redirect(url_for('mail.inbox'))
    
    return render_template('admin/dashboard.html',
        stats=get_system_stats(),
        recent_actions=get_recent_actions(),
        system_alerts=get_system_alerts()
    )

@admin.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        return redirect(url_for('mail.inbox'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('mail.inbox'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_active = 'is_active' in request.form
        user.is_admin = 'is_admin' in request.form
        
        if request.form.get('password'):
            user.set_password(request.form['password'])
        
        db.session.commit()
        flash('Пользователь обновлен')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin.route('/user/create', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return redirect(url_for('mail.inbox'))
    
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    auth_type = request.form['auth_type']
    is_admin = 'is_admin' in request.form
    
    user = User(
        username=username,
        email=email,
        auth_type=auth_type,
        is_admin=is_admin
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно создан', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при создании пользователя: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin.route('/user/<int:user_id>/delete', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin.route('/domains')
@login_required
def domains():
    if not current_user.is_admin:
        return redirect(url_for('mail.inbox'))
    
    return render_template('admin/domains.html')

@admin.route('/logs')
@login_required
def logs():
    if not current_user.is_admin:
        return redirect(url_for('mail.inbox'))
    
    return render_template('admin/logs.html')

@admin.route('/settings')
@login_required
def settings():
    if not current_user.is_admin:
        return redirect(url_for('mail.inbox'))
    
    return render_template('admin/settings.html') 