import pygame
import os, sys

def make_crop(surface, topleft, bottomright):
    width = bottomright[0] - topleft[0]
    height = bottomright[1] - topleft[1]
    rect = pygame.Rect(topleft[0], topleft[1], width, height)
    return surface.subsurface(rect)

def scaleNx(surface, n):
    size = surface.get_size()
    size = size[0]*n, size[1]*n
    scaled =  pygame.transform.scale(surface, size)
    return scaled



IMAGE = {}

_image_loaded = False

def load_all_image(scale = 1):
    dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
    dirname = os.path.join(dirname, "res")
    atlas = pygame.image.load(os.path.join(dirname, "atlas.png")).convert_alpha()
    IMAGE["background_day"] = make_crop(atlas, (0, 0), (144, 256))
    IMAGE["background_night"] = make_crop(atlas, (146, 0), (390, 256))
    IMAGE["get_ready"] = make_crop(atlas, (292, 57), (390, 88))
    IMAGE["floor"] = make_crop(atlas, (292, 0), (460, 56))
    IMAGE["gameover"] = make_crop(atlas, (392, 58), (493, 84))
    IMAGE["tap_tap"] = make_crop(atlas, (292, 91), (349, 140))
    IMAGE["copy_right"] = make_crop(atlas, (442, 91), (505, 98))
    IMAGE["flappy_bird"] = make_crop(atlas, (351, 91), (440, 115))
    IMAGE["button_play"] = make_crop(atlas, (352, 118), (409, 151))
    IMAGE["button_share"] = make_crop(atlas, (412, 118), (469, 151))
    IMAGE["star_small"] = make_crop(atlas, (140, 344), (141, 345))
    IMAGE["star_medium"] = make_crop(atlas, (139, 368), (143, 371))
    IMAGE["star_big"] = make_crop(atlas, (139, 394), (144, 398))
    IMAGE["medal_golden"] = make_crop(atlas, (121, 282), (143, 304))
    IMAGE["medal_silver"] = make_crop(atlas, (112, 453), (134, 475))
    IMAGE["medal_copper"] = make_crop(atlas, (112, 477), (134, 499))
    IMAGE["medal_platinum"] = make_crop(atlas, (121, 258), (143, 280))
    IMAGE["pipe_top_green"] = make_crop(atlas, (56, 324), (82, 483))
    IMAGE["pipe_bottom_green"] = make_crop(atlas, (84, 323), (110, 483))
    IMAGE["score_board"] = make_crop(atlas, (0, 258), (119, 321))
    IMAGE["bird_yellow_0"] = make_crop(atlas, (3, 491), (20, 503))
    IMAGE["bird_yellow_1"] = make_crop(atlas, (31, 491), (48, 503))
    IMAGE["bird_yellow_2"] = make_crop(atlas, (59, 491), (76, 503))
    IMAGE["bird_blue_0"] = make_crop(atlas, (87, 491), (104, 503))
    IMAGE["bird_blue_1"] = make_crop(atlas, (115, 329), (132, 341))
    IMAGE["bird_blue_2"] = make_crop(atlas, (115, 355), (132, 367))
    IMAGE["bird_red_0"] = make_crop(atlas, (115, 381), (132, 393))
    IMAGE["bird_red_1"] = make_crop(atlas, (115, 407), (132, 419))
    IMAGE["bird_red_2"] = make_crop(atlas, (115, 433), (132, 445))
    IMAGE["icon"] = IMAGE["bird_yellow_1"]
    IMAGE["newrecord"] = make_crop(atlas, (112, 501), (128, 508))

    bigest_numbers={
            "0": ((496, 60), (508, 78)),
            "1": ((136, 455), (144, 473)),
            "2": ((292, 160), (304, 178)),
            "3": ((306, 160), (318, 178)),
            "4": ((320, 160), (332, 178)),
            "5": ((334, 160), (346, 178)),
            "6": ((292, 184), (304, 202)),
            "7": ((306, 184), (318, 202)),
            "8": ((320, 184), (332, 202)),
            "9": ((334, 184), (346, 202)),
            }
    for c in "0123456789":
        IMAGE["number_bigest_" + c] = make_crop(atlas, *bigest_numbers[c])
    medium_numbers = {
            "0": ((137, 306), (144, 316)),
            "1": ((137, 477), (144, 487)),
            "2": ((137, 489), (144, 499)),
            "3": ((131, 501), (138, 511)),
            "4": ((502, 0), (509, 10)),
            "5": ((502, 12), (509, 22)),
            "6": ((505, 26), (512, 36)),
            "7": ((505, 42), (512, 52)),
            "8": ((293, 242), (300, 252)),
            "9": ((311, 206), (318, 216)),
            }
    for c in "0123456789":
        IMAGE["number_medium_" + c] = make_crop(atlas, *medium_numbers[c])

    if not scale == 1:
        for key in IMAGE.keys():
            scaled = scaleNx(IMAGE[key], scale)
            IMAGE[key] = scaled

SFX = {}
def load_all_sfx():
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    dirname = os.path.join(dirname, "res")
    accept = [".ogg"]
    for sfx in os.listdir(dirname):
        name, ext = os.path.splitext(sfx)
        if ext.lower() in accept:
            SFX[name] = pygame.mixer.Sound(os.path.join(dirname, sfx))

def render_number(number, fontsize):
    num = int(number)
    num = str(num)
    length = len(num)
    renders = []
    if fontsize is "large":
        base = "number_bigest_"
    elif fontsize is "medium":
        base = "number_medium_"
    width = 0
    height = 0

    em = IMAGE[base + "0"].get_width()
    for digital in num:
        render = IMAGE[base + digital]
        width += render.get_width()
        h = render.get_height()
        height = max(h, height)
        renders.append(render)
    if fontsize is "large":
        width -= (length-1)*3*em//18
    else:
        width += (length-1)*2*em//10
    surface = pygame.Surface((int(width), int(height))).convert_alpha()
    surface.fill((0,0,0,0))

    cursor = 0
    for render in renders:
        surface.blit(render, (int(cursor), 0))
        cursor += render.get_width()
        if fontsize is "large":
            cursor-=3*em//18
        else:
            cursor+=2*em//10
    return surface
    
