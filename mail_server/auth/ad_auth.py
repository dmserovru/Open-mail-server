from ldap3 import Server, Connection, NTLM, ALL
from flask import current_app

class ADAuth:
    def __init__(self, config):
        self.server = Server(config.AD_SERVER, get_info=ALL)
        self.admin_connection = Connection(
            self.server,
            user=config.AD_USERNAME,
            password=config.AD_PASSWORD,
            authentication=NTLM
        )
    
    def authenticate(self, username, password):
        try:
            # Пробуем подключиться с учетными данными пользователя
            user_connection = Connection(
                self.server,
                user=f"{username}@{current_app.config['AD_DOMAIN']}",
                password=password,
                authentication=NTLM
            )
            
            if user_connection.bind():
                # Получаем информацию о пользователе
                self.admin_connection.search(
                    current_app.config['AD_BASE_DN'],
                    f'(sAMAccountName={username})',
                    attributes=['mail', 'displayName']
                )
                
                if self.admin_connection.entries:
                    user_data = self.admin_connection.entries[0]
                    return {
                        'username': username,
                        'email': user_data.mail.value,
                        'display_name': user_data.displayName.value
                    }
            return None
        except Exception as e:
            current_app.logger.error(f"AD Authentication error: {str(e)}")
            return None 