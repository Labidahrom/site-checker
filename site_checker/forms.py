from django import forms
from site_checker.models import Url


class UrlUpdateForm(forms.ModelForm):
    class Meta:
        model = Url
        fields = [
            'name',
            'expected_title',
            'expected_response_by_http',
            'expected_response_by_https',
            'expected_text'
        ]


class UrlListForm(forms.Form):
    url_string = forms.CharField(
        label='Введите список URL',
        widget=forms.Textarea(
            attrs={'placeholder': 'Вставьте запись вида: "url без протокола'
                                  '||title||код ответа по http||код ответа '
                                  'по https||текст который нужно найти на '
                                  'странице". Данные по каждому url должны '
                                  'начинаться с новой строки'})
    )


class CheckTextForm(forms.Form):
    url_string = forms.CharField(
        label='Введите список значений',
        widget=forms.Textarea(
            attrs={'placeholder': 'Вставьте запись вида: "url c протоколом'
                                  '||текст который должен найтись", например'
                                  ' "https://ya.ru/||Яндекс"'})
    )


class UrlParseListForm(forms.Form):
    url_string = forms.CharField(
        label='Введите список URL',
        widget=forms.Textarea(
            attrs={'placeholder': 'Вставьте список URL, каждый с новой '
                                  'строки'})
    )
    checkbox = forms.BooleanField(label='Добавить данные URL в проверку',
                                  required=False)
