import re

from django import forms
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import smart_unicode

#from misc.utils import get_send_mail
#send_mail = get_send_mail()
from mailer import send_mail

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

#from timezones.forms import TimeZoneField

alnum_re = re.compile(r'^\w+$')

class LoginForm(forms.Form):

    username = forms.CharField(label=_("Username"), max_length=30, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    remember = forms.BooleanField(label=_("Remember Me"), help_text=_("If checked you will stay logged in for 3 weeks"), required=False)

    user = None

    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValdidationError(_("This account is currently inactive."))
        else:
            raise forms.ValidationError(_("The username and/or password you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            #request.user.message_set.create(message=ugettext(u"Successfully logged in as %(username)s.") % {'username': self.user.username})
            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
            return self.user
        return None


class UserForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class ChangePasswordForm(UserForm):

    oldpassword = forms.CharField(label=_("Current Password"), widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_("New Password (again)"), widget=forms.PasswordInput(render_value=False))

    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]

    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]

    def save(self):
        self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
        self.user.message_set.create(message=ugettext(u"Password successfully changed."))


class ResetPasswordForm(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True, widget=forms.TextInput(attrs={'size':'30'}))

    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data["email"]).count() == 0:
            raise forms.ValidationError(_("Email address not verified for any user account"))
        if User.objects.filter(email__iexact=self.cleaned_data["email"]).count() > 1:
            raise forms.ValidationError(_("More than one user has that email address, cannot reset password"))
        return self.cleaned_data["email"]

    def save(self):
        for user in User.objects.filter(email__iexact=self.cleaned_data["email"]):
            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
            subject = _("Password reset")
            message = render_to_string("account/password_reset_message.txt", {
                "user": user,
                "new_password": new_password,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], priority="high")
        return self.cleaned_data["email"]

