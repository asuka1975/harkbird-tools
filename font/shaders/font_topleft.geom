#version 460 

layout (points) in;
layout (triangle_strip, max_vertices=4) out;

layout (location = 1) uniform vec2 screen;

struct CharData {
    vec2 uv;
    vec2 width;
};

layout (std430, binding = 0) buffer Widths {
    CharData chardata[];
};

layout (location = 0) in uint char_id[];
layout (location = 1) in float size[];

layout (location = 0) out vec2 outUv;

void main() {
    vec2 position = gl_in[0].gl_Position.xy;
    uint id = char_id[0];
    float sz = size[0];
    gl_Position = vec4(position, 0, 1);
    outUv = vec2(chardata[id].uv.x, 0);
    EmitVertex();

    gl_Position = vec4(position + vec2(chardata[id].width.x, 0) * sz * screen.y / screen.x, 0, 1);
    outUv = vec2(chardata[id].uv.x + chardata[id].uv.y, 0);
    EmitVertex();
    
    gl_Position = vec4(position + vec2(0, -1) * sz, 0, 1);
    outUv = vec2(chardata[id].uv.x, 1);
    EmitVertex();

    gl_Position = vec4(position + vec2(chardata[id].width.x * screen.y / screen.x, -1) * sz, 0, 1);
    outUv = vec2(chardata[id].uv.x + chardata[id].uv.y, 1);
    EmitVertex();
    EndPrimitive();
}