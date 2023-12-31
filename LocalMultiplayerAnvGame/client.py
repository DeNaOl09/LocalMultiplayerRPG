import pygame as pg
import socket as sc
from time import time
from random import randint

WIDTHWIN, HEIGHTWIN = 1200, 1000

gsocket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
gsocket.setsockopt(sc.IPPROTO_TCP, sc.TCP_NODELAY, 1)
ip = input('Введите IP >>> ')
nick = input('Введите ник >>> ')

playerclass = input('Выберите класс: 1-варвар, 2-стрелок: ')


class Enemy:
    def __init__(self, hp, dmg):
        self.hp = hp
        self.dmg = dmg


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
        killed = False

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

        if self.enemy:
            if self.enemy.hp <= 0:
                killed = True
            if self.enemy.dmg == 3:
                window.blit(pg.image.load('images/reptiloid.png'), (self.x, self.y))

        if killed:
            self.enemy = False


hp = 0
dmg = 0
x = 100
y = 100

pg.font.init()
mfont = pg.font.SysFont('Arial', 24)

buttons = []
walk = Button(1000, 0, pg.image.load('images/go.png'))
attack = Button(1000, 100, pg.image.load('images/attack.png'))

if playerclass == '1':
    hp = 100
    dmg = 5
    skin = pg.image.load('images/barbarian1.png')
    attackrange = 200
    walkrange = 200

elif playerclass == '2':
    hp = 75
    dmg = 3
    skin = pg.image.load('images/gunslinger1.png')
    attackrange = 600
    walkrange = 300

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
hitcd = time()
hit = False
damaged = 0

while running:
    clock.tick(60)

    window.fill((227, 62, 14))

    '''Отправляем все данные'''
    if damaged:
        gsocket.send(f'{x} {y}-{damaged[0]} {damaged[1]} {damaged[2]}'.encode())
        damaged = 0
    else:
        gsocket.send(f'{x} {y}-'.encode())

    if hp <= 0:
        quit()

    '''Принимаю состояние игрового поля'''
    data = gsocket.recv(4096)
    data = data.decode()
    data = data.split('-')
    cells = []
    for cell in data:
        info = cell.split(';')
        if len(info) == 5:
            if info[3]:
                cells.append(Cell(info[0], info[1], info[2], Enemy(int(info[3]), int(info[4]))))
        elif len(info) == 4:
            cells.append(Cell(info[0], info[1], info[2], False))

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
                    clickcd = time()
                    if cell.x == selected[0] and cell.y == selected[1]:
                        selected = (-1, -1)
                    else:
                        selected = (cell.x, cell.y)
                    break

    if walk.update():
        if (selected[0] - x)**2 + (selected[1] - y)**2 <= walkrange**2:
            for cell in cells:
                if cell.x == selected[0] and cell.y == selected[1]:
                    if not cell.enemy:
                        x, y = selected[0], selected[1]
        else:
            info_text = mfont.render('Слишком далеко!', True, (0, 255, 255))
            infocd = time()

    if attack.update():
        for cell in cells:
            if cell.x == selected[0] and cell.y == selected[1]:
                if cell.enemy:
                    if (selected[0] - x)**2 + (selected[1] - y)**2 <= attackrange**2:
                        if time() - clickcd >= 0.3:
                            hit = (selected[0], selected[1])
                            hitcd = time()
                            cell.enemy.hp -= dmg

                            if randint(1, 2) == 2:
                                if cell.enemy.dmg < 10 and (selected[0] - x) ** 2 + (selected[1] - y) ** 2 <= 200 ** 2:
                                    hp -= cell.enemy.dmg
                                    info_text = mfont.render(f'dmg: {dmg}, hp: -{cell.enemy.dmg}', True, (0, 255, 255))
                                    infocd = time()
                            else:
                                info_text = mfont.render(
                                    f'dmg: {dmg}!', True, (0, 255, 255))
                                infocd = time()

                            damaged = (selected[0], selected[1], dmg)
                            clickcd = time()

                    else:
                        info_text = mfont.render('Слишком далеко!', True, (0, 255, 255))
                        infocd = time()
                else:
                    info_text = mfont.render('Атаковать не кого!', True, (0, 255, 255))
                    infocd = time()

    '''Отрисовка игрового поля'''
    dirt = pg.image.load('images/dirt.png')
    grass = pg.image.load('images/grass.png')
    sand = pg.image.load('images/sand.png')

    for cell in cells:
        cell.draw()

    if hit:
        if time()-hitcd <= 0.5:
            if playerclass == '1':
                window.blit(pg.image.load('images/hit1.png'), hit)
            elif playerclass == '2':
                window.blit(pg.image.load('images/hit2.png'), hit)
            hit = False
            hitcd = time()

    window.blit(skin, (x, y))

    pg.display.update()

