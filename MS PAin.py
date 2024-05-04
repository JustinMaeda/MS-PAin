import pygame
import random
import os
import PIL
from PIL import Image

pygame.init()
SIZE = [400, 708]
FONT = pygame.font.Font('Font/COMICSANS.TTF', 50)
INSULT_FONT = pygame.font.Font('Font/COMICSANS.TTF', 20)


pygame.mixer.init()
pygame.mixer.music.set_volume(0.03)


def delete_iccfile(image_path):
    img = PIL.Image.open(image_path)
    img.info.pop('icc_profile', None)
    img.save(image_path)


class Player:
    def __init__(self):
        self.x = 50
        self.y = 350
        self.jump = 0
        self.jump_speed = 10
        self.gravity = 10
        self.dead = False
        self.sprite = 0
        self.player_sprites = [pygame.image.load("images/1.png").convert_alpha(),
                             pygame.image.load("images/2.png").convert_alpha(),
                             pygame.image.load("images/dead.png").convert_alpha()]
        # self.img_rect =

    def move(self):
        if self.dead:  # dead player
            self.sprite = 2  # change to dead.png
            # keeps falling until it hits the ground
            if self.y < SIZE[1] - 30:
                self.y += self.gravity
        elif self.y > 0:
            # handling movement while jumping
            if self.jump:
                self.sprite = 1  # change to 2.png
                self.jump_speed -= 1
                self.y -= self.jump_speed
            else:
                # regular falling (increased gravity)
                self.gravity += 0.2
                self.y += self.gravity
        else:
            # in-case where the player reaches the top
            # of the screen
            self.jump = 0
            self.y += 3

    def bottom_check(self):
        # player hits the bottom = DEAD
        if self.y >= SIZE[1] - 30:
            self.dead = True

    def get_rect(self):
        # updated player image rectangle
        img_rect = self.player_sprites[self.sprite].get_rect()
        img_rect[0] = self.x
        img_rect[1] = self.y
        return img_rect


class Pillar:
    def __init__(self, pos):
        # pos == True is top , pos == False is bottom
        self.pos = pos
        self.img = self.get_image()

    def get_rect(self):
        # returns the pillar image rect
        return self.img.get_rect()

    def get_image(self):
        if self.pos:  # image for the top pillar
            return pygame.image.load("images/top.png").convert_alpha()
        else:  # image for the bottom pillar
            return pygame.image.load("images/bottom.png").convert_alpha()


class Options:
    def __init__(self):
        self.score_img = pygame.image.load("images/score.png").convert_alpha()  # score board image
        self.play_img = pygame.image.load("images/play.png").convert_alpha()  # play button image
        self.play_rect = self.play_img.get_rect()
        self.score_rect = self.score_img.get_rect()
        self.align_position()
        self.score = 0
        self.font = FONT

    def align_position(self):
        # aligns the "menu" in certain positions
        self.play_rect.center = (200, 330)
        self.score_rect.center = (200, 220)

    def inc(self):
        # score increased by 1
        self.score += 1

class Tries:
    def __init__(self):
        self.tries = 0
        self.font = FONT

    def inc(self):
        # score increased by 1
        self.tries += 1




