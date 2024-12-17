import pygame
import random

from states.state import State
from states.pause import PauseMenu
from states.game_over import GameOver


class Game_World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game.score = 0
        self.enemies = []
        self.explosions = []
        self.player = Plane(game, 370, 700, 2, 5, self.enemies, self.explosions)
        self.background = Background(game)
        self.gui = game_GUI(game, self.player)
        self.test1 = Enemy1(game, 415, 0, 2, 3, self.player, self.enemies, self.explosions)
        self.test2 = Enemy1(game, 315, 0, 2, 3, self.player, self.enemies, self.explosions)
        self.test3 = Enemy1(game, 215, 0, 2, 3, self.player, self.enemies, self.explosions)
        self.enemies.append(self.test1)
        self.enemies.append(self.test2)
        self.enemies.append(self.test3)
        self.load_assets()

    def update(self, delta_time, actions):

        self.background.update(delta_time)
        self.player.update(delta_time)

        for bullet in self.player.bullets:
            bullet.update(delta_time)

        for enemy in self.enemies:
            enemy.update(delta_time)

        for explosion in self.explosions:
            explosion.update(delta_time)

        if actions["escape"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()

    def render(self, display):
        self.background.render(display)
        self.player.render(display)

        for bullet in self.player.bullets:
            bullet.render(display)

        for enemy in self.enemies:
            enemy.render(display)

        for explosion in self.explosions:
            explosion.render(display)

        self.gui.render(display)

    def load_assets(self):
        pass


class Plane(object):
    def __init__(self, game, x, y, scale, health, enemies, explosions):
        self.game = game
        self.scale = scale
        self.load_assets()
        self.x = x
        self.y = y
        self.vel = 4
        self.width = self.plane1_spr[0].get_width()
        self.height = self.plane1_spr[0].get_height()
        self.current_frame = 0
        self.last_frame_update = 0
        self.health = health
        self.maxHealth = health
        self.lives = 3
        self.bullets = []
        self.maxBullets = 5
        self.bulletCooldown = 50
        self.bulletTimer = 0
        self.enemies = enemies
        self.explosions = explosions
        self.visible = True
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.invincibilityCount = 0
        self.respawnCount = 0

    def update(self, delta_time):
        if self.visible:
            # Movement
            if self.game.actions['left'] and self.x > 0:
                self.x -= self.vel * (delta_time * 100)
            elif self.game.actions['right'] and self.x < (
                    self.game.WIN_WIDTH - (self.plane1_spr[0].get_width() * self.scale)):
                self.x += self.vel * (delta_time * 100)
            if self.game.actions['up'] and self.y > 0:
                self.y -= (self.vel - 1) * (delta_time * 100)
            elif self.game.actions['down'] and self.y < (
                    (self.game.WIN_HEIGHT - 200) - (self.plane1_spr[0].get_height() * self.scale)):
                self.y += (self.vel + 1) * (delta_time * 100)

            # Player Hitbox
            self.hitbox = pygame.Rect(self.x + 15, self.y + 10, (self.width * self.scale) - 30,
                                      (self.height * self.scale) - 20)

            # Propeller Animation
            self.animate(delta_time)

            # Space to shoot bullets
            if self.game.actions['space'] and self.bulletTimer == 0 and len(self.bullets) < self.maxBullets:
                bullet = Projectile(self.x + self.plane1_spr[0].get_width(), self.y,
                                    5, 1, 1, self.game, self)
                self.bullets.append(bullet)

                self.game.gun_sound.set_volume(.25 * self.game.master_volume)
                self.game.effects_channel1.play(self.game.gun_sound)

                # Starts the cooldown of the bullets
                self.bulletTimer = 1

            # Bullet Cooldown
            if self.bulletTimer > 0:
                self.bulletTimer += (delta_time * 100)
            if self.bulletTimer > self.bulletCooldown:
                self.bulletTimer = 0

            for enemy in self.enemies:
                if pygame.Rect.colliderect(self.hitbox, enemy.hitbox) and self.invincibilityCount == 0:
                    self.hit(1)

            # Death check
            if self.health <= 0:
                self.death()

        # Invincibility Frames
        if self.invincibilityCount >= 100:
            self.invincibilityCount = 0

        if self.invincibilityCount > 0:
            self.invincibilityCount += self.invincibilityCount * (delta_time * 10)

        #Respawn Timer
        if self.respawnCount >= 1000:
            self.respawnCount = 0
            self.visible = True

        if self.respawnCount > 0:
            self.respawnCount += self.respawnCount * (delta_time * 10)

    def render(self, display):
        if self.visible:
            display.blit(self.curr_image, (self.x, self.y))

            self.hitbox = pygame.Rect(self.x + 15, self.y + 10, (self.width * self.scale) - 30,
                                      (self.height * self.scale) - 20)

            # Use to see hitboxes
            pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

    def animate(self, delta_time):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time

        # Controls Speed of the Animation
        if self.last_frame_update > .04:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame + 1) % len(self.plane1_spr)
            self.curr_image = pygame.transform.scale_by(self.plane1_spr[self.current_frame], self.scale)

    def hit(self, damage):
        self.health -= damage
        self.hit_sound.set_volume(.5 * self.game.master_volume)
        self.game.effects_channel2.play(self.hit_sound)
        self.invincibilityCount = 1

    def death(self):
        self.lives -= 1
        self.health = self.maxHealth
        self.visible = False

        # Create an explosion
        explosion = Explosion(self.game, self.x, self.y, 2, self.explosions)
        self.explosions.append(explosion)

        # Reset Position
        self.x = 370
        self.y = 700

        # Start respawn timer
        self.respawnCount = 1

        # Trigger end of game sequence
        if self.lives <= 0:

            # Go to game over
            new_state = GameOver(self.game)
            new_state.enter_state()

    def load_assets(self):
        self.plane1_spr = [pygame.image.load('assets/sprites/plane1/plane1-0.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane1/plane1-1.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane1/plane1-2.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane1/plane1-3.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane1/plane1-4.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane1/plane1-5.png').convert_alpha()]

        self.curr_image = pygame.transform.scale_by(self.plane1_spr[0], self.scale)

        self.hit_sound = pygame.mixer.Sound('assets/audio/effects/hit.mp3')
        self.hit_sound.set_volume(.5 * self.game.master_volume)


