#version 460

layout (std140, binding = 2) uniform Rect {
    vec2 leftbottom;
    vec2 righttop;
};

void main() {
    vec2[4] vertices = vec2[](
        vec2(leftbottom.x, righttop.y), righttop,
        vec2(righttop.x, leftbottom.y), leftbottom
    );
    gl_Position = vec4(vertices[gl_VertexID], 0, 1);
}