from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views import View
from site_checker.models import Url, Check, LastParse, TextCheckData
from site_checker import forms
from site_checker.modules.parser import add_urls_data_to_db, prepare_urls_data, \
    add_check_urls_data_to_db, add_text_check_data_to_db, add_prepared_urls_data_to_db


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
        form = forms.UrlListForm()
        return render(request, 'create_urls.html', {'form': form})

    def post(self, request, *args, **kwargs):
        url_string = request.POST.get('url_string', '')
        add_urls_data_to_db(url_string)
        return render(request, 'index.html')


class UpdateUrl(UpdateView):
    form_class = forms.UrlUpdateForm
    model = Url
    template_name = 'update_url.html'
    success_url = reverse_lazy('url_list')


class DeleteUrl(DeleteView):
    model = Url
    template_name = 'delete_url.html'
    success_url = reverse_lazy('url_list')


class PrepareUrlsData(View):
    def get(self, request, *args, **kwargs):
        form = forms.UrlParseListForm()
        return render(request, 'parse_urls.html', {'form': form})

    def post(self, request, *args, **kwargs):
        url_strings = request.POST.get('url_string', '')
        check_box = request.POST.get('checkbox', '')
        add_prepared_urls_data_to_db(check_box, url_strings)

        return render(request, 'index.html')


class PreparedUrlsList(ListView):
    model = LastParse
    template_name = 'parse_urls_list.html'
    context_object_name = 'parse_urls_data'

    def get_object(self):
        return LastParse.objects.first()


class UrlsList(ListView):
    model = Url
    template_name = 'urls_list.html'
    context_object_name = 'urls'


class ChecksList(ListView):
    model = Check
    template_name = 'checks_list.html'
    context_object_name = 'checks'


class CheckUrl(View):
    def post(self, request, *args, **kwargs):
        add_check_urls_data_to_db()
        return redirect('checks_list')


class CheckText(View):
    def get(self, request, *args, **kwargs):
        form = forms.CheckTextForm()
        return render(request, 'check_text.html', {'form': form})

    def post(self, request, *args, **kwargs):
        text_string = request.POST.get('url_string', '')
        add_text_check_data_to_db(text_string)
        return render(request, 'index.html')


class CheckTextList(ListView):
    model = TextCheckData
    template_name = 'text_check_list.html'
    context_object_name = 'text_check_data'

    def get_object(self):
        return TextCheckData.objects.first()