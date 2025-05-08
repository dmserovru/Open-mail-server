from flask import Flask, redirect, url_for
from flask_login import LoginManager
from .models import db, User
from .api.routes import api
from .auth.routes import auth
from .mail.routes import mail
from config import Config
from .utils.filters import filters

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    
    # Настройка login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    # Регистрация blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(mail, url_prefix='/mail')
    app.register_blueprint(filters)
    
    # Корневой маршрут
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    with app.app_context():
        # Удаляем все таблицы и создаем заново
        db.drop_all()
        db.create_all()
        
        # Создание админа если его нет
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@localhost',
                is_admin=True,
                auth_type='local'
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
    
    return app 