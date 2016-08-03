# -*- coding : utf-8 -*-

__author__ = "U.unyxi"

import pygame

from random import randint
import random
import sys, os
from resloader import load_all_sfx, load_all_image, IMAGE, SFX, render_number, scaleNx
import constants

try:
    from config import *
    SCALE = int(SCALE)
    SCALE = max(SCALE, 1)
    SCALE = min(SCALE, 10)
    PLAYERS = int(PLAYERS)
    PLAYERS = min(PLAYERS, 15)
    PLAYERS = max(PLAYERS, 1)
    for i in range(1, PLAYERS+1):
        key = KEYBINDS.get("{}p".format(i))
        if not key:
            KEYBINDS["{}p".format(i)] = pygame.K_SPACE
    WSRD = bool(WSRD)
except Exception as e:
    print("Error in reading config:")
    print(e)
    print("using default config.")
    WSRD = False
    SCALE = 3
    PLAYERS = 1
    KEYBINDS = {"1p" : pygame.K_SPACE}

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
    def _on_mouseup(self):
        if hasattr(self, "on_mouseleave"):
            self.on_mouseup()
        pass
    def _on_mousedown(self):
        if hasattr(self, "on_mouseleave"):
            self.on_mousedown()
        pass
class GameButton(Widget):
    def _on_mousedown(self):
        self.rect.y += SCALE
        Widget._on_mouseover(self)
    def _on_mouseup(self):
        self.rect.y -= SCALE
        Widget._on_mouseleave(self)       

class Widgets(pygame.sprite.RenderUpdates):
    def __init__(self):
        pygame.sprite.RenderUpdates.__init__(self)
        self.last_over = set()
        self.last_buttondown = set()
    def handle_event(self, pressed, pos):
        for btn in self.sprites():
            if btn.rect.collidepoint(pos):
                if not btn in self.last_over:
                    self.last_over.add(btn)
                    btn._on_mouseover()
                if pressed[0]:
                    if not btn in self.last_buttondown:
                        self.last_buttondown.add(btn)
                        btn._on_mousedown()
                else:
                    if btn in self.last_buttondown:
                        self.last_buttondown.remove(btn)
                        btn._on_mouseup()
                        btn._on_click()
            else:
                if btn in self.last_over:
                    self.last_over.remove(btn)
                    btn._on_mouseleave()
                if btn in self.last_buttondown:
                    self.last_buttondown.remove(btn)
                    btn._on_mouseup()
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
        self._y = self.rect.y

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
            basetime = 0
            flyuptime = basetime + 24
            idletime1 = flyuptime + 2
            flydowntime = idletime1 + 24
            idletime2 = flydowntime + 2

            timeout = False
            if self.timer < flyuptime:
                self._y -= 1*SCALE / 5.
            elif self.timer < idletime1:
                pass
            elif self.timer < flydowntime:
                self._y += 1*SCALE / 5.
            elif self.timer < idletime2:
                pass
            else:
                self.timer = 0
                timeout = True
            if not timeout: 
                self.timer += 1
            self.rect.y = int(self._y)

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
        self.screen = game.screen
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
    def __init__(self, screen):
        self.current_scene = None
        self.screen = screen

        self.sprites = pygame.sprite.LayeredUpdates()
        self.widgets = Widgets()
        self.background = None
        
        self.scenes = {}
        self.done = False
        bird_image_seq = self.random_bird_seq()
        self.bird = Bird((37*SCALE, 130*SCALE), bird_image_seq)
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
        color = random.choice(["yellow", "blue", "red"])
        bird_image_seq = []
        for i in range(3):
            bird_image_seq.append(IMAGE["bird_{}_".format(color) + str(i)])
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

    def update(self):
        if self.current_scene.done:
            self.set_scene(self.current_scene.next_scene)
        if self.background:
            self.screen.blit(self.background,(0,0))


        #self.eventloop()
        self.current_scene.update()
        self.widgets.update()

        if self.bird.rect.top > 0:
            rect = self.screen.get_rect()
            rect.height = FLOOR*SCALE
            self.bird.rect.center = self.bird.box_collider.clamp(rect).center

        updates = []

        if not WSRD:
            updates.extend(self.sprites.draw(self.screen))
            updates.extend(self.widgets.draw(self.screen))
        else:
            self.sprites.draw(self.screen)
            self.widgets.draw(self.screen)

        if self.flip:
            updates = [self.screen.get_rect()]
            self.flip = False

        return updates
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

