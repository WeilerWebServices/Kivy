/* simple.glsl

simple diffuse lighting based on laberts cosine law; see e.g.:
    http://en.wikipedia.org/wiki/Lambertian_reflectance
    http://en.wikipedia.org/wiki/Lambert%27s_cosine_law
*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif


attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec4 v_color;
attribute vec2 v_tc0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform mat4 normal_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

varying vec4 normal_vec;
varying vec4 vertex_pos;
varying vec4 frag_color;
varying vec2 uv_vec;

void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    vertex_pos = pos;
    normal_vec = vec4(v_normal,0.0);

    frag_color = v_color;
    uv_vec = v_tc0;

    gl_Position = projection_mat * pos;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 normal_vec;
varying vec4 vertex_pos;

uniform mat4 normal_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

uniform vec3 camera_pos;
uniform vec3 Ka; // color (ambient)
uniform vec3 Kd; // diffuse color
uniform vec3 Ks; // specular color
uniform float Tr; // transparency
uniform float Ns; // shininess
uniform float tex_ratio;

uniform vec3 light_pos;
uniform float light_intensity;


void main (void){
    //correct normal, and compute light vector (assume light at the eye)
    vec4 v_normal = normalize( normal_mat * normal_vec ) ;
    vec4 v_light = normalize( vec4(0,0,0,1) - vertex_pos );

    // force lightPos to lower-left (like in Kivy)
    vec4 lightPos = model_mat * vec4(light_pos, 0.0) - gl_FragCoord;
    float lightPosLen = length(lightPos);

    // set ambient, diffuse, specular color
    vec3 Ia = Ka * light_intensity / lightPosLen;
    vec3 Id = Kd * max(dot(v_light, v_normal), 0.0);
    vec3 Is = Ks * pow(max(dot(v_light, v_normal), 0.0), Ns);

    //reflectance based on lamberts law of cosine
    float theta = clamp(dot(v_normal, v_light), 0.1, 1.0);
    vec3 thetaColor = theta * vec3(Ia + Id + Is);

    gl_FragColor = vec4(thetaColor, Tr);
}
