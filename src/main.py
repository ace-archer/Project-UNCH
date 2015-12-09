#System imports
import math
import sys
import time
import os
import glob
import signal
import getch
import threading
import random

#Module imports
import gui
import method

#Platform code
os.system("clear")
os.system("stty -echo")
os.system("setterm -cursor off")
def quit():
	os.system("stty echo")
	os.system('clear')
	os.system("setterm -cursor on")
	print "Project UNCH has quit."
	sys.exit(0)

#Global variables
FRAMES_PER_SECOND = 20
GAME_RUNNING = True
MOB_FILES = glob.glob("../resources/mobs/*.txt")
COUNT_FILES=0
MOBS=[]
DEATH_FRAME = 0
MONEY=0
HIT_DMG=1
DPS=0
MOB_HP=10
MOB_MAX_HP=10
CURRENT_MOB=0
HIGHEST_ZONE=1
CURRENT_ZONE=1
ZONE_MOBS_KILLED=0
BOSS_TIMER=0.0
MOB_DEAD=False
quitMenuOpen=False
cmddisp=False
#Mob loading
for i in MOB_FILES:
	MOBS.append([])
	f=open(i)
	MOBS[COUNT_FILES].append("&RK"+i[16+i.find("/resources/mobs/"):len(i)-4].capitalize()+"&XX")
	for line in f:
		MOBS[COUNT_FILES].append(line)
	COUNT_FILES+=1
	f.close()
	
#Draw Title
gui.drawtitle()

#Definitions and methods

#Saving
def writesave():
	todo="write"

def readsave():
	todo="read"

#Methods
def hit():
	global HIT_DMG
	global MOB_HP
	MOB_HP -= HIT_DMG
	if MOB_HP < 0:
		MOB_HP = 0
def destroy():
	global MOB_HP
	MOB_HP -= 10000
	if MOB_HP < 0:
		MOB_HP = 0
def createMob():
	global MOB_MAX_HP, MOB_HP, CURRENT_MOB, MOB_DEAD, BOSS_TIMER
	MOB_DEAD=False
	MOB_MAX_HP = CURRENT_ZONE+random.randint(0,5)
	if CURRENT_ZONE % 5 == 0:
		MOB_MAX_HP = 10*CURRENT_ZONE+50
		BOSS_TIMER = time.time()
	MOB_HP = MOB_MAX_HP
	CURRENT_MOB=random.randint(0,COUNT_FILES-1)
def killMob():
	global ZONE_MOBS_KILLED, HIGHEST_ZONE, MOB_DEAD, MONEY
	MOB_DEAD=True
	MONEY += 1
	if CURRENT_ZONE==HIGHEST_ZONE:
		if CURRENT_ZONE % 5 != 0:
			ZONE_MOBS_KILLED = min(ZONE_MOBS_KILLED + 1, 10)
			if ZONE_MOBS_KILLED==10:
				ZONE_MOBS_KILLED=0
				HIGHEST_ZONE=max(HIGHEST_ZONE,CURRENT_ZONE+1)
		else:
			HIGHEST_ZONE=HIGHEST_ZONE+1
			ZONE_MOBS_KILLED=0
def update():
	global MOB_HP, HIGHEST_ZONE, CURRENT_ZONE, ZONE_MOBS_KILLED
	if MOB_HP <= 0 and not MOB_DEAD:
		killMob()
	if CURRENT_ZONE % 5 == 0 and 30.0-time.time()+BOSS_TIMER<=0:
		createMob()
