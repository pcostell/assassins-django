import hashlib
from django.conf import settings
from models import WebauthUser
from django.contrib.auth.models import User

WEBAUTH_VERSION = "WA_2"

class WebauthVersionNotSupported(Exception):
    """
    Error occurs only when the server providing login services had a version that was not equal to ours.
    """
    pass

def _make_hash(string):
    "SHA-1 stub method"
    m = hashlib.sha1()
    m.update(string)
    return m.hexdigest()

def WebauthLogin(request,version,username,hashString,full_name=None):
    """
    Completes the login process for a Webauth user; checks the hash + nonce to ensure the user should be able to login,
    then sets the appropriate parameter so that the middleware logs in the user.

    The session will not be active until the middleware runs again (i.e., the next page load.)
    """
    if version != WEBAUTH_VERSION:
        raise WebauthVersionNotSupported

    (nonce,hash) = hashString.split('$')
    expected_hash = _make_hash(settings.WEBAUTH_SHARED_SECRET + nonce + username)

    if expected_hash == hash:
        # create Django user for the WebAuth'd person if they don't exist
        # session will not be active till next pageload
        if WebauthUser.objects.filter(username__exact=username).count() == 0:
            WebauthCreate(username,full_name)

        request.session['wa_username'] = username
        return True
    else:
        return False

def WebauthCreate(username, full_name):
    """
    Creates a WebauthUser from the provided username + full name. If the given username already exists, it converts the user
    into a WebauthUser.
    """
    if WebauthUser.objects.filter(username__exact=username).count() > 0:
        return
        
    authuser_obj = User.objects.filter(username__exact=username)
    if not authuser_obj.exists():
        user = WebauthUser()
        user.new_webauth(username,full_name)
    else:
        user = authuser_obj.get()
        user.__class__ = WebauthUser
        user.new_webauth(username,full_name)

def WebauthLogout(request):
    """
    Logs out a WebauthUser session.
    """
    del request.session['wa_username']