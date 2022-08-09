from ctypes import Structure, sizeof
import sys

from OpenGL.GL import *
import glfw

import charts

class Shader:
    def __init__(self):
        self.handle = glCreateProgram()
    
    def attach_shader(self, content, type, log_always=False):
        shader = glCreateShader(type)
        glShaderSource(shader, [content])
        glCompileShader(shader)

        status = ctypes.c_uint(GL_UNSIGNED_INT)
        glGetShaderiv(shader, GL_COMPILE_STATUS, status)
        if log_always or not status:
            print(glGetShaderInfoLog(shader).decode("utf-8"), file=sys.stderr)
            glDeleteShader(shader)
            return False
        
        glAttachShader(self.handle, shader)
        glDeleteShader(shader)
        return True

    def link(self, log_always=False):
        glLinkProgram(self.handle)
        status = ctypes.c_uint(GL_UNSIGNED_INT)
        glGetProgramiv(self.handle, GL_LINK_STATUS, status)
        if log_always or not status:
            print(glGetProgramInfoLog(self.handle).decode("utf-8"), file=sys.stderr)
            return False
        return True
    
    def use(self):
        glUseProgram(self.handle)

    def unuse(self):
        glUseProgram(0)

def framebuffer_callback(window, width, height):
    glViewport(0, 0, width, height)

def main():
    if glfw.init() == glfw.FALSE:
        raise RuntimeError("failed to initialize GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    window = glfw.create_window(1500, 900, "sample", None, None)
    if not window:
        raise RuntimeError("failed to create GLFWwindow")
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_callback)

    padding = (0.2, 0.2)
    range_ = (7, 41)
    tick = 7
    axis = charts.core.Axis(padding)
    frame = charts.core.Frame(padding)
    xgrid = charts.core.XGrid(padding, range_, tick)
    ygrid = charts.core.YGrid(padding, range_, tick)
    xscale = charts.core.XScale(padding, range_, tick)
    yscale = charts.core.YScale(padding, range_, tick)

    vao = glGenVertexArrays(1)

    glClearColor(1, 1, 1, 1)
    while glfw.window_should_close(window) == glfw.FALSE:
        glClear(GL_COLOR_BUFFER_BIT)

        frame.draw(vao)
        xgrid.draw(vao)
        ygrid.draw(vao)
        axis.draw(vao)
        xscale.draw(vao)
        yscale.draw(vao)

        glfw.swap_buffers(window)
        glfw.wait_events()

    glDeleteVertexArrays(1, [vao])

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
