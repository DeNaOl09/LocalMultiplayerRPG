import pygame as pg
import socket as sc

WIDTHWIN, HEIGHTWIN = 1000, 1000

gsocket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
gsocket.setsockopt(sc.IPPROTO_TCP, sc.TCP_NODELAY, 1)
ip = input('Введите IP >>> ')
nick = input('Введите ник >>> ')

playerclass = input('Выберите класс: 1-варвар: ')

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
while running:
    clock.tick(60)

    '''Принимаю состояние игрового поля'''
    data = gsocket.recv(4096)
    data = data.decode()
    data = data.split('-')
    cells = []
    for cell in data:
        cells.append(cell.split(';'))

    cells = cells[:-1]

    '''Обработка событий'''
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.mouse.get_pressed()[0]:
            mx, my = pg.mouse.get_pos()

    gsocket.send(f'{x} {y}'.encode())

    '''Отрисовка игрового поля'''
    dirt = pg.image.load('images/dirt.png')
    grass = pg.image.load('images/grass.png')
    sand = pg.image.load('images/sand.png')

    for cell in cells:

        if cell[2] == 'dirt':
            window.blit(dirt, (int(cell[0]), int(cell[1])))
        elif cell[2] == 'grass':
            window.blit(grass, (int(cell[0]), int(cell[1])))
        elif cell[2] == 'sand':
            window.blit(sand, (int(cell[0]), int(cell[1])))

    window.blit(skin, (x, y))

    pg.display.update()
