FRAG = """#version 460

layout (location = 0) out vec4 outColor;

layout (location = 4) uniform vec4 color;

void main() {
    outColor = color;
}
"""