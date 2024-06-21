import pygame, sys, math, random
from pygame.locals import *

clock = pygame.time.Clock()

pygame.init()

WINDOW_SIZE = pygame.Vector2(1080 * 0.5, 1920 * 0.5)
GRID_LINE_COLOR = (80, 80, 80)

surface = pygame.display.set_mode((WINDOW_SIZE.x, WINDOW_SIZE.y))
pygame.display.set_caption("Sandbox")
font = pygame.font.Font("fonts/sans.ttf", 12)

app_is_running = True

class Atom:
    def __init__(self, symbol: str, weight: float, energy_levels: tuple, color: pygame.Color = pygame.Color(255, 255, 255)) -> None:
        self.weight: float = weight
        self.energy_levels: tuple = energy_levels
        self.symbol: str = symbol
        self.color: color = color
        self.has_moved = False

class Button:
    def __init__(self, rect: pygame.Rect, color: pygame.Color, hint = "Unknow") -> None:
        self.rect = rect
        self.hint = hint
        self.color = color
        self.can_show_hint = False

    def draw(self):
        pygame.draw.rect(surface, self.color, self.rect)
        
        if self.can_show_hint:
            text = font.render(self.hint, True, (255, 255, 255))
            rect = text.get_rect()
            rect.center = pygame.mouse.get_pos()
            rect.y += 32

            surface.blit(text, rect)


    def update(self):
        mouse_position = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_position[0], mouse_position[1]):
            self.can_show_hint = True
        else:
            self.can_show_hint = False


class Grid:
    def __init__(self, amount_slot: int = 32, slot_size: float = 16, position: pygame.Vector2 = pygame.Vector2(100, 100)):
        self.position: pygame.Vector2 = position
        self.amount_slot: int = amount_slot
        self.slot_size: float = slot_size

        self.center()

    def center(self):
        self.position.x = WINDOW_SIZE.x / 2 - (self.amount_slot * self.slot_size / 2)
        self.position.y = WINDOW_SIZE.y / 2 - (self.amount_slot * self.slot_size / 2)

    def draw(self):
        for i in range(0, self.amount_slot + 1):
            pygame.draw.line(surface, GRID_LINE_COLOR,
                (self.position.x + self.slot_size * i, self.position.y + 0),
                (self.position.x + self.slot_size * i, self.position.y + self.slot_size * self.amount_slot))
            pygame.draw.line(surface, GRID_LINE_COLOR,
                (self.position.x + 0, self.position.y + self.slot_size * i),
                (self.position.x + self.slot_size * self.amount_slot, self.position.y + self.slot_size * i))

class Universe:
    def __init__(self) -> None:
        self.grid = Grid()
        self.atoms = [[None for _ in range(self.grid.amount_slot)] for _ in range(self.grid.amount_slot)]
    
    def add_atom(self, position, color = (255, 255, 255)):
        atom_position = (
            int(math.ceil((position.x - self.grid.position.x) / self.grid.slot_size) - 1),
            int(math.ceil((position.y - self.grid.position.y) / self.grid.slot_size) - 1))
        
        if atom_position[0] >= 0 and atom_position[0] <= self.grid.amount_slot - 1 and atom_position[1] >= 0 and atom_position[1] <= self.grid.amount_slot - 1:
            if self.atoms[atom_position[1]][atom_position[0]] == None:
                atom =  Atom('H', 1.008, (1))
                atom.color = color
                self.atoms[atom_position[1]][atom_position[0]] = atom

    def remove_atom(self, position):
        atom_position = (
            int(math.ceil((position.x - self.grid.position.x) / self.grid.slot_size) - 1),
            int(math.ceil((position.y - self.grid.position.y) / self.grid.slot_size) - 1))
        
        if atom_position[0] >= 0 and atom_position[0] <= self.grid.amount_slot - 1 and atom_position[1] >= 0 and atom_position[1] <= self.grid.amount_slot - 1:
            if self.atoms[atom_position[1]][atom_position[0]] != None:
                self.atoms[atom_position[1]][atom_position[0]] = None

    def gravity(self, x, y):
        if x < self.grid.amount_slot and y + 1 < self.grid.amount_slot and x >= 0 and y >= 0 and self.atoms[y][x] != None:
            if self.atoms[y + 1][x] == None and not self.atoms[y][x].has_moved:
                self.atoms[y][x].has_moved = True
                
                if self.atoms[y + 1][x] != None and self.atoms[y + 1][x + 1] == None:
                    self.atoms[y + 1][x + 1] = self.atoms[y][x]
                else:
                    self.atoms[y + 1][x] = self.atoms[y][x]
                self.atoms[y][x] = None
                
            else:
                self.atoms[y][x].has_moved = False

    def update(self):
        for y in range(len(self.atoms)):
            for x in range(len(self.atoms[y])):
                    self.gravity(x, y)

    def draw(self):
        for y in range(len(self.atoms)):
            for x in range(len(self.atoms[y])):
                atom = self.atoms[y][x]
                if atom != None:
                    pygame.draw.rect(surface, atom.color, pygame.Rect(
                            self.grid.position.x + x * self.grid.slot_size,
                            self.grid.position.y + y * self.grid.slot_size,
                            self.grid.slot_size, self.grid.slot_size))
        self.grid.draw()

universe = Universe()
mouse_button_is_down = False
can_update = False

materials = {}

materials["SAND"] = Button(pygame.Rect(32, 24, 32, 32), (255, 227, 87), "Sand")
materials["GRASS"] = Button(pygame.Rect(32 * 2 + 12, 24, 32, 32), (72, 255, 31), "Grass")
materials["DIRT"] = Button(pygame.Rect(32 * 3 + 12 * 2, 24, 32, 32), (122, 67, 0), "Dirt")
materials["WATER"] = Button(pygame.Rect(32 * 4 + 12 * 3, 24, 32, 32), (0, 110, 255), "Water (Solid? XD)")
materials["SNOW"] = Button(pygame.Rect(32 * 5 + 12 * 4, 24, 32, 32), (255, 255, 255), "Snow")

current_atom = materials["SNOW"]

while app_is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_is_running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_button_is_down = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_button_is_down = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                can_update = not can_update

    if mouse_button_is_down and pygame.mouse.get_pressed()[0]:
        universe.add_atom(pygame.Vector2(pygame.mouse.get_pos()), current_atom.color)

    elif mouse_button_is_down and pygame.mouse.get_pressed()[2]:
        universe.remove_atom(pygame.Vector2(pygame.mouse.get_pos()))

    for index, (key, atom) in enumerate(materials.items()):
        if mouse_button_is_down and pygame.mouse.get_pressed()[0] and atom.can_show_hint:
            current_atom = Atom('H', 0, (1), atom.color)

    if can_update:
        universe.update()

    for index, (key, atom) in enumerate(materials.items()):
        atom.update()

    surface.fill((0, 0, 0))

    for index, (key, atom) in enumerate(materials.items()):
        atom.draw()

    universe.draw()

    # lazy to clean code it
    if can_update:
        text = font.render("Gravity: Enabled", True, (255, 255, 255))
        r = text.get_rect()
        r.x = 12
        r.y = 200
        
        surface.blit(text, r)
    else:
        text = font.render("Gravity: Disabled", True, (255, 255, 255))
        r = text.get_rect()
        r.x = 12
        r.y = 200
        
        surface.blit(text, r)

        

    pygame.display.update()
    clock.tick(30)

pygame.quit()
sys.exit()