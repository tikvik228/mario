import pygame
import os
import sys


def main(num):
    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image


    pygame.init()
    FPS = 50
    WIDTH, HEIGHT = 500, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))


    tile_images = {"wall": load_image('box.png'), "empty": load_image('grass.png')}
    player_image = load_image("mar.png")

    tile_width = tile_height = 50

    class Camera:
        def __init__(self):
            self.dx = 0
            self.dy = 0

        def apply(self, obj):
            return obj.rect.move(self.dx, self.dy)

        def update(self, target):
            self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
            self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)

    class ScreenFrame(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.rect = (0, 0, WIDTH, HEIGHT)


    class SpriteGroup(pygame.sprite.Group):

        def __init__(self):
            super().__init__()

        def get_event(self, event):
            for sprite in self:
                sprite.get_event(event)


    class Sprite(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.rect = None

        def get_event(self, event):
            pass


    class Tile(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(sprite_group)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)


    class Player(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y):
            super().__init__(hero_group)
            self.image = player_image
            self.rect = self.image.get_rect().move(
                tile_width * pos_x + 15, tile_height * pos_y + 5)
            self.pos = (pos_x, pos_y)

        def move(self, x, y):
            self.pos = (x, y)
            self.rect = self.image.get_rect().move(
                tile_width * self.pos[0] + 15, tile_height * self.pos[1] + 5)


    player = None
    running = True
    clock = pygame.time.Clock()
    sprite_group = SpriteGroup()
    hero_group = SpriteGroup()


    def terminate():
        pygame.quit()
        sys.exit()

    def start_screen():
        intro_text = ["ЗАСТАВКА", "",
                      "Правила игры",
                      "Если в правилах несколько строк,",
                      "приходится выводить их построчно"]

        fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)


    def load_level(filename):
        filename = "data/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        # и подсчитываем максимальную длину
        max_width = max(map(len, level_map))
        # дополняем каждую строку пустыми клетками ('.')
        return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))

    def generate_level(level):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Tile('empty', x, y)
                elif level[y][x] == '#':
                    Tile('wall', x, y)
                elif level[y][x] == '@':
                    Tile('empty', x, y)
                    new_player = Player(x, y)
                    level[y][x] = "."
        # вернем игрока, а также размер поля в клетках
        return new_player, x, y

    def move(hero, movement):
        x, y = hero.pos
        if movement == "up":
            if y > 0 and level_map[y - 1][x] == ".":
                hero.move(x, y - 1)
        if movement == "down":
            if y <= max_y - 1 and level_map[y + 1][x] == ".":
                hero.move(x, y + 1)
        if movement == "left":
            if x > 0 and level_map[y][x - 1] == ".":
                hero.move(x - 1, y)
        if movement == "right":
            if x <= max_x - 1 and level_map[y][x + 1] == ".":
                hero.move(x + 1, y)


    start_screen()
    level_map = load_level(f"map{num}.txt")
    camera = Camera()
    hero, max_x, max_y = generate_level(level_map)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move(hero, "up")
                elif event.key == pygame.K_DOWN:
                    move(hero, "down")
                elif event.key == pygame.K_LEFT:
                    move(hero, "left")
                elif event.key == pygame.K_RIGHT:
                    move(hero, "right")
        screen.fill(pygame.Color("black"))
        camera.update(hero)
        for field in sprite_group:
            screen.blit(field.image, camera.apply(field))
        for h in hero_group:
            screen.blit(h.image, camera.apply(h))
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


num = int(input("Введите номер карты (1-4)"))
if 0 < num < 5:
    main(num)
else:
    print("нет такого номера")