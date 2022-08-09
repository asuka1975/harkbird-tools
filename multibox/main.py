from ctypes import Structure, sizeof
import sys
import random

from OpenGL.GL import *
import glfw
import glm

class Box(Structure):
    _fields_ = [
        ("range", GLfloat * 2),
        ("value", GLfloat),
        ("color_id", GLint)
    ]


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

def create_box():
    start = random.random() * 2 - 1
    end = start + random.random() * 0.1
    if end > 1:
        end = 1
    value = random.random() * 2 - 1
    color_id = random.randint(0, 5)
    return Box((GLfloat * 2)(start, end), value, color_id)

def leftbottom(select_start, select_end):
    return (min(select_start[0], select_end[0]), min(select_start[1], select_end[1]))

def righttop(select_start, select_end):
    return (max(select_start[0], select_end[0]), max(select_start[1], select_end[1]))

def mouse_buton_callback(window, btn, action, mods):
    data = glfw.get_window_user_pointer(window)
    rect = glfw.get_framebuffer_size(window)
    mouse = glfw.get_cursor_pos(window)
    mousef = (mouse[0] / rect[0] * 2 - 1, - mouse[1] / rect[1] * 2 + 1)
    if btn == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        data["select_start"] = mousef
    if btn == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        data["select_box_visible"] = False
    if btn == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        data["prev_mouse"] = mousef
        if not (mods & glfw.MOD_SHIFT):
            select = data["select"]
            select.use()
            data["prev_mouse"] = mousef
            glBindBuffer(GL_UNIFORM_BUFFER, data["ubo"])
            glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof(GLfloat) * 4, (GLfloat * 4)(*mousef, *mousef)) 
            glDispatchCompute(*NUM_WORKGROUPS)
            select.unuse()
    if btn == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE and not (mods & glfw.MOD_SHIFT):
        select = data["select"]
        select.use()
        glBindBuffer(GL_UNIFORM_BUFFER, data["ubo"])
        glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof(GLfloat) * 4, (GLfloat * 4)(-2, -2, -2, -2)) # 矩形が選択状態にならないよう選択範囲を描画範囲の外に配置＋選択範囲を０に
        glDispatchCompute(*NUM_WORKGROUPS)
        select.unuse()
        pass

def cursor_position_callback(window, xpos, ypos):
    data = glfw.get_window_user_pointer(window)
    rect = glfw.get_framebuffer_size(window)
    mouse = (xpos / rect[0] * 2 - 1, -ypos / rect[1] * 2 + 1)
    prev_mouse = data["prev_mouse"]
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT):
        data["prev_mouse"] = mouse
        data["move"].use()
        glUniform2f(0, mouse[0] - prev_mouse[0], mouse[1] - prev_mouse[1])
        glDispatchCompute(*NUM_WORKGROUPS)
        data["move"].unuse()
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT):
        data["select_box_visible"] = True 
        data["select_end"] = mouse
        lb = leftbottom(data["select_start"], data["select_end"])
        rt = righttop(data["select_start"], data["select_end"])
        glBindBuffer(GL_UNIFORM_BUFFER, data["ubo"])
        glBufferSubData(GL_UNIFORM_BUFFER, 0, sizeof(GLfloat) * 4, (GLfloat * 4)(*lb, * rt))
        data["select"].use()
        glDispatchCompute(*NUM_WORKGROUPS)
        data["select"].unuse()

NUM_WORKGROUPS = (32, 32, 1)

def main():
    if glfw.init() == glfw.FALSE:
        raise RuntimeError("failed to initialize GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    window = glfw.create_window(1500, 900, "boxes", None, None)
    if window is None:
        raise RuntimeError("failed to create GLFWwindwo")
    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window, mouse_buton_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    data = {}
    glfw.set_window_user_pointer(window, data)

    num_boxes = 1000
    boxes = (Box * num_boxes)(*[create_box() for _ in range(num_boxes)])

    ssbos = glGenBuffers(2)
    [ssbo, select_ssbo] = ssbos
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(boxes), boxes, GL_DYNAMIC_DRAW)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssbo)

    selects = (GLint * num_boxes)(*[0 for _ in range(num_boxes)])
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, select_ssbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(selects), selects, GL_DYNAMIC_DRAW)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, select_ssbo)

    ubo = glGenBuffers(1)
    glBindBuffer(GL_UNIFORM_BUFFER, ubo)
    ubo_data = (GLfloat * 4)(-2, -2, -2, -2)
    glBufferData(GL_UNIFORM_BUFFER, sizeof(ubo_data), ubo_data, GL_DYNAMIC_DRAW)
    glBindBufferBase(GL_UNIFORM_BUFFER, 2, ubo)

    vao = glGenVertexArrays(1)


    program = Shader()
    with open("shaders/box.vert", "r") as f:
        program.attach_shader(f.read(), GL_VERTEX_SHADER)
    with open("shaders/box.frag", "r") as f:
        program.attach_shader(f.read(), GL_FRAGMENT_SHADER)
    program.link()

    select_border = Shader()
    with open("shaders/select_border.vert", "r") as f:
        select_border.attach_shader(f.read(), GL_VERTEX_SHADER)
    with open("shaders/select_border.frag", "r") as f:
        select_border.attach_shader(f.read(), GL_FRAGMENT_SHADER)
    select_border.link()

    select_box = Shader()
    with open("shaders/select_box.vert", "r") as f:
        select_box.attach_shader(f.read(), GL_VERTEX_SHADER)
    with open("shaders/select_box.frag", "r") as f:
        select_box.attach_shader(f.read(), GL_FRAGMENT_SHADER)
    select_box.link()

    select = Shader()
    with open("shaders/select.comp", "r") as f:
        select.attach_shader(f.read(), GL_COMPUTE_SHADER)
    select.link()
    select.use()
    glUniform1ui(2, num_boxes)
    select.unuse()

    move = Shader()
    with open("shaders/move.comp", "r") as f:
        move.attach_shader(f.read(), GL_COMPUTE_SHADER)
    move.link()
    move.use()
    glUniform1ui(1, num_boxes)
    move.unuse()

    data["select"] = select
    data["move"] = move
    data["select_box"] = select_box
    data["select_border"] = select_border

    data["prev_mouse"] = (-2, -2)
    data["ubo"] = ubo
    data["select_box_visible"] = False

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glClearColor(0, 0, 0, 1)
    while glfw.window_should_close(window) == glfw.FALSE:
        glClear(GL_COLOR_BUFFER_BIT)

        program.use()
        glBindVertexArray(vao)
        glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, num_boxes)
        glBindVertexArray(0)
        program.unuse()

        if data["select_box_visible"]:
            select_box.use()
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
            glBindVertexArray(0)
            select_box.unuse()

            select_border.use()
            glBindVertexArray(vao)
            glDrawArrays(GL_LINE_LOOP, 0, 4)
            glBindVertexArray(0)
            select_border.unuse()


        glfw.swap_buffers(window)
        glfw.wait_events()

    glDeleteBuffers(len(ssbos), ssbos)
    glDeleteBuffers(1, [ubo])
    glDeleteVertexArrays(1, [vao])
    glDeleteProgram(select_box.handle)
    glDeleteProgram(select_border.handle)
    glDeleteProgram(select.handle)
    glDeleteProgram(program.handle)
    
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
