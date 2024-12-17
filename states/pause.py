import pygame

from states.state import State


class PauseMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.stopEffects()
        self.options = {0: "Resume", 1: "Quit", 2: "Sound"}
        self.option_choice = 0
        self.option_cooldown = 0

        self.button = pygame.Rect(0, 0, 350, 75)
        self.button.center = (400, 300)

        self.buttonGlow = pygame.Rect(0, 0, 356, 81)
        self.buttonGlow.center = (400, 300 + (self.option_choice * 100))

        self.menuBg = pygame.Rect(0, 0, 450, 450)
        self.menuBg.center = (400, 360)

        self.menuBgGlow = pygame.Rect(0, 0, 456, 456)
        self.menuBgGlow.center = (400, 360)

        self.volumeBar = pygame.Rect(301, 481, 255, 38)

    def update(self, delta_time, actions):
        # Unpause using escape key
        if not actions["escape"]:
            self.playEffects()
            self.exit_state()

        # Select option
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
        self.buttonGlow.center = (400, 300 + (self.option_choice * 100))

        self.volumeBar.width = self.game.master_volume * 127

    def render(self, display):

        # Menu background glow
        pygame.draw.rect(display, (255, 255, 255), self.menuBgGlow)
        # Menu background
        display.blit(self.game.pauseMenuBackground, self.menuBg)

        # Pause text and Pause text shadow
        self.game.draw_text(display, "Paused", (0, 0, 0), 406, 206, self.game.font1_1)
        self.game.draw_text(display, "Paused", (255, 255, 255), 400, 200, self.game.font1_1)

        # Glow around selected option
        pygame.draw.rect(display, (255, 255, 255), self.buttonGlow)

        # Option Buttons
        for i in range(len(self.options) - 1):
            self.button.center = (400, 300 + (i * 100))
            display.blit(self.game.pauseMenuButton, self.button)

        # Volume Button
        self.button.center = (400, 300 + (2 * 100))
        display.blit(self.game.pauseMenuVolumeButton, self.button)
        pygame.draw.rect(display, (255, 255, 255), self.volumeBar)

        # Option button info
        self.game.draw_text(display, "Resume", (255, 255, 255), 400, 305, self.game.font1_1)
        self.game.draw_text(display, "Quit Game", (255, 255, 255), 400, 403, self.game.font1_1)

        # Volume Icon
        if self.game.master_volume == 0:
            display.blit(self.game.volume_icons[0], (240, 475))
        elif self.game.master_volume < 1:
            display.blit(self.game.volume_icons[1], (240, 475))
        elif self.game.master_volume < 1.75:
            display.blit(self.game.volume_icons[2], (240, 475))
        else:
            display.blit(self.game.volume_icons[3], (240, 475))

    def stopEffects(self):
        # Pause sound effects
        self.game.effects_channel1.pause()
        self.game.effects_channel2.pause()
        self.game.effects_channel3.pause()

        # Play pause sound effect
        self.game.pause_sound.set_volume(.5 * self.game.master_volume)
        self.game.buttons_channel.play(self.game.pause_sound)

    def playEffects(self):
        # Resume sound effects
        self.game.effects_channel1.unpause()
        self.game.effects_channel2.unpause()
        self.game.effects_channel3.unpause()

        # Play unpause sound effect
        self.game.unpause_sound.set_volume(.5 * self.game.master_volume)
        self.game.buttons_channel.play(self.game.unpause_sound)

    def select_option(self, option):
        match option:
            # Resume
            case 0:
                self.game.reset_keys()
                self.playEffects()
                self.exit_state()

            # Back to Title Screen
            case 1:
                self.game.reset_keys()
                self.exit_state()
                self.exit_state()

            # Change volume
            case 2:
                self.game.actions["space"] = False
                self.game.volume_choice += 1

                if self.game.volume_choice >= len(self.game.volume_options):
                    self.game.volume_choice = 0

                self.game.master_volume = self.game.volume_options[self.game.volume_choice]
