from django.db import models
from webauth.models import WebauthUser

class ContractStatus:
  ACTIVE=0
  PENDING=1
  COMPLETE=2
  INCOMPLETE=3
  PENDING_TERMINATED=4

class PersonStatus:
  ALIVE = 0
  DEAD = 1
  ALMOST_DEAD = 2

# Create your models here.
class Person(models.Model):
  sunetid = models.CharField(max_length=40)
  webauth = models.ForeignKey(WebauthUser, unique=True)
  has_photo = models.BooleanField(default=False)
  status = models.IntegerField()

  def name(self):
    return self.webauth.get_full_name()

  def first_name(self):
    return self.name().split()[0]

  def kills(self):
    contracts = Contract.objects.filter(killer=self, status=ContractStatus.COMPLETE)
    return len(contracts)

class Contract(models.Model):
  assassin = models.ForeignKey(Person, related_name='assassin')
  target = models.ForeignKey(Person, related_name='target')
  killer = models.ForeignKey(Person, null=True)
  start_time = models.DateTimeField('Start Time')
  end_time = models.DateTimeField('End Time', null=True)
  status = models.IntegerField()

  def status_string(self):
    if self.status == 0:
      return "Active"
    elif self.status == 1:
      return "Pending"
    elif self.status == 2:
      return "Complete"
    elif self.status == 3:
      return "Incomplete"
    elif self.status == 4:
      return "Pending (Terminated)"