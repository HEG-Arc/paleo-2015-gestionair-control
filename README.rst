# Gestion'air Web controller

Gestion'air is a web-based controller to run a call center simulation. You can visit our website http://gestionair.ch to see it in action.

## Web controller

web.py

## Task manager

Celery

celery -A config worker -l info -B

## Cache

Redis

## Media control

Pyglet

! On Ubuntu, you need the latest version of AVlib in order to play audio files with pyglet.

Download from: http://avbin.github.io/AVbin/Download.html

'''
$ chmod +x install-avbin-linux-x86-64-v10
sudo ./install-avbin-linux-x86-64-v10
'''

## U-HID library

PyUSB

## Call center

- https://wiki.koumbit.net/NagiosAndAsterisk
- http://www.voip-info.org/wiki/view/Asterisk%2Bauto-dial%2Bout%2Bdeliver%2Bmessage
- http://www.pycall.org/
- https://github.com/asterisk/ari-py
- https://wiki.asterisk.org/wiki/pages/viewpage.action?pageId=29395573#AsteriskRESTInterface(ARI)-WhatisaWebSocket?


Pygame

- http://stackoverflow.com/questions/17869101/unable-to-install-pygame-using-pip
- http://www.pygame.org/wiki/CompileUbuntu

## Printers windows:
- install print driver EPSON Advanced Printer Drivers TM-T20II
- check logo is on printer else add with drivers utility
- share printer

## CUPS test

apt-get install smbclient cups

+ enable initd cups

./tmx-cups/install.sh

docker:
mv /usr/lib/cups/backend/parallel /usr/lib/cups/backend-available/ &&\
    mv /usr/lib/cups/backend/serial /usr/lib/cups/backend-available/ &&\
    mv /usr/lib/cups/backend/usb /usr/lib/cups/backend-available/ &&\
    mv /usr/lib/cups/backend/gutenprint52+usb /usr/lib/cups/backend-available/

lpadmin -p winprinter -v smb://WINDOWSNETBIOSNAME/printersharename -P tmx-cups/ppd/tm-ba-thermal-rastertotmt.ppd

cupsaccept winprinter
cupsenable winprinter
lpstat -p

lp -d winprinter test.pdf



# .env file
POSTGRES_USER=
POSTGRES_PASSWORD=
DATABASE_URL=
DJANGO_SECRET_KEY=
ASTERISK_URL=
ASTERISK_USERNAME=
ASTERISK_PASSWORD=


JSON stats
==========
  {
	"event": {"name": "Capa'cité 2016", "start_date": "2016-09-05", "end_date": "2016-09-12"}
	"attendance": {"09:00": 23, "10:00": 100, "11:00": 121, "12:00": 32, "13:00": 49, "14:00": 118, "15:00": 152, "16:00": 129, "17:00": 92, "18:00": 21},
	"stats": {
		"win": {"wheel": 380, "free": 320},
		"scores": {"min": 5, "mean": 45, "max": 125},
		"retention": {"register": 760, "start": 740, "limit": 710, "scan": 700},
	},
	inventory: {"bonbons": 839, "parapluie": 45, "sac": 12, "linge": 45, "stylo": 2900, "porte-cle": 1800, "lunettes": 434, "tasses": 219}
  }
