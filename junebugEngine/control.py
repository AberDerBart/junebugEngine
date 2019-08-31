import pygame

from .game_object import Direction
from .moving_object import MovingObject

class Control:
    keymap = {}
    keymaps = {}
    entity = None
    def setEntity(entity):
        if isinstance(entity, MovingObject):
            entity = PlayerControl(entity)
        Control.keymap = Control.keymaps.get(type(entity), {})
        Control.entity = entity
    def processEvent(event):
        if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            if event.key in Control.keymap:
                Control.keymap[event.key](Control.entity, event.type == pygame.KEYDOWN)

class PlayerControl:
    def __init__(self, char=None):
        self.char = char
        self.active = set()

    def setCharacter(self, char):
        self.char = char
        self.active = set()
    def right(self, pressed):
        if pressed:
            self.active.add(PlayerControl.right)
            self.char.run_right()
        else:
            self.active.discard(PlayerControl.right)
            if PlayerControl.left in self.active:
                self.char.run_left()
            else:
                self.char.idle()
    def left(self, pressed):
        if pressed:
            self.active.add(PlayerControl.left)
            self.char.run_left()
        else:
            self.active.discard(PlayerControl.left)
            if PlayerControl.right in self.active:
                self.char.run_right()
            else:
                self.char.idle()
    def jump(self, pressed):
        self.char.jump(pressed)
    def attack(self, pressed):
        if pressed:
            self.char.special()
    def switch(self, pressed):
        if pressed:
            self.char = self.char.switch()
