import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# --- Paleta de Cores Idealizada (Baseada nas fotos) ---
COLOR_WALL          = (0.98, 0.82, 0.76)  # Salmão/Rosa mais fiel
COLOR_DOOR_WINDOW   = (0.01, 0.22, 0.45)  # Azul forte e profundo
COLOR_MOLDING       = (0.95, 0.94, 0.90)  # Branco/Bege claro para molduras
COLOR_BALCONY_GRILL = (0.45, 0.65, 0.85)  # Azul claro e vibrante para as grades
COLOR_ROOF          = (0.7, 0.45, 0.3)   # Telhado terracota/marrom
COLOR_GROUND        = (0.6, 0.6, 0.6)     # Cinza para o chão/calçada
COLOR_WOOD_DARK     = (0.3, 0.15, 0.05)   # Madeira escura para móveis
COLOR_WOOD_LIGHT    = (0.6, 0.4, 0.2)     # Madeira clara para móveis
COLOR_PLANT_GREEN   = (0.1, 0.5, 0.1)     # Verde para a planta


# CLASSE DA CÂMERA COM FÍSICA

class Camera:
    def __init__(self, position=(0, 1.8, 15), yaw=-90.0, pitch=0.0):
        self.position = np.array(position, dtype=float)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 0.15
        self.sensitivity = 0.12
        self.player_height = 1.8
        self.gravity = -0.015
        self.jump_speed = 0.25
        self.y_velocity = 0
        self.on_ground = True
        self.update_vectors()

    def update_vectors(self):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        self.front = np.array([
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad)
        ])
        self.front = self.front / np.linalg.norm(self.front) if np.linalg.norm(self.front) else self.front
        self.right = np.cross(self.front, np.array([0, 1, 0]))
        self.right = self.right / np.linalg.norm(self.right) if np.linalg.norm(self.right) else self.right
        self.up = np.cross(self.right, self.front)

    def process_mouse(self, dx, dy):
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update_vectors()

    def update(self, keys):
        move_front = np.array([self.front[0], 0, self.front[2]])
        if np.linalg.norm(move_front) > 0:
            move_front /= np.linalg.norm(move_front)
        
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

        ground_level = 0
        if self.position[1] < ground_level + self.player_height:
            self.position[1] = ground_level + self.player_height
            self.y_velocity = 0
            self.on_ground = True

    def look(self):
        look_at_point = self.position + self.front
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            look_at_point[0], look_at_point[1], look_at_point[2],
            self.up[0], self.up[1], self.up[2]
        )


# FUNÇÕES DE DESENHO PRIMITIVAS

def draw_cube(center, size, color):
    x, y, z = center
    sx, sy, sz = size
    glColor3fv(color)
    v = [
        (x-sx/2,y-sy/2,z-sz/2),(x+sx/2,y-sy/2,z-sz/2),(x+sx/2,y+sy/2,z-sz/2),(x-sx/2,y+sy/2,z-sz/2),
        (x-sx/2,y-sy/2,z+sz/2),(x+sx/2,y-sy/2,z+sz/2),(x+sx/2,y+sy/2,z+sz/2),(x-sx/2,y+sy/2,z+sz/2)
    ]
    s=[(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,5,6,2),(0,1,5,4),(3,2,6,7)]
    glBegin(GL_QUADS)
    for surf in s:
        for i in surf:
            glVertex3fv(v[i])
    glEnd()

def draw_arched_opening(center, size, color, arch_ratio=0.8):
    x,y,z = center
    sx,sy,sz = size
    r = sx/2
    
    rh = sy - (r * arch_ratio)
    if rh < 0: rh = 0

    glColor3fv(color)
    # Parte retangular
    glBegin(GL_QUADS)
    glVertex3f(x-sx/2, y-sy/2, z); glVertex3f(x+sx/2, y-sy/2, z)
    glVertex3f(x+sx/2, y-sy/2+rh, z); glVertex3f(x-sx/2, y-sy/2+rh, z)
    glEnd()
    
    # Parte do arco
    acy = y-sy/2+rh
    if arch_ratio > 0.01:
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x, acy, z)
        for i in range(19):
            a = math.radians(i*10)
            dx = r * math.cos(a)
            dy = r * math.sin(a) * arch_ratio
            glVertex3f(x + dx, acy + dy, z)
        glEnd()


# FUNÇÕES DE DESENHO (FACHADA E EXTERIOR)

