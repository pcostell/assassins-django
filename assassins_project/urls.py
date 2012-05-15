from django.conf.urls import patterns, include, url

from django.views.static import *
from django.conf import settings

urlpatterns = patterns('',

    url(r'^admin/init_contracts', 'assassins.views.init_contracts'),
    url(r'^admin/scramble_remaining', 'assassins.views.scramble_remaining'),
    url(r'^admin/update_user', 'assassins.views.update_user'),
    url(r'^admin/email', 'assassins.views.email'),
    url(r'^leaderboard', 'assassins.views.leaderboard'),
    url(r'^logged_out', 'assassins.views.logged_out'),
    url(r'^new_user', 'assassins.views.new_user'),
    url(r'^admin', 'assassins.views.admin'),
    url(r'^webauth/', include('webauth.urls')),
    url(r'^report_kill$', 'assassins.views.report_kill'),
    url(r'^confirm_death$', 'assassins.views.confirm_death'),
    url(r'^$', 'assassins.views.view_target'),
)
