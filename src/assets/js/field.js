/* SEA Audit · animated contour field (WebGL). Loaded after the page is idle. */
(function () {
  'use strict';
  var html = document.documentElement;
  if (html.classList.contains('no-motion')) return;
  var canvas = document.createElement('canvas');
  canvas.id = 'field';
  canvas.setAttribute('aria-hidden', 'true');
  var gl = null;
  try { gl = canvas.getContext('webgl', { antialias: false, alpha: false, depth: false, stencil: false, powerPreference: 'low-power' }); } catch (e) { gl = null; }
  if (!gl) return;
  // Software renderers (no GPU) make a full-screen shader slow: keep the static background instead.
  try {
    var dbg = gl.getExtension('WEBGL_debug_renderer_info');
    var renderer = String(dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
    if (/swiftshader|llvmpipe|softpipe|software|basic render/i.test(renderer)) return;
  } catch (e) {}
  if (navigator.connection && navigator.connection.saveData) return;
  var deriv = !!gl.getExtension('OES_standard_derivatives');

  var FRAG = [
    '#ifdef GL_FRAGMENT_PRECISION_HIGH', 'precision highp float;', '#else', 'precision mediump float;', '#endif',
    'uniform vec2 u_res;uniform float u_time;uniform vec2 u_mouse;uniform float u_scroll;uniform float u_tilt;uniform float u_heat;uniform float u_glow;',
    'vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}',
    'vec2 mod289(vec2 x){return x-floor(x*(1.0/289.0))*289.0;}',
    'vec3 permute(vec3 x){return mod289(((x*34.0)+1.0)*x);}',
    'float snoise(vec2 v){const vec4 C=vec4(0.211324865405187,0.366025403784439,-0.577350269189626,0.024390243902439);',
    'vec2 i=floor(v+dot(v,C.yy));vec2 x0=v-i+dot(i,C.xx);vec2 i1=(x0.x>x0.y)?vec2(1.0,0.0):vec2(0.0,1.0);',
    'vec4 x12=x0.xyxy+C.xxzz;x12.xy-=i1;i=mod289(i);vec3 p=permute(permute(i.y+vec3(0.0,i1.y,1.0))+i.x+vec3(0.0,i1.x,1.0));',
    'vec3 m=max(0.5-vec3(dot(x0,x0),dot(x12.xy,x12.xy),dot(x12.zw,x12.zw)),0.0);m=m*m;m=m*m;',
    'vec3 x=2.0*fract(p*C.www)-1.0;vec3 h=abs(x)-0.5;vec3 ox=floor(x+0.5);vec3 a0=x-ox;',
    'm*=1.79284291400159-0.85373472095314*(a0*a0+h*h);vec3 g;g.x=a0.x*x0.x+h.x*x0.y;g.yz=a0.yz*x12.xz+h.yz*x12.yw;return 130.0*dot(m,g);}',
    'float fbm(vec2 p){float f=0.0;float a=0.5;mat2 r=mat2(0.8,0.6,-0.6,0.8);for(int i=0;i<4;i++){f+=a*snoise(p);p=r*p*2.02+1.7;a*=0.5;}return f;}',
    'float hash(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}',
    'void main(){',
    ' vec2 uv=(gl_FragCoord.xy-0.5*u_res)/u_res.y;',
    ' float horizon=mix(3.2,0.95,u_tilt);float d=horizon/(horizon-uv.y);vec2 p=uv*d;',
    ' vec2 q=p*1.15+vec2(-0.3,u_scroll*2.6+u_time*0.01);',
    ' vec2 w=vec2(snoise(q*0.5+vec2(u_time*0.018,0.0)),snoise(q*0.5+vec2(4.1,-u_time*0.015)));',
    ' float h=fbm(q+0.42*w);float f=h*7.5;',
    '#ifdef HAS_DERIV', ' float fw=fwidth(f);', '#else', ' float fw=0.045*d;', '#endif',
    ' fw=max(fw,0.0001);float dist=abs(fract(f+0.5)-0.5);float line=1.0-smoothstep(0.0,fw*1.25,dist);',
    ' float major=1.0-smoothstep(0.0,fw*0.35,abs(fract(f/5.0+0.5)-0.5));line*=1.0-smoothstep(0.35,0.9,fw);',
    ' float hi=smoothstep(-0.4,0.7,h);float md=length(uv-u_mouse);float glow=exp(-md*md*6.0)*u_glow;',
    ' vec3 bg=vec3(0.020,0.055,0.098);vec3 bone=vec3(0.80,0.86,0.93);vec3 lime=vec3(0.83,0.95,0.35);',
    ' vec3 lc=mix(bone,lime,clamp(u_heat*0.7+glow*0.9,0.0,1.0));',
    ' float a=line*(0.045+0.11*hi+0.09*major)*(1.0+glow*2.2);',
    ' vec3 col=bg+lc*a+lime*glow*0.025;',
    ' col*=1.0-0.55*smoothstep(0.35,1.35,length(uv*vec2(0.72,1.0)));',
    ' col=mix(col,bg,smoothstep(horizon-0.95,horizon-0.15,uv.y)*u_tilt);',
    ' col+=(hash(gl_FragCoord.xy+fract(u_time)*91.0)-0.5)*0.018;',
    ' gl_FragColor=vec4(col,1.0);}'
  ].join('\n');

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  var prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, 'attribute vec2 a;void main(){gl_Position=vec4(a,0.0,1.0);}'));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, (deriv ? '#extension GL_OES_standard_derivatives : enable\n#define HAS_DERIV 1\n' : '') + FRAG));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error('link');
  } catch (err) { return; }
  gl.useProgram(prog);
  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var aLoc = gl.getAttribLocation(prog, 'a');
  gl.enableVertexAttribArray(aLoc);
  gl.vertexAttribPointer(aLoc, 2, gl.FLOAT, false, 0, 0);
  var U = {};
  ['u_res', 'u_time', 'u_mouse', 'u_scroll', 'u_tilt', 'u_heat', 'u_glow'].forEach(function (n) { U[n] = gl.getUniformLocation(prog, n); });

  document.body.insertBefore(canvas, document.body.firstChild);
  var small = window.matchMedia('(max-width: 899px)').matches;
  var fine = window.matchMedia('(pointer: fine)').matches;
  var W = 0, H = 0;
  function size() {
    var w = window.innerWidth, h = window.innerHeight;
    if (W && Math.abs(w - W) < 1 && Math.abs(h - H) < 140) return;
    W = w; H = h;
    var dpr = Math.min(window.devicePixelRatio || 1, small ? 1 : 1.35);
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
  }
  size();
  window.addEventListener('resize', size, { passive: true });

  var m = { x: 0.35, y: 0.1 }, mc = { x: 0.35, y: 0.1 }, glowT = 0, glowC = 0;
  if (fine) window.addEventListener('pointermove', function (e) {
    m.x = (e.clientX - window.innerWidth / 2) / window.innerHeight;
    m.y = -(e.clientY - window.innerHeight / 2) / window.innerHeight;
    glowT = 1;
  }, { passive: true });

  var heatEls = Array.prototype.slice.call(document.querySelectorAll('[data-heat]'));
  var st = { tilt: 0.12, heat: 0, scroll: 0 }, cur = { tilt: 0.12, heat: 0, scroll: 0 };
  function targets() {
    var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    var p = window.scrollY / max;
    st.scroll = window.scrollY / Math.max(1, window.innerHeight) * 0.12;
    st.tilt = 0.12 + Math.min(1, window.scrollY / window.innerHeight) * 0.6 - p * 0.25;
    var heat = 0;
    heatEls.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var v = 1 - Math.min(1, Math.abs(r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight);
      heat = Math.max(heat, v);
    });
    st.heat = heat;
  }

  var visible = true, t0 = performance.now(), running = false, n = 0;
  document.addEventListener('visibilitychange', function () { visible = !document.hidden; if (visible) loop(); });
  function frame(now) {
    running = false;
    if (!visible) return;
    if (small && (n++ & 1)) { loop(); return; }
    targets();
    var k = 0.06;
    cur.tilt += (st.tilt - cur.tilt) * k;
    cur.heat += (st.heat - cur.heat) * k;
    cur.scroll += (st.scroll - cur.scroll) * 0.08;
    mc.x += (m.x - mc.x) * 0.07; mc.y += (m.y - mc.y) * 0.07;
    glowC += (glowT - glowC) * 0.04;
    gl.uniform2f(U.u_res, canvas.width, canvas.height);
    gl.uniform1f(U.u_time, (now - t0) / 1000);
    gl.uniform2f(U.u_mouse, mc.x, mc.y);
    gl.uniform1f(U.u_scroll, cur.scroll);
    gl.uniform1f(U.u_tilt, cur.tilt);
    gl.uniform1f(U.u_heat, cur.heat);
    gl.uniform1f(U.u_glow, fine ? glowC : 0.0);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    loop();
  }
  function loop() { if (running) return; running = true; requestAnimationFrame(frame); }
  loop();
  requestAnimationFrame(function () { canvas.classList.add('on'); html.classList.add('has-field'); });
})();
