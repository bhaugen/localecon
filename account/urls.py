from django.conf.urls.defaults import *
from account.forms import *

urlpatterns = patterns('',
    url(r'^login/$', 'account.views.login', name="acct_login"),
    url(r'^password_change/$', 'account.views.password_change', name="acct_passwd"),
    url(r'^password_reset/$', 'account.views.password_reset', name="acct_passwd_reset"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {"template_name": "account/logout.html"}, name="acct_logout"),
)

