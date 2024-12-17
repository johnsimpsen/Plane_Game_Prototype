import pygame
import time
import json

from states.title import Title


class Game(object):
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.set_num_channels(64)
        pygame.display.set_caption("Plane Game")

        self.music_channel = pygame.mixer.Channel(0)
        self.buttons_channel = pygame.mixer.Channel(1)
        self.effects_channel1 = pygame.mixer.Channel(2)
        self.effects_channel2 = pygame.mixer.Channel(3)
        self.effects_channel3 = pygame.mixer.Channel(4)

        self.volume_options = (0, .25, .5, .75, 1, 1.25, 1.5, 1.75, 2)
        self.volume_choice = 4
        self.master_volume = self.volume_options[self.volume_choice]

        self.GAME_WIDTH = 800
        self.GAME_HEIGHT = 1000
        self.WIN_WIDTH = 800
        self.WIN_HEIGHT = 1000
        self.resolutions = [(800, 1000),
                            (864, 1080),
                            (1152, 1440)]

        self.resolution_num = 0
        self.game_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT), pygame.RESIZABLE)
        self.info = pygame.display.Info()
        self.fullscreen = False
        self.running = True
        self.playing = True
        self.actions = {"start": False, "left": False, "right": False, "up": False, "down": False,
                        "space": False, "escape": False}

        # Save file
        self.save = {"highscore": 0,
                     "prevscore": 0}

        # Load save file
        with open("save.json", "r") as file:
            save = json.load(file)

        self.highscore = save["highscore"]
        self.prevscore = save["prevscore"]
        self.score = 0

        self.dt = 0
        self.prev_time = 0
        self.state_stack = []
        self.load_assets()
        self.load_states()

    def game_loop(self):
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        #print(self.actions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save the game
                with open("save.json", "w") as file:
                    json.dump({"highscore": self.highscore,
                               "prevscore": self.prevscore}, file)

                self.playing = False
                self.running = False

                self.info = pygame.display.Info()
                self.GAME_WIDTH = self.info.current_w
                self.GAME_HEIGHT = self.info.current_h
                self.win = pygame.display.set_mode((self.info.current_w, self.info.current_h))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    if self.resolution_num >= len(self.resolutions) - 1:
                        self.resolution_num = 0
                    else:
                        self.resolution_num += 1

                    self.GAME_WIDTH = self.resolutions[self.resolution_num][0]
                    self.GAME_HEIGHT = self.resolutions[self.resolution_num][1]
                    self.win = pygame.display.set_mode(self.resolutions[self.resolution_num])

                if event.key == pygame.K_ESCAPE:
                    self.actions["escape"] = not self.actions["escape"]
                if event.key == pygame.K_RETURN:
                    self.actions["start"] = True
                if event.key == pygame.K_a:
                    self.actions["left"] = True
                if event.key == pygame.K_d:
                    self.actions["right"] = True
                if event.key == pygame.K_w:
                    self.actions["up"] = True
                if event.key == pygame.K_s:
                    self.actions["down"] = True
                if event.key == pygame.K_SPACE:
                    self.actions["space"] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.actions["left"] = False
                if event.key == pygame.K_d:
                    self.actions["right"] = False
                if event.key == pygame.K_w:
                    self.actions["up"] = False
                if event.key == pygame.K_s:
                    self.actions["down"] = False
                if event.key == pygame.K_SPACE:
                    self.actions["space"] = False

    def update(self):
        #print(self.actions)
        self.state_stack[-1].update(self.dt, self.actions)
        self.get_dt()

    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.win.blit(pygame.transform.scale(self.game_canvas, (self.GAME_WIDTH, self.GAME_HEIGHT)), (0, 0))
        pygame.display.flip()

    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now

    @staticmethod
    def draw_text(surface, text, color, x, y, font):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        # Sprites / Background ************************************************************

        self.proj_spr = pygame.image.load('./assets/sprites/bullet.png').convert_alpha()

        # Sound Effects / Music ***********************************************************

        self.gun_sound = pygame.mixer.Sound('assets/audio/effects/gun.mp3')
        self.gun_sound.set_volume(.25 * self.master_volume)

        self.explosion_sound = pygame.mixer.Sound('assets/audio/effects/explosion.mp3')
        self.explosion_sound.set_volume(.5 * self.master_volume)

        self.pause_sound = pygame.mixer.Sound('assets/audio/effects/pause.mp3')
        self.pause_sound.set_volume(.5 * self.master_volume)

        self.unpause_sound = pygame.mixer.Sound('assets/audio/effects/unpause.mp3')
        self.unpause_sound.set_volume(.5 * self.master_volume)

        # Fonts ***************************************************************************

        self.font1_0 = pygame.font.Font('./assets/fonts/FFF Forward.TTF', 48)
        self.font1_1 = pygame.font.Font('./assets/fonts/FFF Forward.TTF', 36)

        # GUI *****************************************************************************

        self.titleMenuButton = pygame.image.load('assets/gui/title_button.png').convert()
        self.titleMenuQuitButton = pygame.image.load('assets/gui/title_red_button.png').convert()
        self.titleMenuBackground = pygame.image.load('assets/gui/title_bg.png').convert()

        self.quitMenuButton = pygame.image.load('assets/gui/quit_button.png').convert()
        self.quitMenuQuitButton = pygame.image.load('assets/gui/quit_red_button.png').convert()
        self.quitMenuBackground = pygame.image.load('assets/gui/quit_bg.png').convert()

        self.pauseMenuButton = pygame.image.load('assets/gui/pause_button.png').convert()
        self.pauseMenuVolumeButton = pygame.image.load('assets/gui/pause_volume_button.png').convert()
        self.pauseMenuBackground = pygame.image.load('assets/gui/pause_bg.png').convert()

        self.volume_icons = [pygame.image.load('assets/gui/mute_volume.png').convert_alpha(),
                             pygame.image.load('assets/gui/low_volume.png').convert_alpha(),
                             pygame.image.load('assets/gui/medium_volume.png').convert_alpha(),
                             pygame.image.load('assets/gui/full_volume.png').convert_alpha()]

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False

    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)


if __name__ == "__main__":
    g = Game()
    while g.running:
        g.game_loop()
