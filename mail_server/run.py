from app import create_app
from config import Config
from app.mail.smtp_server import start_smtp_server
from utils.ssl_gen import generate_self_signed_cert
import subprocess
import sys
import os
import threading

def check_dependencies():
    required = ['flask', 'sqlalchemy', 'ldap3', 'psycopg2-binary', 'flask-login', 'aiosmtpd', 'cryptography']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"Установка необходимых зависимостей...")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + required)
            break

def init_directories():
    dirs = [
        Config.MAILBOX_PATH,
        'logs',
        'ssl'
    ]
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # Генерируем SSL сертификаты если их нет
    cert_path = 'ssl/cert.pem'
    key_path = 'ssl/key.pem'
    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        print("Генерация SSL сертификатов...")
        generate_self_signed_cert(cert_path, key_path)

def main():
    check_dependencies()
    init_directories()
    
    app = create_app()
    
    # Запускаем SMTP сервер в отдельном потоке
    smtp_thread = threading.Thread(target=start_smtp_server, args=(app,))
    smtp_thread.daemon = True
    smtp_thread.start()
    
    # Запускаем веб-приложение
    app.run(host='0.0.0.0', port=5000, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))

if __name__ == '__main__':
    main() 