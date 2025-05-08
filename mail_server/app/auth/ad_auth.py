from ldap3 import Server, Connection, NTLM, ALL
from flask import current_app

class ADAuth:
    def __init__(self):
        self.server = Server(current_app.config['AD_SERVER'], get_info=ALL) if current_app.config['AD_SERVER'] else None
        
    def authenticate(self, username, password):
        if not self.server:
            return None
            
        try:
            # Пробуем подключиться с учетными данными пользователя
            user_connection = Connection(
                self.server,
                user=f"{username}@{current_app.config['AD_DOMAIN']}",
                password=password,
                authentication=NTLM
            )
            
            if user_connection.bind():
                # Создаем админское подключение для получения информации о пользователе
                admin_connection = Connection(
                    self.server,
                    user=current_app.config['AD_USERNAME'],
                    password=current_app.config['AD_PASSWORD'],
                    authentication=NTLM
                )
                
                if admin_connection.bind():
                    admin_connection.search(
                        current_app.config['AD_BASE_DN'],
                        f'(sAMAccountName={username})',
                        attributes=['mail', 'displayName']
                    )
                    
                    if admin_connection.entries:
                        user_data = admin_connection.entries[0]
                        return {
                            'username': username,
                            'email': user_data.mail.value if hasattr(user_data, 'mail') else f"{username}@{current_app.config['AD_DOMAIN']}",
                            'display_name': user_data.displayName.value if hasattr(user_data, 'displayName') else username
                        }
            return None
        except Exception as e:
            current_app.logger.error(f"AD Authentication error: {str(e)}")
            return None 