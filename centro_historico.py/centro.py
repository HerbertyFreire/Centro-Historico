import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# --- CORES ---
COLOR_WALL = (0.98, 0.82, 0.76)
COLOR_DOOR_WINDOW = (0.01, 0.22, 0.45)
COLOR_MOLDING = (0.95, 0.94, 0.90)
COLOR_BALCONY_GRILL = (0.45, 0.65, 0.85)
COLOR_ROOF = (0.7, 0.45, 0.3)
COLOR_GROUND = (0.6, 0.6, 0.6)
COLOR_WOOD_DARK = (0.30, 0.15, 0.05)
COLOR_WOOD_LIGHT = (0.60, 0.40, 0.20)
COLOR_PLANT_GREEN = (0.10, 0.50, 0.10)
COLOR_CHAIR_BLUE = COLOR_DOOR_WINDOW
COLOR_TABLE_GRAY = (0.75, 0.75, 0.75)
COLOR_TABLE_GRAY_D = (0.50, 0.50, 0.50)
COLOR_INTERIOR_WALL = (0.92, 0.88, 0.82)
COLOR_WOOD_FLOOR_BASE = (0.32, 0.22, 0.12)
COLOR_WOOD_FLOOR_SEAM = (0.16, 0.11, 0.07)
FLOOR_Y = 0.03
COLOR_BLACK = (0.0, 0.0, 0.0)
COLOR_WHITE = (0.97, 0.97, 0.97)
COLOR_FRAME = (0.40, 0.26, 0.12)

# --- CÂMERA ---
class Camera:
    def __init__(self, position=(0, 1.8, 15), yaw=-90.0, pitch=0.0):
        self.position = np.array(position, dtype=float)
        self.yaw, self.pitch = yaw, pitch
        self.speed, self.sensitivity = 0.15, 0.12
        self.player_height = 1.8
        self.gravity, self.jump_speed = -0.015, 0.25
        self.y_velocity, self.on_ground = 0, True
        self.update_vectors()

    def update_vectors(self):
        yaw_rad, pitch_rad = math.radians(self.yaw), math.radians(self.pitch)
        self.front = np.array([
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad)
        ])
        if np.linalg.norm(self.front) > 0: self.front /= np.linalg.norm(self.front)
        self.right = np.cross(self.front, np.array([0, 1, 0]))
        if np.linalg.norm(self.right) > 0: self.right /= np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)

    def process_mouse(self, dx, dy):
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_vectors()

    def update(self, keys):
        move_front = np.array([self.front[0], 0, self.front[2]])
        if np.linalg.norm(move_front) > 0: move_front /= np.linalg.norm(move_front)
        move_right = self.right
        if keys[pygame.K_w]: self.position += move_front * self.speed
        if keys[pygame.K_s]: self.position -= move_front * self.speed
        if keys[pygame.K_a]: self.position -= move_right * self.speed
        if keys[pygame.K_d]: self.position += move_right * self.speed
        self.y_velocity += self.gravity
        self.position[1] += self.y_velocity
        if keys[pygame.K_SPACE] and self.on_ground:
            self.y_velocity = self.jump_speed
            self.on_ground = False
        if self.position[1] < self.player_height:
            self.position[1] = self.player_height
            self.y_velocity = 0
            self.on_ground = True

    def look(self):
        look_at_point = self.position + self.front
        gluLookAt(self.position[0], self.position[1], self.position[2],
                  look_at_point[0], look_at_point[1], look_at_point[2],
                  self.up[0], self.up[1], self.up[2])

