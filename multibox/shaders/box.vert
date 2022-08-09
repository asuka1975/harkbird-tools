#version 460

struct Box {
    vec2 range;
    float value;
    int color_id;
};

layout (std430, binding = 0) buffer SSBO {
    Box boxes[];
};

layout (std430, binding = 1) buffer Select {
    int selects[];
};

layout (location = 0) out vec3 outColor;

const float height = 0.01;
const vec3[6] colors = vec3[](
    vec3(1, 0, 0), vec3(0, 1, 0), vec3(0, 0, 1), 
    vec3(0, 1, 1), vec3(1, 0, 1), vec3(1, 1, 0)
);

void main() {
    Box box = boxes[gl_InstanceID];
    vec2[4] vertices = vec2[](
        vec2(box.range.x, box.value + height), vec2(box.range.y, box.value + height),
        vec2(box.range.x, box.value - height), vec2(box.range.y, box.value - height)
    );
    gl_Position = vec4(vertices[gl_VertexID], 0, 1);
    outColor = colors[box.color_id] + float(selects[gl_InstanceID]) * vec3(0.7);
}