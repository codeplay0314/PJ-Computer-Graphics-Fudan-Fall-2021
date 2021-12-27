import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# 窗口大小
pygame.init()
infoObject = pygame.display.Info()
screen_w = int(infoObject.current_h)
screen_h = int(infoObject.current_h)
display_w = screen_w / 3
display_h = screen_h / 3

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(5, 20, -9, 0, 0, 0, -.1, -5, 0)   # 观察点位置，斜方向观察戒指
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display_w / display_h, 1, 100)
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, -0 / 100., 0.0)
    glRotatef(0, 0.0, 0.0, 1.0)
    glRotatef(0, 1.0, 0.0, 0.0)
    glRotatef(0, .0, 1.0, 0.0)
    glRotate(90, 0., 0., 1.)
    glutSolidTorus(1.0, 3.0, 25, 25)            # 设置Torus参数，后两个越大越接近圆柱
    glutSwapBuffers()

# 初始化
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(int(display_w), int(display_h)) 
glutCreateWindow("Ring")

# 光源、阴影等设置
glEnable(GL_NORMALIZE)
glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 10.0, 0.0])
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
glShadeModel(GL_SMOOTH)

# display函数
glutDisplayFunc(display)
glutMainLoop()