# --- FUNÇÕES DE DESENHO PRIMITIVAS ---
def draw_cube(center, size, color):
    x, y, z = center
    sx, sy, sz = size
    glColor3fv(color)
    v = [(x-sx/2,y-sy/2,z-sz/2),(x+sx/2,y-sy/2,z-sz/2),(x+sx/2,y+sy/2,z-sz/2),(x-sx/2,y+sy/2,z-sz/2),
         (x-sx/2,y-sy/2,z+sz/2),(x+sx/2,y-sy/2,z+sz/2),(x+sx/2,y+sy/2,z+sz/2),(x-sx/2,y+sy/2,z+sz/2)]
    s=[(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,5,6,2),(0,1,5,4),(3,2,6,7)]
    glBegin(GL_QUADS)
    for surf in s:
        for i in surf: glVertex3fv(v[i])
    glEnd()

def draw_arched_opening(center, size, color, arch_ratio=0.8):
    x,y,z = center
    sx,sy,sz = size
    r = sx/2
    rh = max(0, sy - (r * arch_ratio))
    glColor3fv(color)
    glBegin(GL_QUADS)
    glVertex3f(x-sx/2, y-sy/2, z); glVertex3f(x+sx/2, y-sy/2, z)
    glVertex3f(x+sx/2, y-sy/2+rh, z); glVertex3f(x-sx/2, y-sy/2+rh, z)
    glEnd()
    acy = y-sy/2+rh
    if arch_ratio > 0.01:
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x, acy, z)
        for i in range(19):
            a = math.radians(i*10)
            glVertex3f(x + math.cos(a)*r, acy + math.sin(a)*r*arch_ratio, z)
        glEnd()

def draw_cylinder(base_center, radius, height, color, slices=32):
    x, y, z = base_center
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    gluCylinder(quadric, radius, radius, height, slices, 1)
    gluDisk(quadric, 0, radius, slices, 1)
    glTranslatef(0, 0, height)
    gluDisk(quadric, 0, radius, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(quadric)
    glEnable(GL_CULL_FACE)

def draw_disk_xy(radius, z, color, slices=64):
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, z)
    for i in range(slices + 1):
        a = 2.0 * math.pi * i / slices
        glVertex3f(radius*math.cos(a), radius*math.sin(a), z)
    glEnd()
    glEnable(GL_CULL_FACE)

def draw_annulus_xy(outer_r, inner_r, z, color, slices=64):
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(slices + 1):
        a = 2.0 * math.pi * i / slices
        co, si = math.cos(a), math.sin(a)
        glVertex3f(outer_r*co, outer_r*si, z)
        glVertex3f(inner_r*co, inner_r*si, z)
    glEnd()
    glEnable(GL_CULL_FACE)

def draw_disk_yz(radius, x, cy, cz, color, slices=64):
    glDisable(GL_CULL_FACE)
    glColor3fv(color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x, cy, cz)
    for i in range(slices + 1):
        a = 2.0 * math.pi * i / slices
        glVertex3f(x, cy + radius*math.cos(a), cz + radius*math.sin(a))
    glEnd()
    glEnable(GL_CULL_FACE)


# --- FUNÇÕES DE DESENHO (OBJETOS / MÓVEIS) ---
def draw_book(bx, by, bz, w, h, d, color, lean_deg=0):
    glPushMatrix()
    glTranslatef(bx, by, bz)
    glTranslatef(0, h/2.0, 0)
    if lean_deg != 0:
        glRotatef(lean_deg, 0, 0, 1)
    draw_cube((0, 0, 0), (w, h, d), color)
    glPopMatrix()

