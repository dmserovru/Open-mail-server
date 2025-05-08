from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # Основные настройки
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///mailserver.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Active Directory
    AD_SERVER = os.getenv('AD_SERVER')
    AD_DOMAIN = os.getenv('AD_DOMAIN')
    AD_BASE_DN = os.getenv('AD_BASE_DN')
    AD_USERNAME = os.getenv('AD_USERNAME')
    AD_PASSWORD = os.getenv('AD_PASSWORD')
    
    # SMTP настройки
    SMTP_HOST = os.getenv('SMTP_HOST', '127.0.0.1')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 2525))
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    
    # Пути
    MAILBOX_PATH = os.getenv('MAILBOX_PATH', './mailboxes')
    MAX_MAILBOX_SIZE = int(os.getenv('MAX_MAILBOX_SIZE', 1024 * 1024 * 1024))  # 1GB по умолчанию 