def draw_balcony(center, size):
    x,y,z = center
    sx,sz = size
    balcony_height = 1.0
    
    # Base da sacada
    draw_cube((x, y, z+sz/2), (sx+0.1, 0.2, sz+0.1), COLOR_MOLDING)

    # Corrimão superior
    draw_cube((x, y + balcony_height, z+sz), (sx+0.1, 0.08, 0.08), COLOR_BALCONY_GRILL)
    draw_cube((x-sx/2, y + balcony_height, z+sz/2), (0.08, 0.08, sz), COLOR_BALCONY_GRILL)
    draw_cube((x+sx/2, y + balcony_height, z+sz/2), (0.08, 0.08, sz), COLOR_BALCONY_GRILL)
    
    # Grades (mais densas para melhor aparência)
    num_posts = 12
    for i in range(num_posts + 1):
        post_x = (x - sx/2) + (sx / num_posts) * i
        draw_cube((post_x, y + balcony_height/2, z+sz), (0.04, balcony_height, 0.04), COLOR_BALCONY_GRILL)

def draw_ornate_window(center, size):
    x, y, z = center
    sx, sy, sz = size
    # Abertura na parede (simulada)
    draw_arched_opening((x, y, z-0.01), (sx, sy, 0.1), (0,0,0))
    # Esquadria azul
    draw_arched_opening((x, y, z), (sx, sy, sz), COLOR_DOOR_WINDOW)

def draw_building_facade():
    # Prédio principal
    draw_cube((0, 4.75, 0), (20, 9.5, 8), COLOR_WALL)

    # Cornijas horizontais
    draw_cube((0, 3.5, 4.05), (20.5, 0.4, 0.3), COLOR_MOLDING)
    draw_cube((0, 6.5, 4.05), (20.5, 0.4, 0.3), COLOR_MOLDING)
    draw_cube((0, 9.5, 4.05), (20.5, 0.4, 0.3), COLOR_MOLDING)
    
    # Portas/janelas do térreo
    for i in [-4, -3, -2, 2, 3, 4]:
        x_pos = i * 2.2
        draw_arched_opening((x_pos, 1.4, 4.05), (1.6, 2.8, 0.1), COLOR_DOOR_WINDOW)
        draw_balcony((x_pos, 0, 4.0), (1.8, 0.6))
        
    # Janelas + sacadas dos andares superiores
    for floor in [1, 2]:
        y_pos = 1.4 + (floor * 3.0)
        for i in range(-4, 5):
            x_pos = i * 2.2
            draw_ornate_window((x_pos, y_pos, 4.05), (1.6, 2.2, 0.1))
            draw_balcony((x_pos, y_pos - 1.1 - 0.2, 4.0), (1.8, 1.0))
            
    # Estrutura do telhado
    draw_cube((0, 10.5, 2), (4, 1.5, 5), COLOR_MOLDING)
    draw_cube((0, 11.2, 2), (4.2, 0.2, 5.2), COLOR_ROOF)
    draw_ornate_window((0, 10.5, 4.55), (1.0, 1.2, 0.1))

def draw_interactive_double_door(is_open):
    angle = 90 if is_open else 0
    door_width, door_height = 1.1, 2.8
    
    # Folha Esquerda
    glPushMatrix()
    glTranslatef(-door_width, 0, 4.0)
    glRotatef(angle, 0, 1, 0)
    draw_arched_opening((door_width/2, door_height/2, 0), (door_width, door_height, 0.1), COLOR_DOOR_WINDOW)
    glPopMatrix()
    
    # Folha Direita
    glPushMatrix()
    glTranslatef(door_width, 0, 4.0)
    glRotatef(-angle, 0, 1, 0)
    draw_arched_opening((-door_width/2, door_height/2, 0), (door_width, door_height, 0.1), COLOR_DOOR_WINDOW)
    glPopMatrix()

def draw_ramp():
    ramp_color = (0.7, 0.7, 0.7)
    handrail_color = (0.4, 0.4, 0.4)
    # Superfície da rampa
    glBegin(GL_QUADS)
    glColor3fv(ramp_color)
    glVertex3f(-2.5, 0.5, 4.1); glVertex3f(2.5, 0.5, 4.1)
    glVertex3f(2.5, 0.0, 8.0); glVertex3f(-2.5, 0.0, 8.0)
    glEnd()
    # Corrimãos
    for side in [-1, 1]:
        x_pos = 2.4 * side
        for i in range(5):
            t = i / 4.0
            z_pos = 4.1 + t * 3.9
            y_pos = 0.5 - t * 0.5
            draw_cube((x_pos, y_pos + 0.5, z_pos), (0.05, 1.0, 0.05), handrail_color)
        
      
        glColor3fv(handrail_color)
        glLineWidth(5.0)
        glBegin(GL_LINES)
        glVertex3f(x_pos, 1.5, 4.1)
        glVertex3f(x_pos, 1.0, 8.0)
        glEnd()

