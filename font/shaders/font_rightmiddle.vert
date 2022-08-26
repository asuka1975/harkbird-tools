#version 460

layout (location = 1) uniform vec2 screen;

layout (location = 0) in uint char_id;
layout (location = 1) in vec2 position;
layout (location = 2) in float size;
layout (location = 3) in float offset;

layout (location = 0) out uint outChar_id;
layout (location = 1) out float outSize;

void main() {
    outChar_id = char_id;
    outSize = size;
    gl_Position = vec4(position + vec2(-offset, 0) * screen.y / screen.x, 0, 1);
}