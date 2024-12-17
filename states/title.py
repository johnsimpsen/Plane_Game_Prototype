import pygame

from states.state import State
from states.game_world import Game_World
from states.quit import Quit


class Title(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.background = Background(game)

        self.options = {0: "Play", 1: "Settings", 2: "Quit"}
        self.option_choice = 0
        self.option_cooldown = 0

        self.button = pygame.Rect(0, 0, 450, 100)
        self.button.center = (400, 400)

        self.buttonGlow = pygame.Rect(0, 0, 456, 106)
        self.buttonGlow.center = (400, 400 + (self.option_choice * 125))

        self.menuBg = pygame.Rect(0, 0, 600, 650)
        self.menuBg.center = (400, 600)

        self.menuBgGlow = pygame.Rect(0, 0, 606, 656)
        self.menuBgGlow.center = (400, 600)

    def update(self, delta_time, actions):
        #print(self.option_choice)

        # Water background
        self.background.update(delta_time)

        if actions["escape"]:
            self.select_option(2)

        if actions["space"]:
            self.select_option(self.option_choice)

        # Option movement cooldown
        if self.option_cooldown >= 5:
            self.option_cooldown = 0

        if self.option_cooldown > 0:
            self.option_cooldown += self.option_cooldown * (delta_time * 10)

        # Option movement
        if self.option_cooldown == 0:
            if actions["up"] or actions["left"]:
                self.option_choice -= 1
                self.option_cooldown = 1
            if actions["down"] or actions["right"]:
                self.option_choice += 1
                self.option_cooldown = 1

        # Option looping
        if self.option_choice >= len(self.options):
            self.option_choice = 0
        if self.option_choice < 0:
            self.option_choice = len(self.options) - 1

        # Glow around selected option
        self.buttonGlow.center = (400, 365 + (self.option_choice * 125))

    def render(self, display):
        # Water background
        self.background.render(display)

        # Menu background glow
        pygame.draw.rect(display, (255, 255, 255), self.menuBgGlow)

        # Menu background
        display.blit(self.game.titleMenuBackground, self.menuBg)

        #self.game.draw_text(display, "Press Space to Begin", (255, 255, 255), 400, 900)

        # Glow around selected option
        pygame.draw.rect(display, (255, 255, 255), self.buttonGlow)

        # Option Buttons
        for i in range(len(self.options) - 1):
            self.button.center = (400, 365 + (i * 125))
            display.blit(self.game.titleMenuButton, self.button)

        # Quit Button
        self.button.center = (400, 365 + (2 * 125))
        display.blit(self.game.titleMenuQuitButton, self.button)

        # Option button info
        self.game.draw_text(display, "Play", (255, 255, 255), 400, 370, self.game.font1_0)
        self.game.draw_text(display, "Settings", (255, 255, 255), 400, 495, self.game.font1_0)
        self.game.draw_text(display, "Quit", (255, 255, 255), 400, 615, self.game.font1_0)

        #Highscore
        self.game.draw_text(display, f'Highscore: {str(self.game.highscore).zfill(4)}', (34, 34, 34), 406, 756,
                            self.game.font1_0)
        self.game.draw_text(display, f'Highscore: {str(self.game.highscore).zfill(4)}', (106, 106, 106), 400, 750,
                            self.game.font1_0)

        # Highscore
        self.game.draw_text(display, f'Last Score: {str(self.game.prevscore).zfill(4)}', (34, 34, 34), 406, 856,
                            self.game.font1_0)
        self.game.draw_text(display, f'Last Score: {str(self.game.prevscore).zfill(4)}', (106, 106, 106), 400, 850,
                            self.game.font1_0)

    def select_option(self, option):
        match option:
            # Play
            case 0:
                new_state = Game_World(self.game)
                new_state.enter_state()
                self.game.reset_keys()

            # Settings
            case 1:
                pass

            # Quit
            case 2:
                new_state = Quit(self.game)
                new_state.enter_state()
                self.game.reset_keys()


class Background(object):
    def __init__(self, game):
        self.game = game
        self.load_assets()
        self.scroll_bg = 0
        self.bg_speed = 4
        self.bg_height = self.water_bg.get_height()

    def update(self, delta_time):
        # Scroll Background
        self.scroll_bg += self.bg_speed * (delta_time * 100)

        # Reset Scroll
        if self.scroll_bg >= self.bg_height:
            self.scroll_bg = 0

    def render(self, display):
        # Calculate the starting position of the background
        y1 = self.scroll_bg

        # Draw the images in a loop to cover the entire screen height
        for y in range(-self.bg_height, self.game.GAME_HEIGHT, self.bg_height):
            display.blit(self.water_bg, (0, y + y1))

    def load_assets(self):
        self.water_bg = pygame.image.load('assets/backgrounds/water.png').convert()
