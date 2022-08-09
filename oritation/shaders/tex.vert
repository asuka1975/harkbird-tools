#version 460

layout (location = 0) out vec2 outUV;

const vec2[4] vertices = vec2[](
    vec2(-1, 1), vec2(1, 1),
    vec2(-1, -1), vec2(1, -1)
);

const vec2[4] uvs = vec2[](
    vec2(0, 1), vec2(1, 1),
    vec2(0, 0), vec2(1, 0)
);

void main() {
    outUV = uvs[gl_VertexID];
    gl_Position = vec4(vertices[gl_VertexID], 0, 1);
}