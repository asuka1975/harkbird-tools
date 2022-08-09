#version 460

layout (location = 0) in vec2 uv;

layout (location = 0) out vec4 outColor;

layout (location = 0) uniform sampler2D tex;
layout (location = 1) uniform float r;

vec3 hsvToRgb(float h, float s, float v) {
    // h: 0.0 - 360.0, s: 0.0 - 1.0, v: 0.0 - 1.0
    float c = s; // float c = v * s;
    float h2 = h / 60.0;
    float x = c * (1.0 - abs(mod(h2, 2.0) - 1.0));
    vec3 rgb = (v - c) * vec3(1.0, 1.0, 1.0);

    if (0.0 <= h2 && h2 < 1.0) {
        rgb += vec3(c, x, 0.0);
    } else if (1.0 <= h2 && h2 < 2.0) {
        rgb += vec3(x, c, 0.0);
    } else if (2.0 <= h2 && h2 < 3.0) {
        rgb += vec3(0.0, c, x);
    } else if (3.0 <= h2 && h2 < 4.0) {
        rgb += vec3(0.0, x, c);
    } else if (4.0 <= h2 && h2 < 5.0) {
        rgb += vec3(x, 0.0, c);
    } else if (5.0 <= h2 && h2 < 6.0) {
        rgb += vec3(c, 0.0, x);
    }

    return rgb;
}

void main() {
    float v = texture2D(tex, uv).r;
    v = pow(v, r);
    outColor = vec4(hsvToRgb(240 * (1 - v), 1, 1), 1);
}