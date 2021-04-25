from django.template.defaultfilters import register
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout

from App.UsernameBackEnd import UsernameBackEnd
from App.forms import PasswordResetForm, SetPasswordForm
from API import models
from django.urls import reverse
from django.http import HttpResponseRedirect

from FaceAPI.FireBase import StorageImage
from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (get_user_model, login as auth_login)
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import (urlsafe_base64_decode)
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views import View

UserModel = get_user_model()

def ShowLoginPage(request):
    if request.user != None:
        if request.user.is_active == True:
            login(request, request.user)
            if request.user.user_type == "1":
                return HttpResponseRedirect(reverse("AdminPage"))
            elif request.user.user_type == "2":
                return HttpResponseRedirect(reverse("StaffPage"))
            elif request.user.user_type == "3":
                return HttpResponseRedirect(reverse("TrainerPage"))
            else:
                return HttpResponseRedirect(reverse("StudentPage"))
    return render(request, "Authentication/Login.html")


def DoLogin(request):
    Account = request.POST.get('Account')
    Password = request.POST.get('Password')
    user = UsernameBackEnd.authenticate(
        request, username=Account, password=Password)
    if user != None:
        if user.is_active == True:
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("AdminPage"))
            elif user.user_type == "2":
                return HttpResponseRedirect(reverse("StaffPage"))
            elif user.user_type == "3":
                return HttpResponseRedirect(reverse("TrainerPage"))
            else:
                return HttpResponseRedirect(reverse("StudentPage"))
        else:
            messages.error(request, "The account is locked!")
            return HttpResponseRedirect("/")
    else:
        messages.error(request, "Invalid Login Details")
        return HttpResponseRedirect("/")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")




# Class-based password reset views
# - PasswordResetView sends the mail
# - PasswordResetDoneView shows a success message for the above
# - PasswordResetConfirmView checks the link the user clicked and
#   prompts for a new password
# - PasswordResetCompleteView shows a success message for the above

class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context


class PasswordResetView(View):
    def get(self, request):
        return render(request, 'registration/password_reset_form.html')

    def post(self, request):
        Email = request.POST.get('email')
        CustomUser = models.CustomUser.objects.filter(email=Email)
        if CustomUser.count() > 0:
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                form.save(self, request=self.request)
        else:
            messages.warning(request, f'Email does not exist in the system!')
            return redirect("password_reset")
        return render(request, 'registration/password_reset_done.html')


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'

class PasswordResetDoneView(View):
    def get(self, request):
        return render(request, 'registration/password_reset_done.html')

#
class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    reset_url_token = 'set-password'
    post_reset_login = False
    post_reset_login_backend = None
    token_generator = default_token_generator
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)
        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        messages.success(self.request, f'Your Password Has Been Set!')
        return redirect('ShowLogin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context

