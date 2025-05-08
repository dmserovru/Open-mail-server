from datetime import datetime
from flask import Blueprint

filters = Blueprint('filters', __name__)

@filters.app_template_filter('time_ago')
def time_ago(dt):
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365}г назад"
    elif diff.days > 30:
        return f"{diff.days // 30}мес назад"
    elif diff.days > 0:
        return f"{diff.days}д назад"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}ч назад"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}мин назад"
    else:
        return "только что"

@filters.app_template_filter('datetime')
def format_datetime(dt):
    return dt.strftime('%d.%m.%Y %H:%M')

@filters.app_template_filter('filesize')
def format_filesize(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB" 