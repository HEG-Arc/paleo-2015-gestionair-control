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