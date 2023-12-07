import socket as sc
import pygame as pg
from random import randint
from math import sqrt

'''Сервер'''
clock = pg.time.Clock()
FPS = 100
WIDTH_ROOM, HEIGHT_ROOM = 1000, 1000


class Enemy:
    def __init__(self, hp, dmg):
        self.hp = hp
        self.dmg = dmg


class Cell:
    def __init__(self, x, y, type, enemy):
        self.x = x
        self.y = y
        self.type = type
        self.enemy = enemy


class Player:
    def __init__(self, x, y, hp, damage, nick, sock, addr):
        self.x = x
        self.y = y
        self.hp = hp
        self.dmg = damage
        self.sock = sock
        self.addr = addr
        self.nick = nick

    def move(self, cx, cy):
        self.x = cx
        self.y = cy


s = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
s.setsockopt(sc.IPPROTO_TCP, sc.TCP_NODELAY, 1)

playersq = int(input('Введите кол-во игроков: '))

window = pg.display.set_mode((400, 400))
pg.display.set_caption('LocalMultiplayerServer')

s.bind(('', 5555))
s.setblocking(False)
s.listen(playersq)
print('Готов!')
server_works = True
players = []
cells = []
enemies = []

for i in range(10):
    for j in range(10):
        rand = randint(1, 10)
        if 1 <= rand <= 4:
            newcell = Cell(j * 100, i * 100, 'dirt', False)
        elif 6 <= rand <= 10:
            newcell = Cell(j * 100, i * 100, 'grass', False)
        elif rand == 5:
            newcell = Cell(j * 100, i * 100, 'sand', Enemy(15, 3))
            if newcell.x == 100 and newcell.y == 100:
                newcell = Cell(j * 100, i * 100, 'sand', False)

        cells.append(newcell)

'''Цикл сервера'''
while server_works:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            server_works = False

    fps = round(clock.get_fps())

    '''Проверяем новые подключения'''
    try:
        new_sock, addr = s.accept()
        new_sock.setblocking(False)

        newplayerinfo = new_sock.recv(2048).decode()
        newplayerinfo = list(newplayerinfo.split('@'))

        newplayer = Player(int(newplayerinfo[0]), int(newplayerinfo[1]), int(newplayerinfo[2]), int(newplayerinfo[3]),
                           newplayerinfo[4], new_sock, addr)
        players.append(newplayer)
        print(f'Новый игрок подключился, адрес: {addr}, ник: {newplayerinfo[4]}')

    except:
        pass

    '''Считывание данных от пользователей и отправка состояния игрового поля'''
    for player in players:
        try:
            data = player.sock.recv(2048)
            data = data.decode().split('-')
            moveto = data[0].split()
            player.move(int(moveto[0]), int(moveto[1]))
            takendamage = data[1].split()

            if len(takendamage) > 1:
                for cell in cells:
                    if cell.x == int(takendamage[0]) and cell.y == int(takendamage[1]):
                        if cell.enemy:
                            cell.enemy.hp -= int(takendamage[2])
                            if cell.enemy.hp <= 0:
                                cell.enemy = False

            senddata = ''

            for cell in cells:
                dx, dy = abs(player.x-cell.x), abs(player.y-cell.y)
                if dx**2+dy**2 <= 1200**2:
                    if cell.enemy:
                        senddata += f'{cell.x};{cell.y};{cell.type};{cell.enemy.hp};{cell.enemy.dmg}-'
                    else:
                        senddata += f'{cell.x};{cell.y};{cell.type};{False}-'

            player.sock.send(senddata.encode())

        except:
            pass

    pg.display.flip()
