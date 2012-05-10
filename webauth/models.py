from django.db import models
from django.contrib.auth.models import User

class WebauthUser(User):
    webauth_username = models.CharField(max_length=40, blank=False,unique=True)
    real_name = models.CharField(max_length=100,blank=True)

    def get_full_name(self):
        return self.real_name.strip()

    def new_webauth(self,username,real_name=None):
        self.webauth_username = username
        self.username = username
        if self.password == '':
            # disable regular Django login for this user
            self.set_unusable_password()
        self.real_name = real_name
        self.save()