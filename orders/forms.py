import re
from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        # Убираем пробелы и дефисы для гибкости
        phone_clean = re.sub(r'[\s\-]', '', phone)
        # Принимаем форматы: +998XXXXXXXXX или 998XXXXXXXXX или 0XXXXXXXXX
        pattern = r'^(\+998|998|0)\d{9}$'
        if not re.match(pattern, phone_clean):
            raise forms.ValidationError(
                'Введите корректный номер телефона. Пример: +998919998877'
            )
        # Приводим к единому формату +998XXXXXXXXX
        if phone_clean.startswith('0'):
            phone_clean = '+998' + phone_clean[1:]
        elif phone_clean.startswith('998'):
            phone_clean = '+' + phone_clean
        return phone_clean