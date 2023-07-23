from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views import View
from site_checker.models import Url, Check, LastParse
from site_checker.modules.parser import make_url_check, parse_url
import re
from django import forms


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
        widget=forms.Textarea(attrs={'placeholder': 'Вставьте запись вида: url без протокола'
                                                    '||title||код ответа по http||код ответа '
                                                    'по https||текст который нужно найти на '
                                                    'странице. Данные по каждому url должны'
                                                    'начинаться с новой строки'})
    )


class UrlParseListForm(forms.Form):
    url_string = forms.CharField(
        label='Введите список URL',
        widget=forms.Textarea(attrs={'placeholder': 'Вставьте список URL, каждый с новой строки'})
    )
    checkbox = forms.BooleanField(label='Добавить данные URL в проверку', required=False)


def make_status_data(url, check_data):
    status_field = ''
    if url.expected_title != check_data['title']:
        status_field += f'Title не совпадает, фактический результат: {check_data["title"]}. '
    if url.expected_response_by_http != check_data['actual_response_by_http']:
        status_field += f'Http ответ не совпадает, фактический результат: {check_data["actual_response_by_http"]}. '
    if url.expected_response_by_https != check_data['actual_response_by_https']:
        status_field += f'Https ответ не совпадает, фактический результат: {check_data["actual_response_by_https"]}. '
    if not check_data['has_expected_text']:
        status_field += 'Проверочный текст на странице не найден. '
    if not status_field:
        status_field = 'ok'
    return status_field


def validate_url_data(string):
    pattern = r'^(?!.*http(s)?://)[^|]+(\|\|[^|]+){4}$'
    return bool(re.match(pattern, string))


def parse_url_string(url_string):
    url_data = url_string.split('||')
    return {
        'name': url_data[0],
        'expected_title': url_data[1],
        'expected_response_by_http': int(url_data[2]),
        'expected_response_by_https': int(url_data[3]),
        'expected_text': url_data[4],
    }


def add_urls_data(url_strings):
    url_list = url_strings.split('\n')
    for i in url_list:
        if not validate_url_data(i):
            continue
        url_data = parse_url_string(i)
        Url.objects.create(**url_data)


def parse_urls(url_strings):
    url_list = url_strings.split('\n')
    parse_result = ''
    for i in url_list:
        i = i.strip('\r')
        parse_result += (f'{i}{parse_url(i)}\n')
    return parse_result


def index(request):
    return render(request, 'index.html')


class LoginUser(SuccessMessageMixin, LoginView):
    template_name = 'login_user.html'
    next_page = reverse_lazy('index')
    success_message = _('You logged in')
    form_class = AuthenticationForm


class LogoutUser(LogoutView):
    template_name = 'index.html'
    next_page = reverse_lazy('index')


class CreateUrls(View):
    def get(self, request, *args, **kwargs):
        form = UrlListForm()
        return render(request, 'create_urls.html', {'form': form})

    def post(self, request, *args, **kwargs):
        url_string = request.POST.get('url_string', '')
        add_urls_data(url_string)
        return render(request, 'index.html')


class UpdateUrl(UpdateView):
    form_class = UrlUpdateForm
    model = Url
    template_name = 'update_url.html'
    success_url = reverse_lazy('url_list')


class DeleteUrl(DeleteView):
    model = Url
    template_name = 'delete_url.html'
    success_url = reverse_lazy('url_list')


class ParseUrls(View):
    def get(self, request, *args, **kwargs):
        form = UrlParseListForm()
        return render(request, 'parse_urls.html', {'form': form})

    def post(self, request, *args, **kwargs):
        url_strings = request.POST.get('url_string', '')
        check_box = request.POST.get('checkbox', '')
        urls_data = parse_urls(url_strings)
        if check_box:
            add_urls_data(urls_data)
        LastParse.objects.create(parse_data=urls_data)

        return render(request, 'parse_urls_list.html', {'urls_data': urls_data})


class UrlsList(ListView):
    model = Url
    template_name = 'urls_list.html'
    context_object_name = 'urls'


class ParsedUrlsList(ListView):
    model = LastParse
    template_name = 'parse_urls_list.html'
    context_object_name = 'parse_urls_data'

    def get_object(self):
        return LastParse.objects.first()


class ChecksList(ListView):
    model = Check
    template_name = 'checks_list.html'
    context_object_name = 'checks'


class CheckUrl(View):
    def post(self, request, *args, **kwargs):
        urls_list = Url.objects.all()
        for url in urls_list:
            check_data = make_url_check(url)
            if not check_data:
                continue
            Check.objects.create(
                url_name=url,
                has_expected_title=check_data['title'] == url.expected_title,
                actual_response_by_http=check_data['actual_response_by_http'],
                actual_response_by_https=check_data['actual_response_by_https'],
                has_expected_text=check_data['has_expected_text']
            )
            status_string = make_status_data(url, check_data)

            if url.check_details != status_string:
                url_entry = Url.objects.get(id=url.id)
                url_entry.check_details = status_string
                url_entry.save()

        return redirect('checks_list')
