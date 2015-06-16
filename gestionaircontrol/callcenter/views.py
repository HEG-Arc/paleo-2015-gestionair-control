# -*- coding: UTF-8 -*-

__author__ = 'benoit.vuille'
from django.http import HttpResponse
import time
from threading import Thread
from datetime import datetime
from django.shortcuts import render



def home(request):
    """ Accueil du Call Center """
    text = """<h1>Bienvenue sur le Call Center</h1>
              <p>Application pour le Paléo !</p>"""


    return HttpResponse(text)


def beat():
    """ Declenche le timer """
    timer = 240
    while timer > 0:
        print(timer)
        timer = timer-1
        time.sleep()


def print_test(request):
    return HttpResponse(beat())


class TimeThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.seconds = 0

    def run(self):
        cpt = 240
        while cpt > 0:
            self.seconds = cpt
            cpt -= 1

            time.sleep(1)

    def get_seconds(self):
        return self.seconds


def start(request):

    print("Lancement thread")
    mon_thread = TimeThread()
    mon_thread.start()

    print("Affichage du temps")
    while True:
        sleep()
        print(mon_thread.get_seconds())

    text = """test"""
    return HttpResponse(text)


def sleep():
    time.sleep(1)


def date1(request):
    return render(request, 'date.html', {'date': datetime.now()})


#def son(beat):
 #   if beat == 240:
  #      introson.start()
   # if beat == 225:
    #    simulson.start()
    #if beat == 15:
     #   finalson.start()