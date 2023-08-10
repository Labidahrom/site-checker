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
            attrs={'placeholder': 'example.com||title||код ответа по '
                                  'http||код ответа по https||текст который'
                                  ' нужно найти на странице'})
    )


class CheckTextForm(forms.Form):
    url_string = forms.CharField(
        label='Введите список значений',
        widget=forms.Textarea(
            attrs={'placeholder': 'https://example.com||текст который должен'
                                  ' найтись'})
    )


class UrlParseListForm(forms.Form):
    url_string = forms.CharField(
        label='Введите список URL',
        widget=forms.Textarea(
            attrs={'placeholder': 'example.com'})
    )
    checkbox = forms.BooleanField(label='Сохранить результат в списке url',
                                  required=False)
