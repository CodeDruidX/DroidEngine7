v = "7.0.0"
print(f"Droid 3d Engine v{v}")


import numpy as np
import cv2
import pygame
import math


def img_into_polygon(np_img: np.float32, np_polygon: np.float32):
    h, w, _ = np_img.shape
    bounds = np.array(
        [[0.0, 0.0], [w, 0.0], [w, h], [0.0, h]]
    )  # Изначальный квадрат изображения

    heights, widths = np_polygon.T
    max_h, max_w = max(heights), max(widths)

    perspective = cv2.getPerspectiveTransform(bounds, np_polygon)  # Матрица поворота
    img = cv2.warpPerspective(np_img, perspective, (max_h, max_w), flags=cv2.INTER_AREA)

    return pygame.image.frombuffer(
        img.tobytes(), img.shape[1::-1], "RGBA"
    ).convert_alpha()  # Конвертация в pygame пригодный формат


def unit_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))


def view3d(camera: np.float32, point: np.float32):
    camera_system = point - camera[0]

    """
    xy_d = math.copysign(np.linalg.norm(camera_system[:2]),camera_system[0]*camera_system[1])
    xyz_d = np.arctan2(xy_d, camera_system[2]) - np.radians(camera[1][0])

    zy_d = math.copysign(np.linalg.norm(camera_system[1:]),camera_system[1]*camera_system[2])
    zyx_d = np.arctan2(zy_d, camera_system[0]) - np.radians(camera[1][1])
    """
    # print(camera_system)
    vert = math.copysign(
        angle_between(
            camera_system, np.array([camera_system[0], camera_system[1], 0.0])
        ),
        camera_system[2],
    )
    bhor = math.copysign(
        angle_between(
            camera_system, np.array([camera_system[0], 0.0, camera_system[2]])
        ),
        1,
    )
    # print(hor,vert)
    B = math.copysign(
        angle_between(camera_system, np.array([0, 0.0, camera_system[2]])), 1
    )

    if camera_system[0] >= 0:
        if camera_system[1] >= 0:
            hor = bhor
        else:
            hor = -bhor
    else:
        if camera_system[1] >= 0:
            hor = 2 * B - bhor
        else:
            hor = -2 * B + bhor

    print(bhor, "->", hor, camera_system, B)

    return np.float32([hor, vert]) - camera[1]


def screen_transform(angles, w, h, fov):
    dir1, dir2 = angles / fov
    w, h = w / 2 - dir1 * w, h / 2 - dir2 * h

    return int(w), int(h)


def render(camera, point, w=1920, h=1080, fov=90):
    angles = view3d(camera, point)
    return screen_transform(angles, w, h, fov), angles


# camera=[[x,y],[vert_angle,horis_angle]]
camera = np.array([[0.0, 0.0, 0.0], [0.0, 0.0]])


from math import hypot, sin, cos, atan, degrees, radians
import pygame
import pyautogui

WIDTH, HEIGHT = pyautogui.size()


pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
successes, failures = pygame.init()
pygame.event.set_allowed([pygame.QUIT])
print("{0} successes and {1} failures".format(successes, failures))


screen = pygame.display.set_mode(
    (WIDTH, HEIGHT), flags=pygame.FULLSCREEN | pygame.DOUBLEBUF
)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
FPS = 60  # Frames per second.

BLACK = (25, 25, 25)
WHITE = (255, 255, 255)
# RED = (255, 0, 0), GREEN = (0, 255, 0), BLUE = (0, 0, 255).

myfont = pygame.font.SysFont("impact", 12)

logs = ""
while True:
    clock.tick(FPS)
    logs = ""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    pressed_keys = pygame.key.get_pressed()
    # print(camera[1])
    if True:
        if pressed_keys[pygame.K_w]:
            camera[0][0] += 0.2
        elif pressed_keys[pygame.K_s]:
            camera[0][0] -= 0.2
        if pressed_keys[pygame.K_a]:
            camera[0][1] += 0.2
        elif pressed_keys[pygame.K_d]:
            camera[0][1] -= 0.2
        if pressed_keys[pygame.K_r]:
            camera[0][2] += 0.2
        elif pressed_keys[pygame.K_f]:
            camera[0][2] -= 0.2
        if pressed_keys[pygame.K_o]:
            quit()
    x, y = pygame.mouse.get_pos()
    x -= WIDTH / 2
    y -= HEIGHT / 2
    pyautogui.moveTo(WIDTH / 2, HEIGHT / 2)
    camera[1][0] -= x
    camera[1][1] -= y
    if camera[1][0] > 180:
        camera[1][0] -= 360
    if camera[1][0] < -180:
        camera[1][0] += 360
    if camera[1][1] > 180:
        camera[1][1] -= 360
    if camera[1][1] < -180:
        camera[1][1] += 360
    screen.fill(BLACK)

    pos, a = render(camera, np.float32([10, 0, 0.9]))
    pygame.draw.circle(screen, WHITE, pos, 10)

    pos, a = render(camera, np.float32([10, 0.9, 0.9]))
    pygame.draw.circle(screen, (0, 0, 255), pos, 10)

    pos, a = render(camera, np.float32([-10, 0, 0.9]))
    pygame.draw.circle(screen, WHITE, pos, 10)

    pos, a = render(camera, np.float32([-10, 0.9, 0.9]))
    pygame.draw.circle(screen, (255, 0, 0), pos, 10)
    pygame.display.update()