class SlideUpAndDown(pygame.sprite.Sprite):
    def __init__(self, image, x, init_y, target_y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.name = "slider"
        self.rect = image.get_rect()
        self.rect.center = x, init_y
        self.target_y = target_y
        self._layer = 3
        self.speed = speed

    def update(self):
        distance = self.target_y - self.rect.centery
        if abs(distance) > self.speed:
            sign = distance / abs(distance)
            self.rect.y += sign*self.speed



class GameOverBoard(SlideUpAndDown):
    def __init__(self, image, pos, score, best):
        image = image.copy()
        image_score = render_number(score, "medium")
        rect = image_score.get_rect()
        rect.right = 105*SCALE
        rect.top = 18*SCALE
        image.blit(image_score, rect)
        image_score = render_number(best, "medium")
        rect = image_score.get_rect()
        rect.right = 105*SCALE
        rect.top = 39*SCALE
        image.blit(image_score, rect)
        if score == best:
            image.blit(IMAGE["newrecord"], (71*SCALE, 30*SCALE))

        if score >= 40:
            medal = IMAGE["medal_platinum"]
        elif score >= 30:
            medal = IMAGE["medal_golden"]
        elif score >= 20:
            medal = IMAGE["medal_silver"]
        elif score >= 10:
            medal = IMAGE["medal_copper"]
        else:
            medal = None

        if medal is not None:
            image.blit(medal, (16*SCALE, 23*SCALE))
        SlideUpAndDown.__init__(self, image, pos[0], pos[1]+90*SCALE, pos[1], 6*SCALE)

class SceneGameOver(Scene):
    def __init__(self, game):
        Scene.__init__(self, game, "gameover")
        self.screen = self.game.screen
        self.width, self.height = self.screen.get_size()
    def entry_action(self):
        self.done = False
        self.clears = set()
        self.game.best_score = max(self.game.best_score, self.game.current_score)

        self.animation_timer = 0

    def update(self):
        if self.animation_timer == 20:
            SFX["sfx_swooshing"].play()
            textgameover = SlideUpAndDown(IMAGE["gameover"], self.width//2, 70*SCALE, 80*SCALE, 3*SCALE)
            self.game.sprites.add(textgameover)
            self.clears.add(textgameover)
        if self.animation_timer == 50:
            SFX["sfx_swooshing"].play()
            scoreboard = GameOverBoard(IMAGE["score_board"],
                (self.width//2,126*SCALE),
                self.game.current_score, self.game.best_score)
            self.game.sprites.add(scoreboard)
            self.clears.add(scoreboard)
        elif self.animation_timer == 70:
            playButton = GameButton(IMAGE["button_play"], (40*SCALE, 188*SCALE))
            def on_click():
                SFX["sfx_swooshing"].play()
                self.quit_to("ready")
            playButton.on_click = on_click;

            self.game.widgets.add(playButton)
            uselessButton = GameButton(IMAGE["button_share"], (105*SCALE, 188*SCALE))
            uselessButton._on_click = lambda:SFX["sfx_swooshing"].play()
            self.game.widgets.add(uselessButton)

        self.game.sprites.update()
        self.animation_timer += 1
    def exit_action(self):
        for spr in self.clears:
            spr.kill()



class Window(object):
    def __init__(self, mainscreen, rect, keybinds):
        rect = pygame.Rect(rect)
        screen = mainscreen.subsurface(rect)
        game = FlappyBird(screen)
        game.add_scene(ScenePlay(game))
        game.add_scene(SceneReady(game))
        game.add_scene(SceneGameOver(game))
        game.set_scene("ready")
        self.game = game
        self.screen = screen
        self.rect = rect
        self.keybinds = keybinds
    def update(self):
        updates = self.game.update()
        if not WSRD:
            return [update.move(self.rect.topleft) for update in updates]


def main():
    pygame.init()
    #winsize = 144*SCALE, 256*SCALE
    winsize = 144*SCALE*PLAYERS, 256*SCALE
    screen = pygame.display.set_mode(winsize)

    pygame.display.set_caption("My-First-Flappy-Bird Version {}".format(constants.VERSION))

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

    pygame.time.delay(2000)
    clock = pygame.time.Clock()

    windows = [Window(screen, (((i-1)*144*SCALE, 0), (144*SCALE, 256*SCALE)),
              {KEYBINDS["{}p".format(i)]: pygame.K_SPACE}) for i in range(1, PLAYERS+1)]

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                for win in windows:
                    if event.key in win.keybinds.keys():
                        newevent = pygame.event.Event(pygame.KEYDOWN, key = win.keybinds[event.key])
                        win.game.current_scene.handle_event(newevent)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for win in windows:
                    if win.rect.collidepoint(pos):
                        newpos = pos[0] - win.rect.left, pos[1] - win.rect.top
                        newevent = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos = newpos)
                        win.game.current_scene.handle_event(newevent)

        pressed = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        updates = []
        for win in windows:
            if win.rect.collidepoint(pos):
                newpos = pos[0] - win.rect.left, pos[1] - win.rect.top
                win.game.widgets.handle_event(pressed, newpos)
            if not WSRD:
                updates.extend(win.update())
            else:
                win.update()

        if WSRD:
            pygame.display.update()
        else:
            pygame.display.update(updates)


if __name__ == "__main__":
    main()
