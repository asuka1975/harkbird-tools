from ctypes import Structure, sizeof
import sys

import glfw
from OpenGL.GL import *
from pydub import AudioSegment
import librosa
import numpy as np

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

def min_max(x, axis=None):
    min = x.min(axis=axis, keepdims=True)
    max = x.max(axis=axis, keepdims=True)
    result = (x-min)/(max-min)
    return result

def key_callback(window, key, scancode, action, mods):
    data = glfw.get_window_user_pointer(window)
    if key == glfw.KEY_UP and action in (glfw.PRESS, glfw.REPEAT):
        data["rate"] += 0.01
    if key == glfw.KEY_DOWN and action in (glfw.PRESS, glfw.REPEAT):
        data["rate"] -= 0.01
    data["program"].use()
    glUniform1f(1, data["rate"])
    data["program"].unuse()
    print(data["rate"])

def main():
    if glfw.init() == glfw.FALSE:
        raise RuntimeError("failed to initialize GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    window = glfw.create_window(1500, 900, "spectrum", None, None)

    if not window:
        raise RuntimeError("failed to create GLFWwindow")
    glfw.make_context_current(window)

    directory = "localized_20220603-123920-0-001_8min_16k_gained.wav"
    wavname = f"{directory}/remixed.wav"
    recording = AudioSegment.from_wav(wavname)
    n_fft = 4096
    win_length = None
    hop_length = 512 
    window_fn = 'hann'
    y = np.array(recording.get_array_of_samples()) / 10000.0
    spec = np.abs(librosa.stft(y=y, n_fft=n_fft, hop_length=hop_length, win_length=win_length, window=window_fn))**2
    spec = (min_max(librosa.power_to_db(spec))).astype(np.float32)

    tex = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexStorage2D(GL_TEXTURE_2D, 4, GL_R32F, spec.shape[1], spec.shape[0])
    bytes = spec.tobytes()
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, spec.shape[1], spec.shape[0], GL_RED, GL_FLOAT, bytes)
    glGenerateMipmap(GL_TEXTURE_2D)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    vao = glGenVertexArrays(1)

    program = Shader()
    with open("shaders/tex.vert", "r") as f:
        program.attach_shader(f.read(), GL_VERTEX_SHADER)
    with open("shaders/tex.frag", "r") as f:
        program.attach_shader(f.read(), GL_FRAGMENT_SHADER)
    program.link()
    program.use()
    glUniform1i(0, 0)
    glUniform1f(1, 2)
    program.unuse()

    data = {
        "program" : program,
        "rate" : 1
    }
    glfw.set_window_user_pointer(window, data)
    glfw.set_key_callback(window, key_callback)

    glClearColor(0, 0, 0, 1)
    while glfw.window_should_close(window) == glfw.FALSE:
        glClear(GL_COLOR_BUFFER_BIT)

        glBindTexture(GL_TEXTURE_2D, tex)
        glActiveTexture(GL_TEXTURE0)

        program.use()
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glBindVertexArray(0)
        program.unuse()

        glfw.swap_buffers(window)
        glfw.wait_events()

    glDeleteTextures(1, [tex])
    glDeleteVertexArrays(1, [vao])
    glDeleteProgram(program.handle)
    
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()