class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SIZE[0], SIZE[1]))
        pygame.display.set_caption("MS PAIN")
        pygame.mixer.music.load('audio/Best_Song_ever.mp3')
        pygame.mixer.music.play()

        self.background = pygame.image.load("images/background.png").convert()  # background image
        self.pillar_x = 400
        self.offset = 0
        self.top_p = Pillar(1)  # top pillar
        self.bot_p = Pillar(0)  # bottom pillar
        self.pillar_gap = 160  # gap between pillars, (can be randomised as well)
        self.player = Player()  # player object
        self.score_board = Options()
        self.tries_board = Tries()
        self.passed = False  # allows to keep track of the score

    def pillar_move(self):
        # handling pillar movement in the background
        if self.pillar_x < -100:
            self.offset = random.randrange(-120, 120)
            self.passed = False
            self.pillar_x = 400
        self.pillar_x -= 5

    def run(self):
        clock = pygame.time.Clock()
        done = True
        while done:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # player jumps
                        self.player.jump = 20
                        self.player.gravity = 5
                        self.player.jump_speed = 10
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # clicking on the play button (game reset)
                    if self.player.dead and self.score_board.play_rect.collidepoint(event.pos):
                        self.player.dead = False
                        self.reset()


            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.top_p.img, (self.pillar_x, 0 - self.pillar_gap - self.offset))
            self.screen.blit(self.bot_p.img, (self.pillar_x, 360 + self.pillar_gap - self.offset))
            self.screen.blit(self.player.player_sprites[self.player.sprite], (self.player.x, self.player.y))
            self.pillar_move()
            self.player.move()
            self.player.bottom_check()
            if not self.player.dead:
                self.collision()
                self.show_score()
                self.show_tries()
            else:
                self.game_over()
            pygame.display.flip()

    def get_pillar_rect(self, pillar):
        # returns current pillar rectangle on display
        rect = pillar.get_image().get_rect()
        rect[0] = self.pillar_x
        if pillar.pos:
            # current rect y position for top pillar
            rect[1] = 0 - self.pillar_gap - self.offset
        else:
            # current rect y position for bottom pillar
            rect[1] = 360 + self.pillar_gap - self.offset
        return rect

    def collision(self):
        top_rect = self.get_pillar_rect(self.top_p)
        bot_rect = self.get_pillar_rect(self.bot_p)
        # collision check player <> pillars
        if top_rect.colliderect(self.player.get_rect()) or bot_rect.colliderect(self.player.get_rect()):
            # print(self.player.player_sprites[self.player.sprite].get_rect())
            self.player.dead = True
        # if player passed the pillars
        elif not self.passed and top_rect.right < self.player.x:
            self.score_board.inc()
            self.passed = True

    def reset(self):
        # game values reset
        self.score_board.score = 0
        self.tries_board.inc()
        self.player = Player()
        self.top_p = Pillar(1)
        self.bot_p = Pillar(0)
        self.pillar_x = 400
        self.player.gravity = 10

    def show_score(self):
        # score font
        if self.tries_board.tries < 10:
            score_font = FONT.render("Score: ""{}".format(self.score_board.score),
                                                   True, (255, 80, 80))
            # score font rectangle
            font_rect = score_font.get_rect()
            font_rect.center = (200, 70)
            self.screen.blit(score_font, font_rect)  # show score board font
        else:
            score_font = FONT.render("Score?: ""{}".format(self.score_board.score),
                                     True, (255, 80, 80))
            # score font rectangle
            font_rect = score_font.get_rect()
            font_rect.center = (200, 70)
            self.screen.blit(score_font, font_rect)  # show score board font

    def show_tries(self):
        # score font
        if self.tries_board.tries < 10:
            score_font = FONT.render("Tries: ""{}".format(self.tries_board.tries),
                                                   True, (255, 80, 80))
            # score font rectangle
            font_rect = score_font.get_rect()
            font_rect.center = (200, 20)
            self.screen.blit(score_font, font_rect)  # show score board font
        else:
            score_font = INSULT_FONT.render("You've died kind of alot huh?: ""{}".format(self.tries_board.tries),
                                     True, (255, 80, 80))
            # score font rectangle
            font_rect = score_font.get_rect()
            font_rect.center = (200, 20)
            self.screen.blit(score_font, font_rect)  # show score board font

    def game_over(self):
        # score font
        score_font = FONT.render("{}".format(self.score_board.score),
                                     True, (255, 80, 80))
        # score font rectangle
        font_rect = score_font.get_rect()
        score_rect = self.score_board.score_rect
        play_rect = self.score_board.play_rect  # play button rectangle
        font_rect.center = (200, 230)
        self.screen.blit(self.score_board.play_img, play_rect)  # show play button
        self.screen.blit(self.score_board.score_img, score_rect)  # show score board image
        self.screen.blit(score_font, font_rect)  # show score font

    def start_screen(self):
        clock = pygame.time.Clock()
        BACKGROUND = pygame.image.load('images/background.png').convert()
        BEGIN_IMAGE = pygame.image.load('images/BEGIN_IMAGE.png').convert()


        done = True
        while done:
            clock.tick(60)
            self.screen.blit(BACKGROUND, (0, 0))
            self.screen.blit(BEGIN_IMAGE, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                        self.run()

            pygame.display.update()



os.chdir(os.path.dirname(__file__))
if __name__ == "__main__":
    game = Game()
    game.start_screen()
