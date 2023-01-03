v="6.0.0"
print(f"Droid 3d Engine v{v}")
print("Loading Engine, JIT maths, prepape pygame")

import pip

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

install('numpy')
install('numba')

from math import hypot,sin,cos,atan,degrees,radians
from numba import njit

import numpy as np

import cv2

def img_into_polygon(img,new_polygon):
	global logs
	new_polygon=list(new_polygon)
	height, width, channels = img.shape
	bounds = np.float32([[0,0],[width,0],[width,height],[0,height]])
	
	farsx=sum(np.absolute(np.array(new_polygon)[:,0]-(np.array(new_polygon)[:,0].mean())))
	farsy=sum(np.absolute(np.array(new_polygon)[:,1]-(np.array(new_polygon)[:,1].mean())))
	if farsx < 10 or farsy < 10: return None
	heights, widths=zip(*new_polygon)
	max_h,max_w=max(heights),max(widths)
	perspective = cv2.getPerspectiveTransform(bounds,np.float32(new_polygon))

	img=cv2.warpPerspective(img,perspective,(max_h,max_w),flags=cv2.INTER_AREA)
	
	surf = pygame.image.frombuffer(img.tobytes(), img.shape[1::-1], "RGBA").convert_alpha()
	return surf



@njit(fastmath=True)
def project_to_vector(x_d,y_d):
    if x_d==0 and y_d>0: direction=0

    elif x_d==0 and y_d<0: direction=180

    elif y_d==0 and x_d>0: direction=90

    elif y_d==0 and x_d<0: direction=270

    elif y_d > 0: direction=degrees(atan(x_d/y_d))

    elif y_d < 0: direction=degrees(atan(x_d/y_d))+180

    else: direction=0

    if direction<0:
        direction+=360
    if direction > 360:
        direction-=360
    return (direction,hypot(x_d,y_d))

@njit(fastmath=True)
def vector_to_project(dir,hyp):
    x_d=sin(radians(dir))*hyp
    y_d=cos(radians(dir))*hyp
    return (x_d, y_d)


def view3d(camera,object):
	global logs
	camera_system=np.array(object)-camera["coords"]

	dir0tmp,tmp=project_to_vector(camera_system[2],camera_system[0])
	if camera_system[0] <= 0: tmp=tmp*-1

	logs+=str(camera_system)+"\n"
	dir1,far=project_to_vector(tmp,camera_system[1])
	logs+=str(int(dir1))+"\n"
	dir0tmp,tmp=project_to_vector(camera_system[0],camera_system[1])
	dir2,far=project_to_vector(tmp,camera_system[2])

	dir1-=camera["dir"][0]
	dir2-=camera["dir"][1]+90
	if dir1>360: dir1-=360
	if dir2>360: dir2-=360
	if dir1<0: dir1+=360
	if dir2<0: dir2+=360
	return far,dir1,dir2


def render_list(camera,objects,w,h,fov):
	res=[]
	dist=[]
	for o in objects:
		far,d1,d2=view3d(camera,o)
		r=screen_transform(d1,d2,w,h,fov)
		res.append(r)
		dist.append(far)
	return res,np.array(dist).mean()

@njit(fastmath=True)
def screen_transform(dir1,dir2,w,h,fov):
	w=((dir1-90)/fov)*w
	#if 0 > dir1 > 180: n_w=(w/2)+((dir1)/180)*w
	h=((dir2-90)/fov)*h

	#w=(n_w/w-int(n_w/w))*w
	#h=(n_h/h-int(n_h/h))*h
	return int(w),int(h)

#Полигон может иметь одну сторону за экраном справа, а другую слева.
#В таком случае он нарисуется поверх всего экрана и будет печально....


def polygon_is_good(poly,w,h):
	max_right=max(list(zip(*poly))[0])
	max_down=max(list(zip(*poly))[1])
	min_right=min(list(zip(*poly))[0])
	min_down=min(list(zip(*poly))[1])
	if max_right > w and min_right < 0: return False
	if max_down > h and min_down < 0: return False
	return True
def blitlogs(surf, renderer):
	h = renderer.get_height()
	lines = logs.split('\n')
	for i, ll in enumerate(lines):
		txt_surface = renderer.render(ll, True, (255,255,255))
		surf.blit(txt_surface, (0, (i*h)))

import numpy as np

camera={
	"coords":[0,0,0],
	"dir":[0,0]
}


