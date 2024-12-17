import pygame

from states.state import State
from states.game_world import Game_World


class Transition(State):
    def __init__(self, game, dest):
        State.__init__(self, game)
        self.dest = dest
        self.timer = 0

    def update(self, delta_time, actions):
        self.timer += (delta_time * 1000)

        match self.dest:
            case "Game_World":
                new_state = Game_World(self.game)
            case _:
                print("No state loaded")
                new_state = 0

        if self.timer > 200:
            new_state.enter_state()
            self.timer = 0

    def render(self, display):
        pygame.Surface.fill(display, (0, 0, 0,))

        match self.dest:
            case "Game_World":
                self.game.draw_text(display, "Get Ready", (255, 255, 255), 400, 400)