def draw():
	global DEATH_FRAME, ZONE_MOBS_KILLED, MOB_MAX_HP, HIGHEST_ZONE, CURRENT_ZONE, lastch
	#gui.drawgui()
	method.bufferxy(4,1,method.dispBigNum(MONEY)) #money
	if CURRENT_ZONE-1>0:
		method.bufferxy(35,1,str(CURRENT_ZONE-1)) #zone num -
	if CURRENT_ZONE != HIGHEST_ZONE:
		method.bufferxy(49-len(str(CURRENT_ZONE)),1,str(CURRENT_ZONE+1)) #zone num + 
	method.bufferxy(42-len(str(CURRENT_ZONE))/2,1,str(CURRENT_ZONE)) #zone num
	if CURRENT_ZONE % 5 == 0: #zone mob nums
		method.bufferxy(36,15,"&RKTime: "+str(round(30.0-time.time()+BOSS_TIMER,1)) + "&XX") #boss timer
		if HIGHEST_ZONE > CURRENT_ZONE:
			method.bufferxy(46,3,"(1/1)")
		else:
			method.bufferxy(46,3,"(0/1)")
	else:
		if HIGHEST_ZONE > CURRENT_ZONE:
			method.bufferxy(44,3,"(10/10)")
		else:
			method.bufferxy(45,3,"("+str(ZONE_MOBS_KILLED)+"/10)")
	method.bufferxy(33,3,MOBS[CURRENT_MOB][0]) #mob name
	Y=int((float(MOB_HP)/float(MOB_MAX_HP))*22.0)
	X=55
	for i in range(22-Y, 22):
		method.bufferxy(X,i+1,("&GG" if Y > 0.5*22.0 else ("&YY" if Y > 0.25*22.0 else "&RR")) + "XX" + "&XX") #hashtag healthbar
	
	if MOB_HP <= 0: #mob death animation
		method.bufferxy(36,16,"rekt")
		if DEATH_FRAME == 20:
			DEATH_FRAME = 0
			createMob()
		else:
			for i in range(1,len(MOBS[CURRENT_MOB]) - (DEATH_FRAME/2)):
				method.bufferxy(32,(4 + (DEATH_FRAME/2)) +i,MOBS[CURRENT_MOB][i][:-1])
			DEATH_FRAME+=1
	else:
		for i in range(1,len(MOBS[CURRENT_MOB])): #mob drawing
			method.bufferxy(32,4+i,MOBS[CURRENT_MOB][i][:-1])
			method.bufferxy(36,16,method.dispBigNum(MOB_HP)) #mob hp num
	if not quitMenuOpen:
		if lastch=='.': #characters at bottom
			method.bufferxy(36,24," < ")
		elif lastch=='h' or lastch=='H':
			method.bufferxy(36,24,"  ?")
			method.bufferxy(18,1,"Press &BXH&XX again for a list of commands.")
		else:
			method.bufferxy(36,24,">  ")
	if quitMenuOpen:
		gui.drawquitmenu()
#Wait for SPACE before moving on.
ch=' '
lastch=' '

ch = getch.getch()
while ch != ' ':
	ch = getch.getch()
#Create first mob	
createMob()

#Main loop
def mainloop():
	while GAME_RUNNING:
		startTime=time.time()
		method.refreshBuffer()
		update()
		draw()
		method.printBuffer()
		endTime=time.time()
		timeElapsed=endTime-startTime
		sleepTime=1.0/float(FRAMES_PER_SECOND)-float(timeElapsed)
		time.sleep(sleepTime)

mainthread = threading.Thread(name='main', target=mainloop)
mainthread.setDaemon(True)
mainthread.start()

#Handle Input
while GAME_RUNNING:
	lastch=ch
	ch = getch.getch()
	#cases
	
	if quitMenuOpen:
		if ch=='y' or ch=='Y':
			GAME_RUNNING=False
			quit()
		elif ch=='n' or ch=='N':
			quitMenuOpen = False
	elif lastch=='h':
		if ch=='h' or ch=='H'
			cmddisp=True
	else:
		if ch=='.' and lastch!='.':
			hit()
		elif ch==',' and lastch=='.':
			hit()
		elif ch=='q':
			quitMenuOpen = True
		elif (ch=='=' or ch=='+') and CURRENT_ZONE<HIGHEST_ZONE:
			CURRENT_ZONE=CURRENT_ZONE+1
			createMob()
		elif (ch=='-' or ch=='_') and CURRENT_ZONE-1>0:
			CURRENT_ZONE=CURRENT_ZONE-1
			#ZONE_MOBS_KILLED=method.getMobsInZone(CURRENT_ZONE)
			createMob()
		elif ch=='0': #THIS IS DEBUG CODE ONLY
			destroy()
