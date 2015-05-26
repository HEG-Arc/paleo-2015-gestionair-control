from django.shortcuts import render
from django.http import HttpResponse
import _thread
import time

# Create your views here.

def home(request):
    """ Accueil du Call Center """
    text = """<h1>Bienvenue sur le Call Center !</h1>
              <p>Application pour le Paléo !</p>"""
    return HttpResponse(text)

def start(request):
    """ Déclenche le timer """
    _thread.start()

def beat(request):
    """ Affiche le timer """
    time = 240
    while time > 0:
         print (time)
         time = time-1
         time.sleep(1)

def stop(request):
    """ Déclenche le timer """
    _thread.stop()

def countdown(request):
    """ Déclenche le timer """

def print(request):
    return HttpResponse(beat())


class Worker(Thread):
    def run(self):
        for x in range(240,0):
            print(x)
            time.sleep(1)


def start():
    Worker().start()


def sleep():
    time.sleep(1)


def date1(request):
    return render(request, 'date.html', {'date': datetime.now()})

def son(beat):
    if beat == 240:
        introson.start()
    if beat == 225:
        simulson.start()
    if beat == 15:
        finalson.start()