class Projectile(object):
    def __init__(self, x, y, vel, scale, damage, game, player):
        self.game = game
        self.x = x
        self.y = y
        self.vel = vel
        self.width = game.proj_spr.get_width()
        self.height = game.proj_spr.get_height()
        self.scale = scale
        self.damage = damage
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.player = player

    def update(self, delta_time):

        # Bullet's position and Collision with border
        if self.game.WIN_HEIGHT > self.y > 0:
            self.y -= self.vel * (delta_time * 100)
        else:
            self.player.bullets.remove(self)

        # Bullet Hitbox
        self.hitbox = pygame.Rect(self.x - 5, self.y - 5, self.width * self.scale, self.height * self.scale)

    def render(self, display):
        display.blit(pygame.transform.scale_by(self.game.proj_spr, self.scale), (self.x - 5, self.y - 5))

        # Use to see hitboxes
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)


class Enemy(object):
    def __init__(self, game, x, y, scale, health, player, enemies, explosions):
        self.game = game
        self.scale = scale
        self.load_assets()
        self.x = x
        self.y = y
        self.player = player
        self.enemies = enemies
        self.explosions = explosions
        self.width = self.plane2_spr[0].get_width()
        self.height = self.plane2_spr[0].get_height()
        self.current_frame = 0
        self.last_frame_update = 0
        self.health = health
        self.maxHealth = health
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, delta_time):
        # Hitbox
        self.hitbox = pygame.Rect(self.x + 15, self.y + 10, (self.width * self.scale) - 30,
                                  (self.height * self.scale) - 20)

        for bullet in self.player.bullets:
            if pygame.Rect.colliderect(self.hitbox, bullet.hitbox):
                self.game.score += 1
                self.hit(bullet.damage)
                self.player.bullets.remove(bullet)

        # Check if dead
        if self.health <= 0:
            self.death()

        # Propeller Animation
        self.animate(delta_time)

    def render(self, display):

        display.blit(self.curr_image, (self.x, self.y))

        self.hitbox = pygame.Rect(self.x + 15, self.y + 10, (self.width * self.scale) - 30,
                                  (self.height * self.scale) - 20)

        # Use to see hitboxes
        pygame.draw.rect(display, (255, 0, 0), self.hitbox, 2)

    def animate(self, delta_time):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time

        # Controls Speed of the Animation
        if self.last_frame_update > .04:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame + 1) % len(self.plane2_spr)
            self.curr_image = pygame.transform.scale_by(self.plane2_spr[self.current_frame], self.scale)

    def hit(self, damage):
        self.health -= damage

    def death(self):
        if self in self.enemies:
            self.enemies.remove(self)

            # Create an explosion
            explosion = Explosion(self.game, self.x, self.y, 2, self.explosions)
            self.explosions.append(explosion)

    def load_assets(self):
        self.plane2_spr = [pygame.image.load('assets/sprites/plane2/plane2-0.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane2/plane2-1.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane2/plane2-2.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane2/plane2-3.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane2/plane2-4.png').convert_alpha(),
                           pygame.image.load('assets/sprites/plane2/plane2-5.png').convert_alpha()]

        self.curr_image = pygame.transform.scale_by(self.plane2_spr[0], self.scale)


