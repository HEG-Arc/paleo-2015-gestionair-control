#
# "$Id: Makefile,v 1.2 2009/07/13 21:17:17 pgrenning Exp $"
#
#   PPD file makefile for the Common UNIX Printing System (CUPS).
#
#   Copyright 2007 by Apple Inc.
#   Copyright 1993-2006 by Easy Software Products.
#
#   These coded instructions, statements, and computer programs are the
#   property of Apple Inc. and are protected by Federal copyright
#   law.  Distribution and use rights are outlined in the file "LICENSE.txt"
#   which should have been included with this file.  If this file is
#   file is missing or damaged, see the license at "http://www.cups.org/".
#

include ../Makedefs

#
# PPD files...
#

FILES	=	deskjet.ppd dymo.ppd epson9.ppd epson24.ppd intelbar.ppd \
		laserjet.ppd okidata9.ppd okidat24.ppd stcolor.ppd \
		stcolor2.ppd stphoto.ppd stphoto2.ppd ttp20x0.ppd ttp7030.ppd \ 
		ttp8200.ppd zebra.ppd zebracpl.ppd zebraep1.ppd zebraep2.ppd  


#
# Make everything...
#

all:


#
# Clean all config and object files...
#

clean:


#
# Dummy depend...
#

depend:


#
# Install files...
#

install:	all
	$(INSTALL_DIR) -m 755 $(DATADIR)/model
	for file in $(FILES); do \
		$(INSTALL_DATA) $$file $(DATADIR)/model; \
	done


#
# Uninstall files...
#

uninstall:
	for file in $(FILES); do \
		$(RM) $(DATADIR)/model/$$file; \
	done
	-$(RMDIR) $(DATADIR)/model
	-$(RMDIR) $(DATADIR)


#
# Update PPD files...
#

ppds:
	ppdc -d . -l `echo $(LANGUAGES) | tr ' ' ','` sample.drv


#
# End of "$Id: Makefile,v 1.2 2009/07/13 21:17:17 pgrenning Exp $".
#
