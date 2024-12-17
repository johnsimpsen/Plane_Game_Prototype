import pygame
import json

from states.state import State


class Quit(State):
    def __init__(self, game):
        State.__init__(self, game)

        self.options = {0: "Yes", 1: "No"}
        self.option_choice = 1
        self.option_cooldown = 0

        self.button = pygame.Rect(0, 0, 184, 75)
        self.button.center = (400, 400)

        self.buttonGlow = pygame.Rect(0, 0, 190, 81)
        self.buttonGlow.center = (311 + (self.option_choice * 210), 380)

        self.quitBg = pygame.Rect(0, 0, 450, 290)
        self.quitBg.center = (400, 300)

        self.quitBgGlow = pygame.Rect(0, 0, 456, 296)
        self.quitBgGlow.center = (400, 300)

    def update(self, delta_time, actions):
        # Back to title menu
        if actions["escape"]:
            self.exit_state()
            self.game.reset_keys()

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
        self.buttonGlow.center = (298 + (self.option_choice * 210), 380)

    def render(self, display):
        #Black background
        display.fill((0, 0, 0))

        # Menu background glow
        pygame.draw.rect(display, (255, 255, 255), self.quitBgGlow)

        # Menu background
        display.blit(self.game.quitMenuBackground, self.quitBg)

        # Menu info
        self.game.draw_text(display, "Are you sure?", (255, 255, 255), 400, 260, self.game.font1_1)

        # Glow around selected option
        pygame.draw.rect(display, (255, 255, 255), self.buttonGlow)

        # Option Buttons
        self.button.center = (298, 380)
        display.blit(self.game.quitMenuQuitButton, self.button)

        self.button.center = (298 + 210, 380)
        display.blit(self.game.quitMenuButton, self.button)

        # Option button info
        self.game.draw_text(display, "Yes", (255, 255, 255), 300, 385, self.game.font1_1)
        self.game.draw_text(display, "No", (255, 255, 255), 510, 385, self.game.font1_1)

    def select_option(self, option):
        match option:
            # Yes
            case 0:
                # Save the game
                with open("save.json", "w") as file:
                    json.dump({"highscore": self.game.highscore,
                               "prevscore": self.game.prevscore}, file)

                self.game.running = False
                self.game.playing = False

            # No
            case 1:
                self.exit_state()
                self.game.reset_keys()
