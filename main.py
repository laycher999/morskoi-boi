from random import randint as r

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел был за пределы доски, попробуйте еще раз!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку, попробуйте еще раз!"

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [(-1, -1), (-1, 0), (-1, 1),(0, -1), (0, 0), (0, 1),(1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        desk = ""
        desk += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            desk += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            desk = desk.replace("■", "O")
        return desk

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "."
        print("Промах!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException:
                print(BoardException)

class AI(Player):
    def ask(self):
        d = Dot(r(0, 5), r(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            try:
                cords = input("Ваш ход: ").split()
                x, y = cords
                return Dot(int(x) - 1, int(y) - 1)
            except:
                print('Введено неверное значение!')

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [1,1,1,1,2,2,3]
        board = Board(size=self.size)
        tries = 0
        for l in lens:
            while True:
                tries += 1
                if tries > 100:
                    return None
                ship = Ship(Dot(r(0, self.size), r(0, self.size)), l, r(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardException:
                    pass
        board.begin()
        return board

    def greet(self):
        print('''
-----------------------------------
|  Приветствую в игре Морской бой |
-----------------------------------
|         Формат ввода            |
-----------------------------------
|        x - по горизонтали       |
|        y - по вертикали         |
-----------------------------------
                        ''')

    def loop(self):
        num = 0
        field = '-' * 27
        while True:
            print(f'''
{field}
Ваша доска:
{self.us.board}
Доска противника:
{self.ai.board}
{field}''')
            if num % 2 == 0:
                repeat = self.us.move()
            else:
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("Вы выиграл!")
                break

            if self.us.board.count == 7:
                print("Противник выиграл!")
                break
            num += 1

    @property
    def start(self):
        self.greet()
        self.loop()

game = Game()
game.start
