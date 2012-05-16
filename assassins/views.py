# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect

from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings

from django.db.models import Q

import time
import sys
import random
from datetime import datetime, timedelta

from assassins.models import Person, Contract, ContractStatus, PersonStatus

def send_mail(subject, message, to):
  email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [to], [settings.DEFAULT_FROM_EMAIL])
  email.send()

@login_required
def admin(request):
  if request.user.username not in settings.ADMIN_SUNETID:
    return render_to_response('message.html', {'message' :  'You aren\'t authorized to view that page.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  return render_to_response('admin.html', {'users' : Person.objects.all(), 'contracts' : Contract.objects.all() })

@login_required
def new_user(request):
  if Person.objects.filter(sunetid=request.user.username):
    return render_to_response('message.html', {'message' : 'You have already signed up.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  p = Person(sunetid=request.user.username,webauth=request.user,status=PersonStatus.ALIVE)
  p.save()
  return redirect('/')

@login_required
def email(request):
  if request.user.username not in settings.ADMIN_SUNETID:
    return render_to_response('message.html', {'message' :  'You aren\'t authorized to view that page.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})

  people = map(lambda p: "%s@stanford.edu" % p.sunetid, list(Person.objects.filter(status=PersonStatus.ALIVE)))
  for to in people:
    send_mail(request.POST['subject'], request.POST['message'], to)
    print >> sys.stderr, "Sent to {0}".format(c.assassin.name())
    time.sleep(1)
  return redirect('/admin/')

@login_required
def update_user(request):
  if request.user.username not in settings.ADMIN_SUNETID:
    return render_to_response('message.html', {'message' :  'You aren\'t authorized to view that page.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  if 'sunetid' not in request.POST:
    return HttpResponse('Error')
  if request.POST['update'] == 'Delete':
    p = Person.objects.get(sunetid=request.POST['sunetid'])
    p.delete()
  elif request.POST['update'] == 'Update':
    p = Person.objects.get(sunetid=request.POST['sunetid'])
    if 'photo' in request.POST:
      p.has_photo = True
    else:
      p.has_photo = False
    p.save()
  return redirect('/admin/')


def get_people(init_list, people_query):
  people = []
  for p in init_list:
    people.append(Person.objects.get(sunetid=p))

  random.shuffle(people_query)
  for person in people_query:
    if person not in people:
      people.append(person)

  return people

@login_required
def scramble_remaining(request):
  if request.user.username not in settings.ADMIN_SUNETID:
    return render_to_response('message.html', {'message' : 'You aren\'t authorized to view that page.', 'user' : current_person})
  old_contracts = Contract.objects.filter(status=ContractStatus.ACTIVE)
  pending_contracts = Contract.objects.filter(Q(status=ContractStatus.PENDING) | Q(status=ContractStatus.PENDING_TERMINATED))
  for contract in old_contracts:
    contract.status = ContractStatus.INCOMPLETE
    contract.save()
  for contract in pending_contracts:
    contract.status = ContractStatus.COMPLETE
    contract.save()

  people = get_people(request.POST['start_list'].split(), list(Person.objects.filter(status=PersonStatus.ALIVE)))

  for i in range(len(people)):
    c = Contract(assassin=people[i], target=people[(i+1)%len(people)], start_time=datetime.now(), status=ContractStatus.ACTIVE)
    c.save()
    send_contract_email(c.assassin.sunetid, c.target.name())
    print >> sys.stderr, "Sent to {0}".format(c.assassin.name())
    time.sleep(1)
  return redirect('/admin/')

@login_required
def init_contracts(request):
  if request.user.username not in settings.ADMIN_SUNETID:
    return render_to_response('message.html', {'message' : 'You aren\'t authorized to view that page.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  Contract.objects.all().delete()

  people = get_people(request.POST['start_list'].split(), list(Person.objects.all()))

  for i in range(len(people)):
    people[i].status = PersonStatus.ALIVE
    people[i].save()
    c = Contract(assassin=people[i], target=people[(i+1)%len(people)], start_time=datetime.now(), status=ContractStatus.ACTIVE)
    c.save()
    send_contract_email(c.assassin.sunetid, c.target.name())
    print >> sys.stderr, "Sent to {0}".format(c.assassin.name())
    time.sleep(1)
  return redirect('/admin/')

@login_required
def view_target(request):
  current_person = None
  try:
    current_person = Person.objects.get(sunetid=request.user.username)
  except ObjectDoesNotExist:
    return redirect('/new_user')
  contracts = Contract.objects.filter(assassin=current_person)
  completed_contracts = contracts.filter(status=ContractStatus.COMPLETE)
  current_contracts = contracts.filter(Q(status=ContractStatus.ACTIVE) | Q(status=ContractStatus.PENDING) | Q(status=ContractStatus.PENDING_TERMINATED))
  all_contracts = Contract.objects.all();
  termination_list = []
  for c in all_contracts:
    if c.status == ContractStatus.ACTIVE and c.assassin.status == PersonStatus.ALIVE and (c.start_time + timedelta(hours=settings.TERMINATION_START)) < datetime.now(c.start_time.tzinfo):
      termination_list.append(c.assassin)
  current_contract = None
  time_left = 0
  hours = 0
  minutes = 0
  seconds = 0
  if current_contracts:
    current_contract = current_contracts[0]
    time_left = (timedelta(hours=settings.TERMINATION_START) + (current_contract.start_time) - datetime.now(current_contract.start_time.tzinfo))
    hours = int(time_left.total_seconds()/60/60)
    minutes = int((time_left.total_seconds()/60)%60)
    seconds = int((time_left.total_seconds()%60))
  return render_to_response('target.html', {'termination_list' : termination_list,
                                            'current_user' : current_person,
                                            'completed_contracts' : completed_contracts,
                                            'defend_time' : settings.DEFEND_TIME,
                                            'dorm_name' : settings.DORM_NAME,
                                            'hours' : hours,
                                            'minutes' : minutes,
                                            'seconds' : seconds,
                                            'current_contract' : current_contract})

def logged_out(request):
  return render_to_response('message.html', {'message' : 'You are logged out.'})

@login_required
def leaderboard(request):
  current_person = Person.objects.get(sunetid=request.user.username)
  people = Person.objects.all().extra(select={'kills': 'select count(*) from assassins_contract where killer_id = assassins_person.id and status = 2'}).extra(order_by=['-kills', 'status'])
  return render_to_response('leaderboard.html', {'current_user' : current_person, 'people' : people, 'dorm_name' : settings.DORM_NAME})


@login_required
def report_kill(request):
  current_person = Person.objects.get(sunetid=request.user.username)
  if not current_person:
    return render_to_response('message.html', {'message' : 'You aren\'t in the game.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  if 'sunetid' not in request.POST:
    return HttpResponse('Error')

  t = str(request.POST['sunetid']).encode('ascii')
  target = Person.objects.get(sunetid__exact=t)
  target.status = PersonStatus.ALMOST_DEAD
  target.save()
  contract = None
  try:
    contract = Contract.objects.get(status=ContractStatus.ACTIVE, target=target)
  except ObjectDoesNotExist:
    pass
  if contract:
    if current_person != contract.assassin:
      contract.status = ContractStatus.PENDING_TERMINATED
    else:
      contract.status = ContractStatus.PENDING
    contract.killer = current_person
    contract.save()
  send_pending_email(current_person.name(), target.sunetid, target.first_name())
  return redirect('/')

@login_required
def confirm_death(request):
  current_person = None
  if request.user.username in settings.ADMIN_SUNETID: #Allows admins to force confirm death
    current_person = Person.objects.get(sunetid=request.POST['sunetid'])
  else:
    current_person = Person.objects.get(sunetid=request.user.username)
  if not current_person:
    return render_to_response('message.html', {'message' : "You aren't in the game.", 'user' : current_person})
  completed_contract = Contract.objects.filter(target=current_person).filter(Q(status=ContractStatus.PENDING) | Q(status=ContractStatus.PENDING_TERMINATED))
  actual_completed_contract = Contract.objects.filter(target=current_person, status=ContractStatus.COMPLETE)
  if len(completed_contract) > 0:
    completed_contract = completed_contract.get()
  elif len(actual_completed_contract) > 0:
    return render_to_response('message.html', {'message' : 'You have already been confirmed dead.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  else:
    return render_to_response('message.html', {'message' : 'It seems no one has claimed that you are dead.', 'user' : current_person, 'dorm_name' : settings.DORM_NAME})
  current_person.status = PersonStatus.DEAD
  current_person.save()
  old_status = completed_contract.status
  if completed_contract and completed_contract.status:
    completed_contract.status = ContractStatus.COMPLETE
    completed_contract.save()
  contract = Contract.objects.filter(Q(status=ContractStatus.ACTIVE) | Q(status=ContractStatus.PENDING) | Q(status=ContractStatus.PENDING_TERMINATED), assassin=current_person)
  if contract:
    contract = contract[0]
    contract.status = ContractStatus.INCOMPLETE
    contract.save()
    if (completed_contract.assassin != contract.target):
      newcontract = Contract(assassin=completed_contract.assassin, target=contract.target, start_time=datetime.now(), status=ContractStatus.ACTIVE)
      newcontract.save()
      if old_status == ContractStatus.PENDING:
        send_contract_email(completed_contract.assassin.sunetid, contract.target.name())
      else:
        send_terminated_email(completed_contract.assassin.sunetid, completed_contract.target.name().split()[0], contract.target.name())
    else:
      send_mail('Game Over!', '%s won the game.' % completed_contract.assassin.name(), settings.ADMIN_SUNETID[0])
  return redirect('/')

def send_terminated_email(assassin_sunetid, target_name, new_target_name):
  send_mail('Your Contract has been terminated',
            'Hello assassin,\n It appears %s was moving too slowly and we had to terminate him. Your next target is:\n%s\n' % target_name, new_target_name,
            '%s@stanford.edu' % assassin_sunetid)

def send_contract_email(assassin_sunetid, target_name):
  send_mail('Your Next Contract',
            'Hello assassin,\nHere is your target: %s\n Should you not complete your assignment in %s hours, you will be terminated.' % (target_name, settings.TERMINATION_START),
            '%s@stanford.edu' % assassin_sunetid)

def send_pending_email(assassin_name, target_sunetid, target_first_name):
  send_mail('Confirm Assassination',
            'Hello %s,\n%s just killed you in our game of assassins. Please go to %s/confirm_death to confirm.\n' % (target_first_name, assassin_name, settings.BASE_URL),
            '%s@stanford.edu' % target_sunetid)