objects=[{
	"wall":[[5,0,3],[5,3,3],[5,3,-3],[5,0,-3]],
	"img":cv2.cvtColor(cv2.cvtColor(cv2.imread("image.png"), cv2.COLOR_RGB2BGR), cv2.COLOR_RGB2RGBA)
},
{
	"wall":[[6,0,3],[6,3,3],[6,3,-3],[6,0,-3]],
	"img":cv2.cvtColor(cv2.cvtColor(cv2.imread("image.png"), cv2.COLOR_RGB2BGR), cv2.COLOR_RGB2RGBA)
},
{
	"wall":[[7,0,3],[7,3,3],[7,3,-3],[7,0,-3]],
	"img":cv2.cvtColor(cv2.cvtColor(cv2.imread("image.png"), cv2.COLOR_RGB2BGR), cv2.COLOR_RGB2RGBA)
},
{
	"wall":[[8,0,3],[8,3,3],[8,3,-3],[8,0,-3]],
	"img":cv2.cvtColor(cv2.cvtColor(cv2.imread("image.png"), cv2.COLOR_RGB2BGR), cv2.COLOR_RGB2RGBA)
},
#{
#	"wall":[[5,3,3],[5,0,3],[-5,0,-6],[-5,3,-6]],
#	"img":cv2.cvtColor(cv2.cvtColor(cv2.imread("img.jpg"), cv2.COLOR_RGB2BGR), cv2.COLOR_RGB2RGBA)
#},
{
	"wall":[[-5,0,3],[-5,3,3],[-5,3,-3],[-5,0,-3]],
	"img":cv2.cvtColor(cv2.cvtColor(cv2.imread("img.png"), cv2.COLOR_RGB2BGR), cv2.COLOR_RGB2RGBA)
}
]
objects[0]["img"][:, :, 3] = 255

import pygame
import pyautogui
WIDTH, HEIGHT = pyautogui.size()


pyautogui.FAILSAFE=False
pyautogui.PAUSE=0
successes, failures = pygame.init()
pygame.event.set_allowed([pygame.QUIT])
print("{0} successes and {1} failures".format(successes, failures))


screen = pygame.display.set_mode((WIDTH, HEIGHT),flags =pygame.FULLSCREEN | pygame.DOUBLEBUF)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
FPS = 60  # Frames per second.

BLACK = (25, 25, 25)
WHITE = (255, 255, 255)
# RED = (255, 0, 0), GREEN = (0, 255, 0), BLUE = (0, 0, 255).

myfont = pygame.font.SysFont("impact", 12)

logs=""
while True:
	clock.tick(FPS)
	logs=""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
	
	pressed_keys = pygame.key.get_pressed()
	#print(camera["dir"])
	if True:
            if pressed_keys[pygame.K_w]:
                camera["coords"][1]+=cos(radians(camera["dir"][0]+180))*0.2
                camera["coords"][0]+=sin(radians(camera["dir"][0]+180))*0.2
            elif pressed_keys[pygame.K_s]:
                camera["coords"][1]+=cos(radians(camera["dir"][0]))*0.2
                camera["coords"][0]+=sin(radians(camera["dir"][0]))*0.2
            if pressed_keys[pygame.K_a]:
                camera["coords"][1]+=cos(radians(camera["dir"][0]+90))*0.2
                camera["coords"][0]+=sin(radians(camera["dir"][0]+90))*0.2
            elif pressed_keys[pygame.K_d]:
                camera["coords"][1]+=cos(radians(camera["dir"][0]-90))*0.2
                camera["coords"][0]+=sin(radians(camera["dir"][0]-90))*0.2
            if pressed_keys[pygame.K_r]:
                camera["coords"][2]+=0.2
            elif pressed_keys[pygame.K_f]:
                camera["coords"][2]-=0.2
            if pressed_keys[pygame.K_o]:
                quit()
	x, y = pygame.mouse.get_pos()
	x-=WIDTH/2
	y-=HEIGHT/2
	pyautogui.moveTo(WIDTH/2, HEIGHT/2)
	camera["dir"][0]+=x
	camera["dir"][1]+=y
	if camera["dir"][0]>360:camera["dir"][0]-=360
	if camera["dir"][0]<0:camera["dir"][0]+=360
	if camera["dir"][1]>360:camera["dir"][1]-=360
	if camera["dir"][1]<0:camera["dir"][1]+=360
	screen.fill(BLACK)

	res=[]
	for object in objects:
		render=render_list(camera,object["wall"],WIDTH,HEIGHT,180)
		if not render:continue
		poly,dist=render
		res.append([dist,(object,poly)])

	res.sort(key=lambda x: x[0],reverse=True)

	for i in res:
		i=i[1]
		object,poly=i
		if poly:
				if polygon_is_good(poly,WIDTH,HEIGHT):
					lst=list(zip(*poly))
					corner=[min(lst[0]),min(lst[1])]
					img=img_into_polygon(object["img"],poly-np.array([corner]*len(poly)))
					if img: screen.blit(img,corner)
	logs+="\n"+str(int(clock.get_fps()))+"\n"
	blitlogs(screen,myfont)
	pygame.display.update()  # Or pygame.display.flip()