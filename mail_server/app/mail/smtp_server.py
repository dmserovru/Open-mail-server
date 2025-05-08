import asyncio
from aiosmtpd.controller import Controller
from email.message import EmailMessage
from email.parser import Parser
from ..models import db, User, Email
from datetime import datetime
import socket
import time

class CustomHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not User.query.filter_by(email=address).first():
            return '550 Recipient not found'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        parser = Parser()
        msg = parser.parsestr(envelope.content.decode())
        
        email = Email(
            sender=envelope.mail_from,
            recipient=envelope.rcpt_tos[0],
            subject=msg.get('subject', ''),
            body=envelope.content.decode(),
            received_at=datetime.utcnow()
        )
        
        db.session.add(email)
        db.session.commit()
        
        return '250 Message accepted'

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True

def start_smtp_server(app):
    with app.app_context():
        # Пробуем разные порты, начиная с базового
        base_port = app.config['SMTP_PORT']
        port = base_port
        
        # Пробуем порты в диапазоне base_port до base_port + 10
        while port < base_port + 10:
            if not is_port_in_use(port):
                try:
                    controller = Controller(
                        CustomHandler(), 
                        hostname='127.0.0.1',
                        port=port
                    )
                    print(f"SMTP сервер запущен на порту {port}")
                    controller.start()
                    break
                except OSError as e:
                    print(f"Ошибка при запуске SMTP сервера на порту {port}: {e}")
            port += 1
            time.sleep(1)  # Небольшая задержка между попытками
        
        if port >= base_port + 10:
            print("Не удалось найти свободный порт для SMTP сервера") 