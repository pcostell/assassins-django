from models import WebauthUser
from django.contrib.auth.models import AnonymousUser

class WebauthMiddleware(object):
    def process_request(self,request):
        assert hasattr(request, 'session'), "The Webauth middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        if not request.session.has_key('wa_username'):
            request.user = AnonymousUser()
        else:
            request.user = WebauthUser.objects.get(username__exact=request.session['wa_username'])
        return None