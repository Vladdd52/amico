import os
import sys

# Добавляем путь к проекту в систему
sys.path.insert(0, os.path.dirname(__file__))

# Указываем Django, где лежат настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amico.settings')

# Импортируем WSGI-приложение Django
from amico.wsgi import application