def draw_ground():
    glColor3fv(COLOR_GROUND)
    glBegin(GL_QUADS)
    glVertex3f(-40, 0, -40); glVertex3f(-40, 0, 40)
    glVertex3f(40, 0, 40); glVertex3f(40, 0, -40)
    glEnd()


# FUNÇÕES DE DESENHO (INTERIOR)

def draw_bookshelf(center):
    x,y,z = center
    draw_cube((x, y+1.5, z), (2.0, 3.0, 0.4), COLOR_WOOD_DARK) # Estrutura
    for i in range(5):
        shelf_y = y + 0.2 + i * 0.65
        draw_cube((x, shelf_y, z), (1.9, 0.05, 0.35), COLOR_WOOD_LIGHT) # Prateleiras

def draw_table(center):
    x,y,z = center
    draw_cube((x, y+0.7, z), (1.5, 0.08, 0.8), COLOR_WOOD_LIGHT) # Tampo
    draw_cube((x-0.65, y+0.35, z-0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT) # Pés
    draw_cube((x+0.65, y+0.35, z-0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)
    draw_cube((x-0.65, y+0.35, z+0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)
    draw_cube((x+0.65, y+0.35, z+0.3), (0.08, 0.7, 0.08), COLOR_WOOD_LIGHT)

def draw_chair(center, rotation=0):
    x,y,z = center
    glPushMatrix()
    glTranslatef(x,y,z)
    glRotatef(rotation, 0, 1, 0)
    draw_cube((0, 0.25, 0), (0.5, 0.05, 0.5), COLOR_WOOD_DARK) 
    draw_cube((0, 0.7, -0.2), (0.5, 0.9, 0.05), COLOR_WOOD_DARK) # Encosto
    draw_cube((-0.2, 0, -0.2), (0.05, 0.5, 0.05), COLOR_WOOD_DARK) # Pés
    draw_cube((0.2, 0, -0.2), (0.05, 0.5, 0.05), COLOR_WOOD_DARK)
    draw_cube((-0.2, 0, 0.2), (0.05, 0.5, 0.05), COLOR_WOOD_DARK)
    draw_cube((0.2, 0, 0.2), (0.05, 0.5, 0.05), COLOR_WOOD_DARK)
    glPopMatrix()
    
def draw_counter(center):
    draw_cube(center, (3.0, 1.0, 0.6), COLOR_WOOD_DARK)
    
def draw_plant(center):
    x,y,z = center
    draw_cube((x, y+0.2, z), (0.4, 0.4, 0.4), (0.5, 0.2, 0.1)) # Vaso
    draw_cube((x, y+0.6, z), (0.6, 0.5, 0.6), COLOR_PLANT_GREEN) # Folhagem

def draw_interior():
    # Paredes internas
    wall_color = (0.9, 0.88, 0.85)
    draw_cube((-10.25, 4.75, 0), (0.5, 9.5, 8), wall_color)
    draw_cube((10.25, 4.75, 0), (0.5, 9.5, 8), wall_color)
    draw_cube((0, 4.75, -4.25), (20.5, 9.5, 0.5), wall_color)
    # Chão
    draw_cube((0, 0.01, 0), (20, 0.02, 8), (0.7, 0.6, 0.5))
    
    # --- Posicionando os 5 objetos internos ---
    draw_bookshelf((-8, 0, -2))
    draw_table((5, 0, -1))
    draw_chair((4.2, 0, -1), rotation=90)
    draw_counter((0, 0, -3))
    draw_plant((8, 0, 2))


# FUNÇÃO PRINCIPAL

def main():
    pygame.init()
    display_size = (1280, 720)
    screen = pygame.display.set_mode(display_size, DOUBLEBUF|OPENGL)
    pygame.display.set_caption("Centro Histórico 3D - Biblioteca Pública de Alagoas")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    gluPerspective(45, (display_size[0]/display_size[1]), 0.1, 100.0)

    camera = Camera()
    is_door_open = False

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    clock = pygame.time.Clock()
    running = True

    print("\n--- CONTROLES ---")
    print("W, A, S, D: Mover")
    print("Mouse: Olhar ao redor")
    print("Espaço: Pular")
    print("F: Abrir / Fechar a porta principal")
    print("ESC: Sair")
    print("-----------------\n")

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                is_door_open = not is_door_open
        
        mouse_rel = pygame.mouse.get_rel()
        camera.process_mouse(mouse_rel[0], mouse_rel[1])
        camera.update(keys)

        glClearColor(0.5, 0.8, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        glPushMatrix()
        camera.look()

        draw_ground()
        
        glPushMatrix()
        glTranslatef(0, 0.5, 0) # Eleva todo o prédio para a altura da rampa
        draw_building_facade()
        draw_interactive_double_door(is_door_open)
        draw_interior()
        glPopMatrix()
        
        draw_ramp()

        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()