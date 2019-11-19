import os
import pygame
from pygame.locals import *  #constants

pygame.init()
pygame.mouse.set_visible(False)
font = pygame.font.SysFont("Times New Roman", 30)
 
screen = pygame.display.set_mode((800, 600), pygame.locals.FULLSCREEN)
pic = pygame.image.load("1.jpg")
screen.blit(pygame.transform.scale(pic, (800, 600)), (0, 0))
pygame.display.flip()

window_width = 400
window_height = 300

MYTIMERID = pygame.USEREVENT + 1
print ("MYEVENTID: " + str(MYTIMERID))

Timer_s  = 0
Timer_max = 60


def changeImage():
	color = (255,255,255)
	screen.blit(pygame.transform.scale(pic, (800, 600)), (0, 0))
	time_string = "Time du overlevede {} sekunder".format(pygame.time.get_ticks()/1000)
	text = font.render(time_string, True, color)
	screen.blit(text, (window_width/2, window_height/2-100))
	pygame.display.update()


def UpdateTimer():
	global Timer_s, Timer_max
	if Timer_s <= Timer_max:
		x = Timer_s / Timer_max * 800
		myrect = pygame.draw.rect(screen, (0,0,0), (0,0,800,32))
		myrec1 = pygame.draw.rect(screen, (0,255,0), (0,0,x,32))
		pygame.display.update()
	else:
		myrect = pygame.draw.rect(screen, (0,0,0), (0,0,800,32))
		pygame.display.update()
		pygame.time.set_timer(MYTIMERID, 0)
	Timer_s = Timer_s +1
		
pygame.time.set_timer(MYTIMERID, 1000)

done = False	
while not done:
	#internally process pygame event handlers
	pygame.event.pump()
	# warte auf ein Event
	event = pygame.event.wait()
	
	if event.type == QUIT:
		pygame.display.quit()

	if event.type == MYTIMERID:
		UpdateTimer()
		
	keyState = pygame.key.get_pressed()
	if keyState[pygame.K_ESCAPE]:
		print('\nGame Shuting Down!')
		done = True	
