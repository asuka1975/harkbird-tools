from ctypes import Structure, sizeof

from OpenGL.GL import *
import glfw

import freetype

from shader import Shader

class CharData(Structure):
    _fields_ = [
        ("uv", GLfloat * 2),
        ("width", GLfloat * 2)
    ]

class Vertex(Structure):
    _fields_ = [
        ("char_id", GLuint),
        ("position", GLfloat * 2),
        ("size", GLfloat),
        ("offset", GLfloat),
    ]

def framebuffer_size_callback(window, width, height):
    program = glfw.get_window_user_pointer(window)["program"]
    glViewport(0, 0, width, height)
    program.use()
    glUniform2f(1, width, height)
    program.unuse()

def text(s, pos, size, advances, align=("top", "left")):
    sum_advances = 0
    vertices = []
    if align[1] == "right":
        s = s[::-1]
    for c in s:
        c = int(c)
        vertices.append(Vertex(c, (GLfloat * 2)(pos[0], pos[1]), size, sum_advances))
        sum_advances += advances[c] * size
    return vertices


def main():
    if glfw.init() == glfw.FALSE:
        raise RuntimeError("failed to initialize GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.SAMPLES, 8)

    window = glfw.create_window(1000, 1000, "sample", None, None)
    if window is None:
        raise RuntimeError("failed to create GLFWwindow")
    glfw.make_context_current(window)

    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    face = freetype.Face("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf")
    sizes = [48 * 16, 48 * 24, 48 * 32, 48*64, 48*128, 48*256]
    for mipmap, size in enumerate(sizes):
        face.set_char_size(size)
        textures = []
        width = 0
        height = 0
        for i in range(10):
            face.load_char(f"{i}")
            bitmap = face.glyph.bitmap
            width += bitmap.width
            height = max(height, bitmap.rows)
            buffer = [0 for _ in range((height - bitmap.rows) * bitmap.width)] + bitmap.buffer
            textures.append((bitmap.width, (GLubyte * len(buffer))(*buffer)))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, len(sizes) - 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, len(sizes) - 1)
        glTexImage2D(GL_TEXTURE_2D, mipmap, GL_RGBA8, width, height, 0, GL_RED, GL_UNSIGNED_BYTE, None)
        x = 0
        for w, texture in textures:
            glTexSubImage2D(GL_TEXTURE_2D, mipmap, x, 0, w, height, GL_RED, GL_UNSIGNED_BYTE, texture)
            x += w

    uv = []
    advances = []
    widths = []
    max_height = 0
    uv_offset = 0
    face.set_char_size(48*512)
    for i in range(10):
        face.load_char(f"{i}")
        uv.append((uv_offset, face.glyph.bitmap.width))
        widths.append(face.glyph.bitmap.width)
        uv_offset += face.glyph.bitmap.width
        advances.append(face.glyph.advance.x >> 6)
        max_height = max(max_height, face.glyph.bitmap.rows)
    uv = list(map(lambda x: (x[0] / (uv[-1][0] + uv[-1][1]), x[1] / (uv[-1][0] + uv[-1][1])), uv))
    advances = list(map(lambda x: x / max_height, advances))
    widths = list(map(lambda x: x / max_height, widths))

    chardata = (CharData * len(widths))(*[CharData((GLfloat * 2)(*uv[i]), (GLfloat * 2)(widths[i], 0)) for i in range(len(widths))])
    ssbo = glGenBuffers(1)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(chardata), chardata, GL_STATIC_DRAW)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssbo)

    vertices = text("1002193516784", (1, 0.5), 0.2, advances, align=("middle", "right"))
    vertices.extend(text("51000", (0, 0), 0.15, advances, align=("middle", "right")))
    vertices.extend(text("9878621", (0.5, -0.5), 0.05, advances, align=("middle", "right")))
    vertices.extend(text("01122", (1, 1), 0.05, advances, align=("middle", "right")))
    num_vertices = len(vertices)
    vertices = (Vertex * num_vertices)(*vertices)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_DYNAMIC_DRAW)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glEnableVertexAttribArray(2)
    glEnableVertexAttribArray(3)
    glVertexAttribIPointer(0, 1, GL_UNSIGNED_INT, sizeof(Vertex), GLvoidp(Vertex.char_id.offset))
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), GLvoidp(Vertex.position.offset))
    glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, sizeof(Vertex), GLvoidp(Vertex.size.offset))
    glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, sizeof(Vertex), GLvoidp(Vertex.offset.offset))
    glBindVertexArray(0)

    program = Shader()
    with open("shaders/font_rightmiddle.vert", "r") as f:
        program.attach_shader(f.read(), GL_VERTEX_SHADER)
    with open("shaders/font_rightmiddle.geom", "r") as f:
        program.attach_shader(f.read(), GL_GEOMETRY_SHADER)
    with open("shaders/font.frag", "r") as f:
        program.attach_shader(f.read(), GL_FRAGMENT_SHADER)
    program.link()
    program.use()
    glUniform1i(0, 0)
    glUniform2f(1, 1000, 1000)
    program.unuse()

    data = {
        "program" : program
    }
    glfw.set_window_user_pointer(window, data)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(1, 1, 1, 1)
    while glfw.window_should_close(window) == glfw.FALSE:
        glClear(GL_COLOR_BUFFER_BIT)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex)
        program.use()
        glBindVertexArray(vao)
        glDrawArrays(GL_POINTS, 0, num_vertices)
        glBindVertexArray(0)
        program.unuse()

        glfw.swap_buffers(window)
        glfw.wait_events()
    
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()