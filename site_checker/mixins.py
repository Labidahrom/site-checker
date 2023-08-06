from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.mixins import AccessMixin
from django.utils.translation import gettext as _


class LoginRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('You are not logged in'))
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)


class UserRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if user_id != request.user.id:
            messages.warning(request, self.permission_denied_message)
            return redirect(reverse('users_list'))
        return super().dispatch(request, *args, **kwargs)
