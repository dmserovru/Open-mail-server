from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Email, User, db
from datetime import datetime

mail = Blueprint('mail', __name__)

@mail.route('/inbox')
@login_required
def inbox():
    emails = Email.query.filter_by(recipient=current_user.email).order_by(Email.received_at.desc()).all()
    unread_count = Email.query.filter_by(recipient=current_user.email, read=False).count()
    return render_template('mail/index.html', 
                         emails=emails, 
                         unread_count=unread_count,
                         folder='inbox')

@mail.route('/sent')
@login_required
def sent():
    emails = Email.query.filter_by(sender=current_user.email).order_by(Email.received_at.desc()).all()
    unread_count = Email.query.filter_by(recipient=current_user.email, read=False).count()
    return render_template('mail/index.html', 
                         emails=emails, 
                         unread_count=unread_count,
                         folder='sent')

@mail.route('/drafts')
@login_required
def drafts():
    # Здесь будет логика для черновиков
    return render_template('mail/index.html', 
                         emails=[], 
                         unread_count=0,
                         folder='drafts')

@mail.route('/spam')
@login_required
def spam():
    # Здесь будет логика для спама
    return render_template('mail/index.html', 
                         emails=[], 
                         unread_count=0,
                         folder='spam')

@mail.route('/trash')
@login_required
def trash():
    # Здесь будет логика для корзины
    return render_template('mail/index.html', 
                         emails=[], 
                         unread_count=0,
                         folder='trash')

@mail.route('/view/<int:email_id>')
@login_required
def view_email(email_id):
    email = Email.query.get_or_404(email_id)
    if email.recipient == current_user.email and not email.read:
        email.read = True
        db.session.commit()
    return render_template('mail/view_email.html', email=email)

@mail.route('/send', methods=['POST'])
@login_required
def send_email():
    recipient = request.form.get('to')
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    if not User.query.filter_by(email=recipient).first():
        flash('Получатель не найден')
        return redirect(url_for('mail.inbox'))
    
    email = Email(
        sender=current_user.email,
        recipient=recipient,
        subject=subject,
        body=body,
        received_at=datetime.utcnow()
    )
    
    db.session.add(email)
    db.session.commit()
    
    flash('Письмо отправлено')
    return redirect(url_for('mail.inbox')) 