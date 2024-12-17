import pygame

from states.state import State


class GameOver(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.timer = 1

        # Update highscore
        if self.game.score > self.game.highscore:
            self.game.highscore = self.game.score

        # Set previous score
        self.game.prevscore = self.game.score

        # Reset score
        self.game.score = 0

    def update(self, delta_time, actions):
        # Option movement cooldown
        if self.timer >= 10000:
            self.exit_state()
            self.exit_state()

        self.timer += self.timer * (delta_time * 10)

    def render(self, surface):
        pass
