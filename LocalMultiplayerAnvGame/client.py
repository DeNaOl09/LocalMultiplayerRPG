import pygame as pg
import socket as sc

WIDTHWIN, HEIGHTWIN = 1000, 1000

gsocket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
gsocket.setsockopt(sc.IPPROTO_TCP, sc.TCP_NODELAY, 1)
ip = input('Введите IP >>> ')
nick = input('Введите ник >>> ')

playerclass = input('Выберите класс: 1-варвар: ')


class Cell:
    def __init__(self, x, y, type, enemy):
        self.x = x
        self.y = y
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

while running:
    clock.tick(60)

    '''Принимаю состояние игрового поля'''
    data = gsocket.recv(4096)
    data = data.decode()
    data = data.split('-')
    cells = []
    for cell in data:
        info = cell.split(';')
        if info:
            cells.append(Cell(info[0], info[1], info[2], info[3]))

    '''Обработка событий'''
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.mouse.get_pressed()[0]:
            mx, my = pg.mouse.get_pos()
            for cell in cells:
                if cell.x == mx and cell.y == my:
                    if cell.x == selected[0] and cell.y == selected[1]:
                        selected = (-1, -1)
                    else:
                        selected = (cell.x, cell.y)

    gsocket.send(f'{x} {y}'.encode())

    '''Отрисовка игрового поля'''
    dirt = pg.image.load('images/dirt.png')
    grass = pg.image.load('images/grass.png')
    sand = pg.image.load('images/sand.png')

    for cell in cells:
        cell.draw()

    pg.display.update()

