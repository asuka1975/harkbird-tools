from OpenGL.GL import *

from ..gl import Shader
from .chart_element_fragment_shader import FRAG
from .tick import * 

VERT = """#version 460

layout (location = 0) uniform vec2 padding;
layout (location = 1) uniform vec2 range;
layout (location = 2) uniform float tick;
layout (location = 3) uniform float tick_start;

void main() {
    float width = range.y - range.x;
    float grid_id = float(gl_VertexID / 2);
    float trans_tick = (tick_start + tick * grid_id - range.x) / width * 2 - 1;
    if(gl_VertexID % 2 == 0) {
        gl_Position = vec4(-1 + padding.x, trans_tick * (2.0 - padding.y * 2.0) / 2.0, 0, 1);
    } else {
        gl_Position = vec4(1 - padding.x, trans_tick * (2.0 - padding.y * 2.0) / 2.0, 0, 1);
    }
}
"""

class YGrid:
    def __init__(self, padding, range_, tick, color=(0.7, 0.7, 0.7, 1)):
        self.program = Shader()
        self.program.attach_shader(VERT, GL_VERTEX_SHADER)
        self.program.attach_shader(FRAG, GL_FRAGMENT_SHADER)
        self.program.link()
        self.program.use()
        glUniform2f(0, *padding)
        glUniform2f(1, *range_)
        glUniform1f(2, tick)
        glUniform1f(3, calc_tick_start(range_, tick))
        glUniform4f(4, *color)
        self.program.unuse()
        
        self.num_grids = calc_num_ticks(range_, tick)

    def draw(self, vao):
        glLineWidth(1)
        self.program.use()
        glBindVertexArray(vao)
        glDrawArrays(GL_LINES, 0, self.num_grids * 2)
        glBindVertexArray(0)
        self.program.unuse()

    def __del__(self):
        glDeleteProgram(self.program.handle)