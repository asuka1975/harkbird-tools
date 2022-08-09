from OpenGL.GL import *

from ..gl import Shader
from .chart_element_fragment_shader import FRAG

VERT = """#version 460

layout (location = 0) uniform vec2 padding;

void main() {
    const vec2[3] vertices = vec2[](
        vec2(-1 + padding.x, 1 - padding.y),
        vec2(-1 + padding.x, -1 + padding.y),
        vec2(1 - padding.x, -1 + padding.y)
    );

    gl_Position = vec4(vertices[gl_VertexID], 0, 1);
}
"""

class Axis:
    def __init__(self, padding, color=(0, 0, 0, 1)):
        self.program = Shader()
        self.program.attach_shader(VERT, GL_VERTEX_SHADER)
        self.program.attach_shader(FRAG, GL_FRAGMENT_SHADER)
        self.program.link()
        self.program.use()
        glUniform2f(0, *padding)
        glUniform4f(4, *color)
        self.program.unuse()

    def draw(self, vao):
        glLineWidth(2)
        self.program.use()
        glBindVertexArray(vao)
        glDrawArrays(GL_LINE_STRIP, 0, 3)
        glBindVertexArray(0)
        self.program.unuse()

    def __del__(self):
        glDeleteProgram(self.program.handle)
