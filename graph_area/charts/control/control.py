from OpenGL.GL import *

class Control:
    def __init__(self, position, size, pixel_size):
        self.position = position
        self.size = size
        self.pixel_size = pixel_size 
        self.callbacks = {}
        self.children = []
        
    def change_pixel_size(self, width, height):
        self.pixel_size = (width, height)

    def connect(self, event, callback):
        self.callbacks[event] = callback

    def emit_event(self, event, *args, **kwargs):
        pass
        