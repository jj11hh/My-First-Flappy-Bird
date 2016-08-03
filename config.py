from pygame.locals import * #Don't remove this line!!!

#[DISPLAY]
SCALE    = 1      #real pixels / game pixels, the size of window depends on
WSRD     = False  #redraw the whole screen


#[GAME]
PLAYERS  = 9   #support three players by default
KEYBINDS = {   #`pydoc pygame.locals' for keys' name 
               #(if you have installed pydoc and pygame-doc)
    "1p" : K_a,
    "2p" : K_s,
    "3p" : K_d,
    "4p" : K_f,
    "5p" : K_g,
    "6p" : K_h,
    "7p" : K_j,
    "8p" : K_k,
    "9p" : K_l
    #"etc.":...
        }