def draw_bookshelf(center):
    x, y, z = center
    w, h, d = 2.00, 3.00, 0.40
    t, tb, back_t = 0.06, 0.05, 0.02
    glPushAttrib(GL_ENABLE_BIT); glDisable(GL_CULL_FACE)
    draw_cube((x - (w/2-t/2), y+h/2, z), (t, h, d), COLOR_WOOD_DARK)
    draw_cube((x + (w/2-t/2), y+h/2, z), (t, h, d), COLOR_WOOD_DARK)
    draw_cube((x, y+t/2, z), (w, t, d), COLOR_WOOD_DARK)
    draw_cube((x, y+h-t/2, z), (w, t, d), COLOR_WOOD_DARK)
    draw_cube((x, y+h/2, z-d/2+back_t/2+0.001), (w-2*t, h-2*t, back_t), COLOR_WOOD_DARK)
    skin, inner_h, inner_d = 0.004, h-2*t, d-0.06
    draw_cube((x-(w/2-t)+skin/2, y+t+inner_h/2, z), (skin, inner_h, inner_d), COLOR_WOOD_DARK)
    draw_cube((x+(w/2-t)-skin/2, y+t+inner_h/2, z), (skin, inner_h, inner_d), COLOR_WOOD_DARK)
    glPopAttrib()
    inner_left, inner_right = x-(w/2-t)+0.01, x+(w/2-t)-0.01
    book_d, book_zc = d-back_t-0.08, (z-d/2+back_t)+ (d-back_t-0.08)/2+0.01
    shelf_y = []
    for i in range(5):
        sy = y + t + i * ((h-2*t)/4.0)
        shelf_y.append(sy)
        draw_cube((x, sy, z), (w-2*t, tb, d-0.06), COLOR_WOOD_LIGHT)
    book_palette = [(0.84,0.15,0.16),(0.1,0.48,0.74),(0.2,0.63,0.17),(0.98,0.75,0.18),(0.56,0.27,0.68),(0.9,0.49,0.13)]
    width_seq = [0.07,0.05,0.08,0.06,0.09,0.045,0.075,0.065,0.055,0.085]
    height_seq = [0.42,0.36,0.48,0.4,0.44,0.38,0.46,0.41,0.43,0.39]
    for i, sy in enumerate(shelf_y):
        base_y = sy + tb/2 + 0.003
        next_clear_y = shelf_y[i+1]-tb/2 if i<4 else y+h-0.06
        max_clearance = max(0.1, next_clear_y - base_y - 0.02)
        cur_x, k, gap = inner_left, 0, 0.006
        while True:
            wbk = width_seq[k%len(width_seq)]
            if cur_x + wbk > inner_right: break
            hbk = min(height_seq[k%len(height_seq)], max_clearance)
            bx = cur_x + wbk/2
            lean_deg = (-5 if k%2==0 else 5) if (bx-inner_left>0.12) and (inner_right-bx>0.12) and ((i+k)%7==0) else 0
            color = book_palette[(i*5+k)%len(book_palette)]
            draw_book(bx, base_y, book_zc, wbk, hbk, book_d, color, lean_deg=lean_deg)
            cur_x += wbk + gap
            k += 1

def place_bookshelf(center, face_dir='+Z'):
    x, y, z = center
    glPushMatrix(); glTranslatef(x, y, z)
    if face_dir == '-Z': glRotatef(180, 0, 1, 0)
    draw_bookshelf((0, 0, 0))
    glPopMatrix()

