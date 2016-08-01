#!/bin/env python2
# -*- coding : utf-8 -*-

__author__ = "U.unyxi"

import pygame

from random import randint
import random
import sys, os
from resloader import load_all_sfx, load_all_image, IMAGE, SFX, render_number


SCALE = 3
FLOOR = 200

class Widget(pygame.sprite.Sprite):
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position

    def _on_click(self):
        if hasattr(self, "on_click"):
            self.on_click()
        pass

    def _on_mouseover(self):
        if hasattr(self, "on_mouseover"):
            self.on_mouseover()
        pass

    def _on_mouseleave(self):
        if hasattr(self, "on_mouseleave"):
            self.on_mouseleave()
        pass

class GameButton(Widget):
    def _on_mouseover(self):
        self.rect.y += SCALE
        Widget._on_mouseover(self)
    def _on_mouseleave(self):
        self.rect.y -= SCALE
        Widget._on_mouseleave(self)       

class Widgets(pygame.sprite.RenderUpdates):
    def __init__(self):
        pygame.sprite.RenderUpdates.__init__(self)
        self.last_over = set()
    def handle_event(self, pressed, pos):
        for btn in self.sprites():
            if btn.rect.collidepoint(pos):
                if not btn in self.last_over:
                    self.last_over.add(btn)
                    btn._on_mouseover()
                if pressed[0]:
                    btn._on_click()
            else:
                if btn in self.last_over:
                    self.last_over.remove(btn)
                    btn._on_mouseleave()
    def remove_internal(self, element):
        try:
            self.last_over.remove(element)
        except KeyError:
            pass
        pygame.sprite.RenderUpdates.remove_internal(self, element)

def circle_iter(iterable):
    def circle_iter():
        it = iter(iterable)
        while True:
            try:
                yield next(it)
            except StopIteration:
                it = iter(iterable)
    return circle_iter()

class Bird(pygame.sprite.Sprite):
    def __init__(self, location, image_seq = None):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'bird'
        if image_seq:
            self.image_seq = image_seq
            self.image_iter = circle_iter(self.image_seq)
            self.image = next(self.image_iter)
        else:
            self.image_seq = self.image_iter = None
            self.image = pygame.Surface((50, 50))
            self.image.fill((255,255,0))
        self.rawimage = self.image.copy()
        self.rect = self.image.get_rect()
        self.static_collide = self.rect.copy()
        self.begin_location = location
        self.speed = 0
        self.accel = 0.125*SCALE
        self.reset()
        self.last_rect = self.rect.copy()
        self.dead = False
        self.deg = 0
        self.target_deg = 0
        self.timer = 0
        self._layer = 1
        self.state = "ready"

    def re_paint(self, image_seq):
            self.image_seq = image_seq
            self.image_iter = circle_iter(self.image_seq)
            self.image = next(self.image_iter)

    @property
    def box_collider(self):
        box = self.static_collide.copy()
        box.center = self.rect.center
        return box
    def reset(self):
        self.rect.center = self.begin_location
        self.speed = 0
        if self.image_seq:
            self.image_iter = circle_iter(self.image_seq)
        self.timer = 0
        self.flaptimer = 0

    def update(self):
        if self.state == "play":
            location = self.rect.center
            if self.image_iter and not self.dead:
                if self.flaptimer > 1:
                    if self.deg < 10:
                        self.rawimage = next(self.image_iter)
                    else:
                        self.rawimage = self.image_seq[1]
                    self.flaptimer = 0
                else:
                    self.flaptimer += 1
            self.speed += self.accel
            self.target_deg = self.speed*27/SCALE-45
            self.deg += self.target_deg / 5
            self.deg = min(self.deg, 90)
            self.deg = max(self.deg, -20)
            self.image = pygame.transform.rotate(self.rawimage, -self.deg)
            self.rect = self.image.get_rect()
            self.rect.center = location
            self.rect.y += self.speed

        elif self.state == "ready":
            if self.timer % 3 == 0:
                if self.timer < 20:
                    self.rect.centery -= 1*SCALE
                elif self.timer < 25:
                    pass
                elif self.timer < 45:
                    self.rect.centery +=1*SCALE
                elif self.timer < 50:
                    pass
                else:
                    self.timer = 0
            self.timer += 1
            if self.image_iter:
                if self.flaptimer > 6:
                    self.image = next(self.image_iter)
                    self.flaptimer = 0
                else:
                    self.flaptimer += 1
    def flap(self):
        if not self.dead and self.state == "play":
            if self.rect.top < 0:
                pass
            else:
                self.speed = -2.3*SCALE
            SFX["sfx_wing"].play()

    def die(self):
        self.dead = True
        SFX["sfx_hit"].play()
        SFX["sfx_die"].play()

