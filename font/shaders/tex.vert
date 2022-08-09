#version 460

const vec2[] position = vec2[] (
    vec2(-1, 1), vec2(1, 1),
    vec2(-1, -1), vec2(1, -1)
);

const vec2[] uv = vec2[] (
    vec2(0, 0), vec2(1, 0),
    vec2(0, 1), vec2(1, 1)
);

layout (location = 0) out vec2 outUv;

void main() {
    gl_Position = vec4(position[gl_VertexID], 0, 1);
    outUv = uv[gl_VertexID];
}