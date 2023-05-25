import pygame
import self as self


class Ship():

    def __init__(self, ai_settings, screen):
        """initialize the ship and original position"""
        self.screen = screen
        self.ai_settings = ai_settings
        # load ship image and get rectangle
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # set every ship in center of bottom of screen
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        # store minimum number in attibute
        self.center = float(self.rect.centerx)
        # sign of moving
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """adjust position of ship according to moving sign"""
        # update center value instead of rect
        # 12.6.5 不完整
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.rect.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > 0:
            self.rect.center -= self.ai_settings.ship_speed_factor

        # renew rect object according to self.center
        self.rect.centerx = self.center

    def blitme(self):
        """draw ship in located"""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.center = self.screen_rect.centerx