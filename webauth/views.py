import re
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
import urllib2
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from services import WebauthLogin, WebauthLogout, WebauthVersionNotSupported
from django.utils.datastructures import MultiValueDictKeyError

def login(request):
    if not 'WA_user' in request.GET:
        # return URL is this view
        return_url = urllib2.quote(settings.BASE_URL[:-1] + reverse('webauth.views.login'))

        # next URL is the URL provided. To prevent XSS, this is just the path within the app... if it were
        # anything else, people could do creative attacks to make webauth auth go to a different domain.
        try:
            next = request.GET['next']
        except MultiValueDictKeyError:
            next = ""
        next_url = urllib2.quote(next)

        return HttpResponseRedirect(settings.WEBAUTH_URL + "?next=" + next_url + "&return=" + return_url)
    else:
        try:
            username_64 = request.GET['WA_user'].strip()
            actual_hash = request.GET['WA_hash'].strip()
            name_64 = request.GET['WA_name'].strip()
            version = request.GET['WA_prot'].strip()
            next_64 = request.GET['WA_next'].strip()
        except MultiValueDictKeyError:
            username_64 = ""
            actual_hash = ""
            name_64 = ""
            version = ""
            next_64 = ""

        username = urllib2.base64.b64decode(username_64).strip()
        name = urllib2.base64.b64decode(name_64).strip()
        next = urllib2.base64.b64decode(next_64).strip()

        try:
            could_login = WebauthLogin(request,version,username,actual_hash,name)
        except WebauthVersionNotSupported:
            could_login = False

        if not could_login:
            return HttpResponseForbidden("Authentication provided was incorrect; check server versions of WebAuth, and make sure you have installed \
            the correct shared secret on both servers. Alternatively, stop trying to hack the site.")

        # redirect to the new URL, which should not be the login URL
        if next == reverse('webauth.views.login'):
            next = ''
        if len(next) > 0 and next[0] == '/':
            next = next[1:]

        return HttpResponseRedirect(settings.BASE_URL + next)

def logout(request):
    WebauthLogout(request)
    return HttpResponseRedirect('/logged_out')

def whoami(request):
    return HttpResponse("You are logged in as %s" % request.user.username)