class Enemy1(Enemy):
    def __init__(self, game, x, y, scale, health, player, enemies, explosions):
        super().__init__(game, x, y, scale, health, player, enemies, explosions)
        self.vel = 5

    def update(self, delta_time):
        super().update(delta_time)

        self.y += self.vel * (delta_time * 100)

        if self.y >= 1000:
            self.x = random.randint(0, self.game.WIN_WIDTH - self.width)
            self.y = -50


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


class Explosion(object):
    def __init__(self, game, x, y, scale, explosions):
        self.game = game
        self.scale = scale
        self.load_assets()
        self.x = x
        self.y = y
        self.explosions = explosions
        self.current_frame = 0
        self.last_frame_update = 0

    def update(self, delta_time):
        self.animate(delta_time)

        if self.current_frame == 0:
            self.game.explosion_sound.set_volume(.5 * self.game.master_volume)
            self.game.effects_channel3.play(self.game.explosion_sound)

        if self.current_frame >= len(self.explosion1_spr) - 1:
            self.explosions.remove(self)

    def render(self, display):
        display.blit(self.curr_image, (self.x - 20, self.y - 20))

    def animate(self, delta_time):
        # Compute how much time has passed since the frame last updated
        self.last_frame_update += delta_time

        # Controls Speed of the Animation
        if self.last_frame_update > .06:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame + 1) % len(self.explosion1_spr)

            self.curr_image = pygame.transform.scale_by(self.explosion1_spr[self.current_frame], self.scale)

    def load_assets(self):
        self.explosion1_spr = [pygame.image.load('assets/sprites/explosion1/explosion1-0.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-1.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-2.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-3.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-4.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-5.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-6.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-7.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-8.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-9.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-10.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-11.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-12.png').convert_alpha(),
                               pygame.image.load('assets/sprites/explosion1/explosion1-13.png').convert_alpha()]

        self.curr_image = pygame.transform.scale_by(self.explosion1_spr[0], self.scale)


class game_GUI(object):
    def __init__(self, game, player):
        self.game = game
        self.x = 0
        self.y = 800
        self.player = player
        self.load_assets()

    def render(self, display):
        display.blit(self.gui, (self.x, self.y))

        # Health Bar
        healthColor = (0, 255, 30)
        if self.player.health < (3 * self.player.maxHealth / 4):
            healthColor = (173, 255, 47)  # Green/Yellow
        if self.player.health < (self.player.maxHealth / 2):
            healthColor = (255, 140, 0)  # Orange
        if self.player.health < (self.player.maxHealth / 4):
            healthColor = (220, 20, 60)  # Red

        pygame.draw.rect(display, healthColor, (36, 836, (434 / self.player.maxHealth * self.player.health), 50))

        # Lives Counter
        for i in range(self.player.lives):
            display.blit(pygame.transform.scale_by(self.lives_shadow, 2), (556 + (i * 75), 916))
            display.blit(pygame.transform.scale_by(self.lives, 2), (550 + (i * 75), 910))

        # Score Counter
        self.game.draw_text(display, f'Score: {str(self.game.score).zfill(4)}', (34, 34, 34), 641, 868,
                            self.game.font1_1)
        self.game.draw_text(display, f'Score: {str(self.game.score).zfill(4)}', (106, 106, 106), 635, 862,
                            self.game.font1_1)

    def load_assets(self):
        self.gui = pygame.image.load('./assets/gui/game.png').convert()
        self.lives = pygame.image.load('./assets/gui/lives.png').convert_alpha()
        self.lives_shadow = pygame.image.load('./assets/gui/lives_shadow.png').convert_alpha()