def draw_table(center):
    x,y,z = center
    draw_cube((x, y+0.7, z), (1.5, 0.08, 0.8), COLOR_WOOD_LIGHT)
    draw_cube((x-0.65, y+0.35, z-0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)
    draw_cube((x+0.65, y+0.35, z-0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)
    draw_cube((x-0.65, y+0.35, z+0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)
    draw_cube((x+0.65, y+0.35, z+0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)

def draw_chair(center, rotation=0):
    x,y,z = center
    glPushMatrix(); glTranslatef(x,y,z); glRotatef(rotation, 0, 1, 0)
    seat_thick,leg_h,leg_off,leg_w,seat_w,seat_d = 0.12,0.45,0.22,0.06,0.55,0.55
    draw_cube((-leg_off, leg_h/2, -leg_off), (leg_w, leg_h, leg_w), COLOR_CHAIR_BLUE)
    draw_cube(( leg_off, leg_h/2, -leg_off), (leg_w, leg_h, leg_w), COLOR_CHAIR_BLUE)
    draw_cube((-leg_off, leg_h/2,  leg_off), (leg_w, leg_h, leg_w), COLOR_CHAIR_BLUE)
    draw_cube(( leg_off, leg_h/2,  leg_off), (leg_w, leg_h, leg_w), COLOR_CHAIR_BLUE)
    seat_y = leg_h + seat_thick/2
    draw_cube((0, seat_y, 0), (seat_w, seat_thick, seat_d), COLOR_CHAIR_BLUE)
    back_h, back_th, back_z, back_y = 0.70, 0.06, -seat_d/2 + 0.03, seat_y + 0.70/2
    draw_cube((0, back_y, back_z), (seat_w*0.95, back_h, back_th), COLOR_CHAIR_BLUE)
    glPopMatrix()

def draw_counter(center):
    draw_cube(center, (3.0, 1.0, 0.6), COLOR_WOOD_DARK)

def draw_plant(center):
    x,y,z = center
    draw_cube((x, y+0.2, z), (0.4, 0.4, 0.4), (0.5, 0.2, 0.1))
    draw_cube((x, y+0.6, z), (0.6, 0.5, 0.6), COLOR_PLANT_GREEN)

def draw_round_table(center, radius=0.8, height=0.75):
    x, y, z = center
    draw_cylinder((x, y, z), 0.12, height, COLOR_TABLE_GRAY_D)
    draw_cylinder((x, y-0.04, z), 0.35, 0.04, COLOR_TABLE_GRAY)
    glPushMatrix(); glTranslatef(x, y+height, z); glRotatef(90, 1, 0, 0)
    draw_cylinder((0,0,0), radius, 0.06, COLOR_TABLE_GRAY)
    glPopMatrix()

def draw_round_table_with_chairs(center, table_radius=0.8):
    cx, cy, cz = center
    draw_round_table(center, table_radius, height=0.75)
    d = table_radius + 0.70
    draw_chair((cx, cy, cz+d), 180); draw_chair((cx, cy, cz-d), 0)
    draw_chair((cx+d, cy, cz), -90); draw_chair((cx-d, cy, cz), 90)

def draw_wall_clock(center, radius=0.5, orientation='x'):
    x, y, z = center
    glPushMatrix(); glTranslatef(x, y, z)
    if orientation == 'x': glRotatef(90, 0, 1, 0)
    draw_annulus_xy(radius, radius-0.035, 0, (0.15,0.15,0.15), 96)
    face_r = radius-0.038
    draw_disk_xy(face_r, 0.0008, COLOR_WHITE, 96)
    glLineWidth(2.5); glColor3fv(COLOR_BLACK); glBegin(GL_LINES)
    for i in range(12):
        a = 2.0*math.pi*i/12.0; r0, r1 = face_r*0.82, face_r*0.95
        glVertex3f(r0*math.cos(a), r0*math.sin(a), 0.0012); glVertex3f(r1*math.cos(a), r1*math.sin(a), 0.0012)
    glEnd()
    min_a, h_a = math.radians(-60), math.radians(-(300+5))
    glLineWidth(3.0); glBegin(GL_LINES); glVertex3f(0,0,0.0016); glVertex3f(0.55*face_r*math.cos(h_a), 0.55*face_r*math.sin(h_a), 0.0016); glEnd()
    glLineWidth(2.5); glBegin(GL_LINES); glVertex3f(0,0,0.0016); glVertex3f(0.88*face_r*math.cos(min_a), 0.88*face_r*math.sin(min_a), 0.0016); glEnd()
    glPointSize(6); glBegin(GL_POINTS); glVertex3f(0,0,0.0016); glEnd()
    glPopMatrix()

def draw_painting(center, width=2.2, height=1.3, orientation='z'):
    x, y, z = center; thickness=0.03; frame=0.1
    hw, hh = width*0.5, height*0.5; margin, eps = frame, 0.001
    if orientation=='z':
        draw_cube((x,y,z), (width,height,thickness), COLOR_FRAME); plane = z+thickness/2+eps
        L,R = x-hw+margin, x+hw-margin; B,T = y-hh+margin, y+hh-margin
    else:
        draw_cube((x,y,z), (thickness,height,width), COLOR_FRAME); plane = x+thickness/2+eps
        L,R = z-hw+margin, z+hw-margin; B,T = y-hh+margin, y+hh-margin
    sky_top,sky_h,sea_t,sea_b,sand,sun = (0.66,0.82,0.95),(0.86,0.92,0.98),(0.07,0.4,0.65),(0.12,0.6,0.7),(0.93,0.86,0.65),(1,0.93,0.55)
    inner_h = T-B; horizon, sand_h = B+inner_h*0.6, inner_h*0.16; sea_top_y, sea_bot_y = horizon-inner_h*0.02, B+sand_h
    glDisable(GL_CULL_FACE)
    if orientation=='z':
        glBegin(GL_QUADS); glColor3fv(sky_top); glVertex3f(L,T,plane); glVertex3f(R,T,plane); glColor3fv(sky_h); glVertex3f(R,horizon,plane); glVertex3f(L,horizon,plane); glEnd()
        glBegin(GL_QUADS); glColor3fv(sea_t); glVertex3f(L,sea_top_y,plane); glVertex3f(R,sea_top_y,plane); glColor3fv(sea_b); glVertex3f(R,sea_bot_y,plane); glVertex3f(L,sea_bot_y,plane); glEnd()
        glBegin(GL_QUADS); glColor3fv(sand); glVertex3f(L,B,plane); glVertex3f(R,B,plane); glVertex3f(R,B+sand_h,plane); glVertex3f(L,B+sand_h,plane); glEnd()
        glPushMatrix(); glTranslatef(R-inner_h*0.3, T-inner_h*0.2, 0); draw_disk_xy(inner_h*0.12, plane+0.0015, sun, 72); glPopMatrix()
    glEnable(GL_CULL_FACE)

# --- FACHADA / EXTERIOR ---
def draw_balcony(center, size):
    x,y,z = center
    sx,sz = size
    balcony_height = 1.0
    draw_cube((x, y, z+sz/2), (sx+0.1, 0.2, sz+0.1), COLOR_MOLDING)
    draw_cube((x, y+balcony_height, z+sz), (sx+0.1, 0.08, 0.08), COLOR_BALCONY_GRILL)
    draw_cube((x-sx/2, y+balcony_height, z+sz/2), (0.08, 0.08, sz), COLOR_BALCONY_GRILL)
    draw_cube((x+sx/2, y+balcony_height, z+sz/2), (0.08, 0.08, sz), COLOR_BALCONY_GRILL)
    for i in range(13):
        post_x = (x-sx/2) + (sx/12)*i
        draw_cube((post_x, y+balcony_height/2, z+sz), (0.04, balcony_height, 0.04), COLOR_BALCONY_GRILL)

def draw_ornate_window(center, size):
    x, y, z = center
    sx, sy, sz = size
    draw_arched_opening((x,y,z-0.02), (sx+0.2,sy+0.2,sz), COLOR_MOLDING)
    draw_arched_opening((x,y,z), (sx,sy,sz), COLOR_DOOR_WINDOW)
    draw_cube((x, y, z+0.01), (sx*0.9, 0.05, 0.02), COLOR_MOLDING)
    for offset in [-0.4, 0.0, 0.4]:
        draw_cube((x+offset, y, z+0.01), (0.05, sy*0.9, 0.02), COLOR_MOLDING)

def draw_building_facade():
    draw_cube((0,4.75,-4.05), (20,9.5,0.1), COLOR_WALL)
    draw_cube((-10.05,4.75,0), (0.1,9.5,8), COLOR_WALL)
    draw_cube((10.05,4.75,0), (0.1,9.5,8), COLOR_WALL)
    draw_cube((0,6.15,4.0), (20,6.7,0.1), COLOR_WALL)
    draw_cube((-5.55,1.4,4.0), (8.9,2.8,0.1), COLOR_WALL)
    draw_cube((5.55,1.4,4.0), (8.9,2.8,0.1), COLOR_WALL)
    draw_cube((0,3.5,4.1), (20.5,0.4,0.3), COLOR_MOLDING)
    draw_cube((0,6.5,4.1), (20.5,0.4,0.3), COLOR_MOLDING)
    draw_cube((0,9.5,4.1), (20.5,0.4,0.3), COLOR_MOLDING)
    for i in [-4,-3,-2,2,3,4]:
        draw_arched_opening((i*2.2, 1.4, 4.06), (1.6,2.8,0.1), COLOR_DOOR_WINDOW)
        draw_balcony((i*2.2, 0, 4.0), (1.8,0.6))
    for floor in [1, 2]:
        y = 1.4 + (floor*3.0)
        for i in range(-4, 5):
            draw_ornate_window((i*2.2, y, 4.06), (1.6,2.2,0.1))
            draw_balcony((i*2.2, y-1.3, 4.0), (1.8,1.0))
    draw_cube((0,10.5,2), (4,1.5,5), COLOR_MOLDING)
    draw_cube((0,11.2,2), (4.2,0.2,5.2), COLOR_ROOF)
    draw_ornate_window((0,10.5,4.55), (1.0,1.2,0.1))

def draw_interactive_double_door(is_open):
    angle = 90 if is_open else 0
    dw, dh, dt = 1.1, 2.8, 0.1
    glPushMatrix(); glTranslatef(-1.1,0,4.0+dt/2); glRotatef(angle,0,1,0); glTranslatef(dw/2,dh/2,0)
    draw_cube((0,0,0), (dw,dh,dt), COLOR_DOOR_WINDOW); glPopMatrix()
    glPushMatrix(); glTranslatef(1.1,0,4.0+dt/2); glRotatef(-angle,0,1,0); glTranslatef(-dw/2,dh/2,0)
    draw_cube((0,0,0), (dw,dh,dt), COLOR_DOOR_WINDOW); glPopMatrix()

def draw_ramp():
    ramp_color, handrail_color = (0.7,0.7,0.7), (0.4,0.4,0.4)
    glBegin(GL_QUADS); glColor3fv(ramp_color)
    glVertex3f(-2.5,0.5,4.1); glVertex3f(2.5,0.5,4.1); glVertex3f(2.5,0,8); glVertex3f(-2.5,0,8)
    glEnd()
    for side in [-1, 1]:
        x = 2.4*side
        for i in range(5):
            t = i/4.0
            draw_cube((x, (0.5-t*0.5)+0.5, 4.1+t*3.9), (0.05,1,0.05), handrail_color)
        glColor3fv(handrail_color); glLineWidth(5.0)
        glBegin(GL_LINES); glVertex3f(x,1.5,4.1); glVertex3f(x,1,8); glEnd()

def draw_ground():
    glColor3fv(COLOR_GROUND)
    glBegin(GL_QUADS)
    glVertex3f(-40,0,-40); glVertex3f(-40,0,40); glVertex3f(40,0,40); glVertex3f(40,0,-40)
    glEnd()

# --- INTERIOR ---
def draw_wood_floor(center, size, plank_width=0.45):
    cx,cy,cz=center; sx,_,sz=size
    x_min,x_max=cx-sx/2.0,cx+sx/2.0; z_min,z_max=cz-sz/2.0,cz+sz/2.0
    y_top,y_line = cy,cy+0.0007
    n_planks = max(1, int(math.ceil((x_max-x_min)/plank_width)))
    real_w = (x_max-x_min)/n_planks
    for i in range(n_planks):
        x0,x1 = x_min+i*real_w, x_min+(i+1)*real_w
        f = 0.9 + 0.12 * (0.5+0.5*math.sin(i*2.1)*math.cos(i*0.7))
        plank_color = tuple(min(1.0, c*f) for c in COLOR_WOOD_FLOOR_BASE)
        glColor3fv(plank_color); glBegin(GL_QUADS)
        glVertex3f(x0,y_top,z_min); glVertex3f(x0,y_top,z_max); glVertex3f(x1,y_top,z_max); glVertex3f(x1,y_top,z_min)
        glEnd()
        glLineWidth(1.5); glColor3fv(COLOR_WOOD_FLOOR_SEAM); glBegin(GL_LINES)
        glVertex3f(x0,y_line,z_min); glVertex3f(x0,y_line,z_max); glEnd()
    glLineWidth(1.5); glColor3fv(COLOR_WOOD_FLOOR_SEAM); glBegin(GL_LINES)
    glVertex3f(x_max,y_line,z_min); glVertex3f(x_max,y_line,z_max); glEnd()

def draw_interior(hide_exterior=False):
    draw_cube((-10.25,4.75,0), (0.5,9.5,8), COLOR_INTERIOR_WALL)
    draw_cube((10.25,4.75,0), (0.5,9.5,8), COLOR_INTERIOR_WALL)
    draw_cube((0,4.75,-4.25), (20.5,9.5,0.5), COLOR_INTERIOR_WALL)
    draw_wood_floor(center=(0,FLOOR_Y,0), size=(20,0,8))
    place_bookshelf((-7.6,0,-2.4),'+Z'); place_bookshelf((7.6,0,-2.4),'+Z')
    place_bookshelf((-7.6,0,2.6),'-Z'); place_bookshelf((7.6,0,2.6),'-Z')
    draw_table((5,0,-1)); draw_chair((4.2,0,-1),90)
    draw_counter((0,0,-3)); draw_plant((8,0,2))
    draw_round_table_with_chairs(center=(-2,0,1.5), table_radius=0.8)
    draw_wall_clock(center=(-9.95,3.2,-0.6), radius=0.5, orientation='x')
    draw_painting(center=(0,2.2,-3.95), width=2.2, height=1.3, orientation='z')
    if hide_exterior:
        draw_cube((0,4.75,3.95), (20,9.5,0.1), COLOR_INTERIOR_WALL)

# --- LÓGICA PRINCIPAL ---
def is_inside_building(cam_pos):
    x,_,z = cam_pos
    return (-10 < x < 10) and (-4 < z < 4)

def main():
    pygame.init()
    display_size = (1280, 720)
    pygame.display.set_mode(display_size, DOUBLEBUF|OPENGL)
    pygame.display.set_caption("Biblioteca Pública Estadual de Alagoas - Maceió")
    glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glCullFace(GL_BACK)
    gluPerspective(45, (display_size[0]/display_size[1]), 0.1, 100.0)
    camera = Camera(position=[0,1.8,25], yaw=-90) # Posição inicial
    is_door_open = False
    pygame.mouse.set_visible(False); pygame.event.set_grab(True)
    clock = pygame.time.Clock()
    running = True
    print("\n--- CONTROLES ---\nW,A,S,D: Mover\nMouse: Olhar\nEspaço: Pular\nF: Abrir/Fechar Porta\nESC: Sair\n-----------------")
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE): running=False
            if event.type==pygame.KEYDOWN and event.key==pygame.K_f: is_door_open = not is_door_open
        mouse_rel = pygame.mouse.get_rel()
        camera.process_mouse(mouse_rel[0], mouse_rel[1]); camera.update(keys)
        inside = is_inside_building(camera.position)
        glClearColor(*(COLOR_INTERIOR_WALL if inside else (0.5,0.8,1.0)), 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glPushMatrix(); camera.look()
        if not inside:
            draw_ground()
            glPushMatrix(); glTranslatef(0,0.5,0)
            draw_building_facade()
            draw_interior(hide_exterior=False)
            glPopMatrix()
            draw_ramp()
        else:
            glPushMatrix(); glTranslatef(0,0.5,0)
            draw_interior(hide_exterior=True)
            glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.5,0)
        draw_interactive_double_door(is_door_open)
        glPopMatrix()
        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()