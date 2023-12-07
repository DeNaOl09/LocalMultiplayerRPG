import pygame as pg
import socket as sc
from time import time

WIDTHWIN, HEIGHTWIN = 1200, 1000

gsocket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
gsocket.setsockopt(sc.IPPROTO_TCP, sc.TCP_NODELAY, 1)
ip = input('Введите IP >>> ')
nick = input('Введите ник >>> ')

playerclass = input('Выберите класс: 1-варвар: ')


class Button:
    def __init__(self, x, y, pic):
        self.img = pic
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        window.blit(self.img, (self.rect.x, self.rect.y))

        if pg.mouse.get_pressed()[0]:
            mx, my = pg.mouse.get_pos()
            if self.rect.x <= mx <= self.rect.x+self.rect.width:
                if self.rect.y <= my <= self.rect.y+self.rect.height:
                    return True

        return False


class Cell:
    def __init__(self, x, y, type, enemy):
        self.x = int(x)
        self.y = int(y)
        self.type = type
        self.enemy = enemy

    def draw(self):
        dirt = pg.image.load('images/dirt.png')
        grass = pg.image.load('images/grass.png')
        sand = pg.image.load('images/sand.png')

        if self.type == 'dirt':
            window.blit(dirt, (self.x, self.y))
        elif self.type == 'grass':
            window.blit(grass, (self.x, self.y))
        elif self.type == 'sand':
            window.blit(sand, (self.x, self.y))

        if self.x == selected[0] and self.y == selected[1]:
            pg.draw.rect(window, (255, 0, 255), (self.x, self.y, 100, 100), 5)


hp = 0
dmg = 0
x = 100
y = 100

pg.font.init()
mfont = pg.font.SysFont('Arial', 24)

buttons = []
walk = Button(1000, 0, pg.image.load('images/go.png'))

if playerclass == '1':
    hp = 100
    dmg = 5
    skin = pg.image.load('images/barbarian1.png')

handshake = f'{x}@{y}@{hp}@{dmg}@{nick}'

while True:
    try:
        gsocket.connect((ip, 5555))
        print('Подключился')
        gsocket.send(handshake.encode())
        print('Отправил handshake')
        break
    except:
        print('Не удалось подключиться к серверу :(')
        print('Повторяю попытку')

window = pg.display.set_mode((WIDTHWIN, HEIGHTWIN))
pg.display.set_caption('LocalMultiplayer.')
clock = pg.time.Clock()

running = True
selected = (-1, -1)
clickcd = time()
info_text = mfont.render('', True, (0, 255, 255))
infocd = time()

while running:
    clock.tick(60)

    window.fill((227, 62, 14))

    '''Отправляем перемещения'''
    gsocket.send(f'{x} {y}'.encode())

    '''Принимаю состояние игрового поля'''
    data = gsocket.recv(4096)
    data = data.decode()
    data = data.split('-')
    cells = []
    for cell in data:
        info = cell.split(';')
        if len(info) == 4:
            cells.append(Cell(info[0], info[1], info[2], info[3]))

    if walk.update():
        if (selected[0] - x)**2 + (selected[1] - y)**2 <= 200**2:
            x, y = selected[0], selected[1]
        else:
            info_text = mfont.render('Слишком далеко!', True, (0, 255, 255))
            infocd = time()

    if time()-infocd <= 5:
        window.blit(info_text, (1000, 500))

    '''Обработка событий'''
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    if pg.mouse.get_pressed()[0]:
        if time()-clickcd >= 0.3:
            mx, my = pg.mouse.get_pos()
            mx = mx//100*100
            my = my//100*100
            for cell in cells:

                if cell.x == mx and cell.y == my:
                    if cell.x == selected[0] and cell.y == selected[1]:
                        selected = (-1, -1)
                    else:
                        selected = (cell.x, cell.y)
                    break

            clickcd = time()

    '''Отрисовка игрового поля'''
    dirt = pg.image.load('images/dirt.png')
    grass = pg.image.load('images/grass.png')
    sand = pg.image.load('images/sand.png')

    for cell in cells:
        cell.draw()

    window.blit(skin, (x, y))

    pg.display.update()

