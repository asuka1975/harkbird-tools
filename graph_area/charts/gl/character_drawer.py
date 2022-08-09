from OpenGL.GL import *

from ..gl import Shader

CHARSET = "0123456789"

VERT = """#version 460


"""

class CharacterDrawer:
    def __init__(self):
        self.program = Shader()

    def __del__(self):
        glDeleteProgram(self.program.handle)