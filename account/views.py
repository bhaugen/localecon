from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from account.forms import *

def login(request, form_class=LoginForm, template_name="account/login.html"):
    if request.method == "POST":
        default_redirect_to = getattr(settings, "LOGIN_REDIRECT_URLNAME", None)
        if default_redirect_to:
            default_redirect_to = reverse(default_redirect_to)
        else:
            default_redirect_to = settings.LOGIN_REDIRECT_URL
        next = request.REQUEST.get("next")
        redirect_to = next
        # light security check -- make sure redirect_to isn't garabage.
        if not redirect_to or "://" in redirect_to or " " in redirect_to:
            next = None
            redirect_to = default_redirect_to
        form = form_class(request.POST)
        user = form.login(request)
        if user:
            return HttpResponseRedirect(redirect_to)
    else:
        form = form_class()
    return render_to_response(template_name, {
        "form": form,
    }, context_instance=RequestContext(request))


def password_change(request, form_class=ChangePasswordForm,
        template_name="account/password_change.html"):
    if request.method == "POST":
        password_change_form = form_class(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            password_change_form = form_class(request.user)
    else:
        password_change_form = form_class(request.user)
    return render_to_response(template_name, {
        "password_change_form": password_change_form,
    }, context_instance=RequestContext(request))
password_change = login_required(password_change)

def password_reset(request, form_class=ResetPasswordForm,
        template_name="account/password_reset.html",
        template_name_done="account/password_reset_done.html"):
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            return render_to_response(template_name_done, {
                "email": email,
            }, context_instance=RequestContext(request))
    else:
        password_reset_form = form_class()
    
    return render_to_response(template_name, {
        "password_reset_form": password_reset_form,
    }, context_instance=RequestContext(request))