class Pipe(pygame.sprite.Sprite):
    def __init__(self, image, x, type):
        self.name = 'pipe'
        pygame.sprite.Sprite.__init__(self)
        self._layer = 0

        self.image = image
        size = width, height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.left = x        
        self.is_frozen = False
        self.speed = 1*SCALE
        self.last_rect = self.rect.copy()
        self.type = type
        self.is_frozen = False
        self.passed = False

    def frozen(self):
        self.is_frozen = True
    def update(self):
        if not self.is_frozen:
            self.rect.x -= self.speed

class Floor(pygame.sprite.Sprite):
    def __init__(self, image, y):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'floor'
        self._layer = 2
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.pause = False
    def update(self):
        if not self.pause:
            self.rect.x -= SCALE
            if self.rect.x == -12*SCALE:
                self.rect.x = 0
    def frozen(self):
        self.pause = True

class Scoreboard(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'scoreboard'
        self._layer = 3
        self.score = 0
        self.location = pos
        self._update()
        self.rect.center = pos
    def up_to_date(self, score):
        if self.score != score:
            self.score = score
            self._update()

    def _update(self):
        score = render_number(self.score, "large")
        rect = score.get_rect()
        rect.top = 25*SCALE
        self.image = score
        self.rect = rect
        self.rect.center = self.location

class Scene(object):
    def __init__(self, game, name):
        self.name = name
        self.game = game
        self.screen = pygame.display.get_surface()
        self.done = False
        self.next_scene = None

    def entry_action(self):
        self.done = False

    def exit_action(self):
        pass

    def update(self):
        pass

    def quit_to(self, scene):
        self.next_scene = scene
        self.done = True
    def handle_event(self, event):
        pass

class FlappyBird(object):
    def __init__(self):
        self.current_scene = None
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.get_surface()

        self.sprites = pygame.sprite.LayeredUpdates()
        self.widgets = Widgets()
        self.background = None
        
        self.scenes = {}
        self.done = False
        bird_image_seq = self.random_bird_seq()
        self.bird = Bird((37*SCALE, 150*SCALE), bird_image_seq)
        self.sprites.add(self.bird)

        self.random_background()

        self.floor = Floor(IMAGE["floor"], FLOOR*SCALE)
        self.sprites.add(self.floor)
        self.current_score = 0
        self.best_score = 0

    def random_background(self):
        bgs = [IMAGE[image] for image in IMAGE.keys() if image[:10] == "background"]
        self.background = random.choice(bgs)
        self.flip = True
    def random_bird_seq(self):
        #bgs = [IMAGE[image] for image in IMAGE.keys() if image[:4] == "bird"]
        #bird_image = random.choice(bgs)
        #width ,height = bird_image.get_size()
        bird_image_seq = []
        for i in range(3):
            bird_image_seq.append(IMAGE["bird_yellow_" + str(i)])
        return bird_image_seq

    def set_scene(self, scene_name):
        if self.current_scene:
            self.current_scene.exit_action()

        scene = self.scenes[scene_name]
        scene.entry_action()
        self.current_scene = scene

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def eventloop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.KEYDOWN:
                self.current_scene.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.current_scene.handle_event(event)

        pressed = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        self.widgets.handle_event(pressed, pos)

    def quit(self):
        self.done = True

    def mainloop(self):
        while not self.done:
            self.clock.tick(self.fps)
            if self.current_scene.done:
                self.set_scene(self.current_scene.next_scene)
            if self.background:
                self.screen.blit(self.background,(0,0))


            self.eventloop()
            self.current_scene.update()
            self.widgets.update()

            if self.bird.rect.top > 0:
                rect = self.screen.get_rect()
                rect.height = FLOOR*SCALE
                self.bird.rect.center = self.bird.box_collider.clamp(rect).center

            updates = []
            updates.extend(self.sprites.draw(self.screen))
            updates.extend(self.widgets.draw(self.screen))
            pygame.display.update(updates)

            if self.flip:
                pygame.display.flip()
                self.flip = False

class ScenePlay(Scene):
    def __init__(self, game):
        Scene.__init__(self, game, "play")
        self.bird = self.game.bird
        self.sprites = self.game.sprites
        self.timer = 0
        self.screen = self.game.screen
        self.rect = self.screen.get_rect()

    def entry_action(self):
        self.done = False
        bird = self.game.bird
        bird.dead = False
        bird.state = "play"
        bird.deg = 0
        bird.flap()
        self.game.floor.pause = False
        self.game.widgets.empty()
        self.scoreboard = Scoreboard((self.rect.width/2, 50*SCALE))
        self.game.sprites.add(self.scoreboard)

    def exit_action(self):
        self.game.sprites.remove(self.scoreboard)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.bird.flap()

    def update(self):
        self.scoreboard.up_to_date(self.game.current_score)
        self.sprites.update()
        if self.timer > 120 and self.timer % 90 == 0:
            height = randint(20*SCALE, 130*SCALE)
            pipe_top = Pipe(IMAGE['pipe_top_green'], self.rect.right, 'top')
            pipe_bot = Pipe(IMAGE["pipe_bottom_green"], self.rect.right, 'bottom')

            pipe_top.rect.bottom = height
            pipe_bot.rect.top = height+45*SCALE
            self.sprites.add(pipe_top)
            self.sprites.add(pipe_bot)

        self.timer += 1

        for pipe in self.sprites:
            if pipe.name == "pipe":
                if pipe.rect.right < 0:
                    pipe.kill()
                if pipe.rect.colliderect(self.bird.box_collider):
                    self.gameover()
                if pipe.type == 'top':
                    pipe_x = pipe.rect.centerx
                    last_x = self.bird.rect.centerx - pipe.speed
                    current_x = self.bird.rect.centerx
                    if last_x <= pipe_x < current_x:
                        if not pipe.passed:
                            pipe.passed = True
                            self.game.current_score += 1
                            SFX["sfx_point"].play()

        
        if self.bird.rect.bottom >= FLOOR*SCALE:
            self.gameover()

    def frozen_all_sprites(self):
        for sprite in self.sprites:
            if sprite.name == "pipe" or sprite.name == "floor":
                sprite.frozen()
            if sprite.name == "bird":
                sprite.die()

    def gameover(self):
        self.frozen_all_sprites()
        self.quit_to("gameover")

class SceneReady(Scene):
    def __init__(self, game):
        Scene.__init__(self, game, "ready")
        self.sprites = self.game.sprites
        self.screen = self.game.screen
        self.width, self.height = self.screen.get_size()
    def entry_action(self):
        self.game.random_background()
        self.game.bird.re_paint(self.game.random_bird_seq())
        self.game.current_score = 0
        self.game.widgets.empty()
        rect = self.screen.get_rect()
        rect.centery = 134*SCALE
        rect.centerx = self.width/2
        tap_tap = Widget(IMAGE["tap_tap"], rect.center)
        self.game.widgets.add(tap_tap)
        rect.centery = 80*SCALE
        get_ready = Widget(IMAGE["get_ready"], rect.center)
        self.game.widgets.add(get_ready)
        for spr in self.game.sprites:
            if spr.name == "pipe":
                spr.kill()
        self.game.floor.pause = False
        self.game.bird.speed = 0
        self.game.bird.dead = False
        self.game.bird.state = "ready"
        self.game.bird.rect.center = (45*SCALE, 135*SCALE)
        self.scoreboard = Scoreboard((self.width/2, 50*SCALE))
        self.game.sprites.add(self.scoreboard)
        self.done = False
    def update(self):
        self.sprites.update()
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.quit_to("play")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.quit_to("play")
    def exit_action(self):
        self.game.sprites.remove(self.scoreboard)
class GameOverBoard(pygame.sprite.Sprite):
    def __init__(self, image, pos, score, best):
        pygame.sprite.Sprite.__init__(self)
        self.image = image.copy()
        image_score = render_number(score, "medium")
        rect = image_score.get_rect()
        rect.right = 105*SCALE
        rect.top = 18*SCALE
        self.image.blit(image_score, rect)
        image_score = render_number(best, "medium")
        rect = image_score.get_rect()
        rect.right = 105*SCALE
        rect.top = 39*SCALE
        self.image.blit(image_score, rect)

        self.rect = image.get_rect()
        self.rect.center = pos
        self._layer = 3

class SceneGameOver(Scene):
    def __init__(self, game):
        Scene.__init__(self, game, "gameover")
        self.screen = self.game.screen
        self.width, self.height = self.screen.get_size()
    def entry_action(self):
        self.done = False
        self.game.best_score = max(self.game.best_score, self.game.current_score)

        playButton = GameButton(IMAGE["button_play"], (40*SCALE, 150*SCALE))
        playButton.on_click = lambda:self.quit_to("ready")
        self.game.widgets.add(playButton)
        self.scoreboard = GameOverBoard(IMAGE["score_board"], (self.width/2,80*SCALE),
                self.game.current_score, self.game.best_score)
        self.game.sprites.add(self.scoreboard)
        SFX["sfx_swooshing"].play()
    def update(self):
        self.game.sprites.update()
    def exit_action(self):
        self.game.sprites.remove(self.scoreboard)

def main():
    pygame.init()
    winsize = 144*SCALE, 256*SCALE
    screen = pygame.display.set_mode(winsize)
    pygame.display.set_caption("Flappy Bird PC Version 0.7")

    try:
        splash = pygame.image.load(
                    os.path.join(
                        os.path.split(
                            os.path.abspath(
                                sys.argv[0]))[0],
                            "splash.png")).convert()
        splash = scaleNx(splash, SCALE)
        rect = splash.get_rect()
        rect.center = winsize[0]//2, winsize[1]//2
        screen.blit(splash, rect)
        pygame.display.update()
    except:
        pass

    load_all_image(SCALE)
    pygame.display.set_icon(IMAGE["icon"])
    load_all_sfx()

    #pygame.time.delay(2000)

    game = FlappyBird()
    game.add_scene(ScenePlay(game))
    game.add_scene(SceneReady(game))
    game.add_scene(SceneGameOver(game))
    game.set_scene("ready")
    game.mainloop()


if __name__ == "__main__":
    main()
