// Basic 1000 teaching pictures: stick figures in the "Faces" style, drawn live with D3.
// A scene is a function of time that returns primitives (lines, shapes, text). Figures are
// skeletons posed by joint angles; animals and objects are small line drawings in the same style.
// Public API: BASIC_FIGURES.has(word), .label(word), .mountAll(container)
var BASIC_FIGURES = (function () {
  var d3 = window.d3;
  if (!d3) return { has: function () { return false; }, label: function () { return ''; }, mountAll: function () {} };

  // ---------- geometry ----------
  var DEG = Math.PI / 180, G = 140; // G: the ground line
  function P(o, len, a) { return [o[0] + len * Math.sin(a * DEG), o[1] + len * Math.cos(a * DEG)]; }
  var DIMS = { head: 9, neck: 3, torso: 30, upper: 15, fore: 14, thigh: 21, shin: 20 };
  var HEAD_SCALE = 1.32;
  var COL = {
    ink: 'var(--ink)', acc: 'var(--tab)', ground: 'var(--fig-ground)', card: 'var(--card)', rule: 'var(--rule)',
    marker: 'var(--marker)', red: 'var(--fig-red, #d6463a)', water: 'var(--fig-water, #6eb4e6)',
    milk: 'var(--fig-milk, #ffffff)', hot: 'var(--fig-hot, #e9822f)', cold: 'var(--fig-cold, #7cc7ee)',
    leaf: 'var(--fig-leaf, #4e9a50)', book: 'var(--fig-book, #8fb1d6)'
  };

  // angles in degrees: 0 points down, 90 points forward, 180 points up. arms: [back upper, back fore, front upper, front fore]
  var LEGS = [-14, -6, 14, 6];
  function pose(arms, legs) { return { lean: 0, head: 0, arms: arms, legs: legs || LEGS }; }
  var POSES = {
    stand: pose([-26, -14, 26, 14]),
    chest: pose([-26, -14, 58, -112]),
    point: pose([-26, -14, 84, 88]),
    give: pose([-26, -14, 60, 92]),
    hold: pose([-26, -14, 22, 100]),
    shrug: pose([-50, -140, 50, 140]),
    pull: pose([-26, -14, 12, 165]),
    eat: pose([-26, -14, 30, 168]),
    sit: pose([-26, -14, 26, 60], [88, 0, 96, 6]),
    kick: pose([-40, -24, 30, 18], [-12, -4, 62, 70]),
    reach: pose([-26, -14, 150, 168]),
    sad: pose([-12, -4, 12, 4])
  };
  var mix = function (a, b, k) { return d3.interpolate(a, b)(k); };
  function waving(t) { return pose([-26, -14, 152, 172 + 22 * Math.sin(t / 140)]); }
  function walking(t, base) {
    var s = 22 * Math.sin(t / 150), p = JSON.parse(JSON.stringify(base || POSES.stand));
    p.legs = [-s, -s * 0.4 - 3, s, s * 0.4 + 3];
    p.arms = [p.arms[0] + s * 0.6, p.arms[1] + s * 0.6, p.arms[2] - s * 0.6, p.arms[3] - s * 0.6];
    return p;
  }

  function skeleton(ps, f, s) {
    var d = {}; Object.keys(DIMS).forEach(function (k) { d[k] = DIMS[k] * s; });
    var up = f * (180 - ps.lean), hip = [0, 0];
    var sh = P(hip, d.torso - 3 * s, up), neck = P(hip, d.torso, up);
    var eL = P(sh, d.upper, f * ps.arms[0]), eR = P(sh, d.upper, f * ps.arms[2]);
    var kL = P(hip, d.thigh, f * ps.legs[0]), kR = P(hip, d.thigh, f * ps.legs[2]);
    return {
      hip: hip, neck: neck, sh: sh, headDir: f * (180 - ps.lean - ps.head),
      eL: eL, hL: P(eL, d.fore, f * ps.arms[1]), eR: eR, hR: P(eR, d.fore, f * ps.arms[3]),
      kL: kL, fL: P(kL, d.shin, f * ps.legs[1]), kR: kR, fR: P(kR, d.shin, f * ps.legs[3])
    };
  }

  // A person. kind: man | woman | boy | girl. Returns primitives, with .hand (front hand) and .head set.
  function figure(o) {
    var kind = o.kind || 'man', child = kind === 'boy' || kind === 'girl';
    var s = o.s || (child ? 0.68 : 1), f = o.facing || 1, k = skeleton(o.pose || POSES.stand, f, s);
    var x = o.x + (o.dx || 0), dy = G - Math.max(k.fL[1], k.fR[1]);
    Object.keys(k).forEach(function (key) { if (Array.isArray(k[key])) k[key] = [k[key][0] + x, k[key][1] + dy]; });
    var r = DIMS.head * HEAD_SCALE * s * (child ? 1.12 : 1);
    var hc = P(k.neck, DIMS.neck * s + r, k.headDir), neckEnd = P(k.neck, DIMS.neck * s, k.headDir);
    var c = o.accent ? COL.acc : (o.c || COL.ink), w = child ? 2.8 : 3.2;
    var out = [];
    if (kind === 'woman') out.push({ t: 'circle', x: hc[0] - f * r * 0.62, y: hc[1] - r * 0.88, r: r * 0.4, c: c, w: 2.6, fill: COL.ground });
    if (kind === 'girl') out.push({ t: 'path', d: 'M' + (hc[0] - f * r * 0.8) + ',' + (hc[1] - r * 0.45) + 'Q' + (hc[0] - f * (r + 6 * s)) + ',' + (hc[1] - r * 0.2) + ' ' + (hc[0] - f * (r + 4 * s)) + ',' + (hc[1] + r * 1.05), c: c, w: 2.6 });
    out.push(
      { t: 'chain', pts: [k.hip, k.kL, k.fL], c: c, w: w },
      { t: 'chain', pts: [k.hip, k.kR, k.fR], c: c, w: w },
      { t: 'chain', pts: [k.hip, neckEnd], c: c, w: w },
      { t: 'chain', pts: [k.sh, k.eL, k.hL], c: c, w: w },
      { t: 'chain', pts: [k.sh, k.eR, k.hR], c: c, w: w },
      { t: 'head', c: hc, r: r, f: f, col: c, look: o.look || 0 }
    );
    if (o.say) out.push({ t: 'bubble', text: o.say.text, hl: o.say.hl, cx: hc[0], top: hc[1] - r, f: f, col: c });
    out.hand = k.hR; out.backHand = k.hL; out.head = hc; out.r = r;
    if (o.op != null && o.op < 1) { var g = [{ t: 'group', op: o.op, prims: out }]; g.hand = out.hand; g.head = hc; g.r = r; return g; }
    return out;
  }

  // ---------- animals and objects (line drawings in the same style) ----------
  function ell(cx, cy, rx, ry) { return 'M' + (cx - rx) + ',' + cy + 'a' + rx + ',' + ry + ' 0 1,0 ' + 2 * rx + ',0a' + rx + ',' + ry + ' 0 1,0 ' + (-2 * rx) + ',0Z'; }
  function M(x, y) { return 'M' + x + ',' + y; }
  function L(x, y) { return 'L' + x + ',' + y; }

  function dog(o) {
    var s = o.s || 1, f = o.f || 1, x = o.x, c = o.c || COL.ink, t = o.t || 0, out = [], by = G - 17 * s;
    [[-10, -1], [-6, 1], [7, -1], [11, 1]].forEach(function (l) { var lx = x + f * l[0] * s; out.push({ t: 'path', d: M(lx, by + 3 * s) + L(lx + f * l[1] * s, G), c: c, w: 3 }); });
    var tail = P([x - f * 13 * s, by - 2 * s], 11 * s, -f * (140 + 22 * Math.sin(t / 110)));
    out.push({ t: 'path', d: M(x - f * 13 * s, by - 2 * s) + 'Q' + (x - f * 17 * s) + ',' + (by - 4 * s) + ' ' + tail[0] + ',' + tail[1], c: c, w: 3 });
    out.push({ t: 'path', d: M(x + f * 10 * s, by - 3 * s) + L(x + f * 14 * s, by - 9 * s), c: c, w: 3 });
    out.push({ t: 'path', d: ell(x, by, 15 * s, 7 * s), c: c, w: 3, fill: COL.ground });
    var hx = x + f * 15 * s, hy = by - 11 * s;
    // muzzle sticking out in front of the head, with the nose on its tip
    out.push({ t: 'path', d: M(hx + f * 2 * s, hy - 1.5 * s) + L(hx + f * 10 * s, hy - 0.5 * s) + 'Q' + (hx + f * 12 * s) + ',' + (hy + 2 * s) + ' ' + (hx + f * 10 * s) + ',' + (hy + 4.5 * s) + L(hx + f * 2 * s, hy + 5 * s) + 'Z', c: c, w: 2.6, fill: COL.ground });
    out.push({ t: 'path', d: ell(hx, hy, 6.2 * s, 5.8 * s), c: c, w: 3, fill: COL.ground });
    out.push({ t: 'path', d: M(hx + f * 2 * s, hy + 1 * s) + L(hx + f * 6 * s, hy + 1.5 * s), c: COL.ground, w: 3.4 });
    out.push({ t: 'circle', x: hx + f * 10.6 * s, y: hy + 0.8 * s, r: 1.7 * s, fill: c });
    out.push({ t: 'circle', x: hx + f * 1.8 * s, y: hy - 1.8 * s, r: 1.3, fill: c });
    // a floppy ear hanging at the back of the head
    out.push({ t: 'path', d: M(hx - f * 1 * s, hy - 5.2 * s) + 'q' + -f * 5.5 * s + ',' + 0.5 * s + ' ' + -f * 5 * s + ',' + 8.5 * s + 'q' + f * 2 * s + ',' + 1.2 * s + ' ' + f * 3.6 * s + ',' + -1 * s + 'Z', c: c, w: 1.6, fill: c });
    return wrap(out, o);
  }

  function cat(o) {
    var s = o.s || 1, f = o.f || 1, x = o.x, c = o.c || COL.ink, t = o.t || 0, out = [], by = G - 11 * s;
    var sway = 4 * Math.sin(t / 300) * s;
    out.push({ t: 'path', d: M(x - f * 10 * s, by - 1 * s) + 'Q' + (x - f * 20 * s) + ',' + (by - 2 * s) + ' ' + (x - f * 17 * s + sway) + ',' + (by - 13 * s) + 'q' + -f * 1 * s + ',' + -4 * s + ' ' + f * 3 * s + ',' + -5 * s, c: c, w: 2.6 });
    [[-7, 0], [-4, 0], [5, 0], [8, 0]].forEach(function (l) { var lx = x + f * l[0] * s; out.push({ t: 'path', d: M(lx, by + 2 * s) + L(lx, G), c: c, w: 2.6 }); });
    out.push({ t: 'path', d: ell(x, by, 11 * s, 5.5 * s), c: c, w: 2.6, fill: COL.ground });
    var hx = x + f * 12 * s, hy = by - 7 * s, r = 5.2 * s;
    out.push({ t: 'path', d: M(hx - f * 4.2 * s, hy - 2 * s) + L(hx - f * 3.6 * s, hy - 9 * s) + L(hx - f * 0.2 * s, hy - 4.6 * s) + 'Z' + M(hx + f * 0.9 * s, hy - 4.8 * s) + L(hx + f * 4.2 * s, hy - 9 * s) + L(hx + f * 4.8 * s, hy - 2 * s) + 'Z', c: c, w: 2, fill: COL.ground });
    out.push({ t: 'path', d: ell(hx, hy, r, r * 0.92), c: c, w: 2.6, fill: COL.ground });
    var blink = (t % 3200) < 140 ? 0.25 : 1;
    [hx - f * 1.2 * s, hx + f * 2.4 * s].forEach(function (ex) { out.push({ t: 'path', d: ell(ex, hy - 0.6 * s, 0.9, 1.3 * blink), fill: c }); });
    out.push({ t: 'path', d: M(hx + f * 3 * s, hy + 1.6 * s) + 'l' + f * 6 * s + ',' + -1 * s + M(hx + f * 3 * s, hy + 2.6 * s) + 'l' + f * 6 * s + ',' + 1 * s, c: c, w: 1 });
    return wrap(out, o);
  }

  function cow(o) {
    var s = o.s || 1, f = o.f || 1, x = o.x, c = o.c || COL.ink, t = o.t || 0, out = [];
    var top = G - 44 * s, bot = G - 21 * s, bx0 = x - 24 * s, bx1 = x + 20 * s;
    var tailEnd = [x - f * (27 + 2 * Math.sin(t / 260)) * s, G - 22 * s];
    out.push({ t: 'path', d: M(x - f * 24 * s, top + 3 * s) + 'Q' + (x - f * 29 * s) + ',' + (top + 10 * s) + ' ' + tailEnd[0] + ',' + tailEnd[1], c: c, w: 2.4 });
    out.push({ t: 'circle', x: tailEnd[0], y: tailEnd[1] + 1.5 * s, r: 2 * s, fill: c });
    [-19, -12, 9, 15].forEach(function (lx0) { var lx = x + f * lx0 * s; out.push({ t: 'path', d: M(lx, bot - 1) + L(lx, G), c: c, w: 3.2 }); });
    var l = Math.min(bx0, bx1), rgt = Math.max(bx0, bx1);
    if (f < 0) { l = x - 20 * s; rgt = x + 24 * s; }
    out.push({ t: 'path', d: M(l + 6 * s, top) + 'H' + (rgt - 6 * s) + 'Q' + rgt + ',' + top + ' ' + rgt + ',' + (top + 6 * s) + 'V' + (bot - 5 * s) + 'Q' + rgt + ',' + bot + ' ' + (rgt - 6 * s) + ',' + bot + 'H' + (l + 6 * s) + 'Q' + l + ',' + bot + ' ' + l + ',' + (bot - 5 * s) + 'V' + (top + 6 * s) + 'Q' + l + ',' + top + ' ' + (l + 6 * s) + ',' + top + 'Z', c: c, w: 3, fill: COL.ground });
    out.push({ t: 'path', d: ell(x - f * 9 * s, top + 9 * s, 5.5 * s, 4 * s), fill: c });
    out.push({ t: 'path', d: ell(x + f * 7 * s, top + 15 * s, 4.5 * s, 3.4 * s), fill: c });
    out.push({ t: 'path', d: M(x + f * 1 * s, bot) + 'q' + f * 3.5 * s + ',' + 5.5 * s + ' ' + f * 7 * s + ',0', c: c, w: 2.2, fill: COL.ground });
    var nod = 1.5 * Math.sin(t / 500) * s, hx = x + f * 27 * s, hy = top + 4 * s + nod;
    out.push({ t: 'path', d: M(hx - f * 3 * s, hy - 7 * s) + 'q' + -f * 3 * s + ',' + -4 * s + ' ' + -f * 1 * s + ',' + -7 * s + M(hx + f * 3 * s, hy - 7 * s) + 'q' + f * 3 * s + ',' + -4 * s + ' ' + f * 1 * s + ',' + -7 * s, c: c, w: 2.2 });
    out.push({ t: 'path', d: ell(hx, hy, 6.5 * s, 8.5 * s), c: c, w: 3, fill: COL.ground });
    out.push({ t: 'path', d: ell(hx + f * 1 * s, hy + 7 * s, 6 * s, 4 * s), c: c, w: 2.4, fill: COL.ground });
    out.push({ t: 'circle', x: hx - 1.6 * s + f * 1 * s, y: hy + 7 * s, r: 0.9 * s, fill: c });
    out.push({ t: 'circle', x: hx + 1.6 * s + f * 1 * s, y: hy + 7 * s, r: 0.9 * s, fill: c });
    out.push({ t: 'circle', x: hx + f * 2 * s, y: hy - 2 * s, r: 1.3, fill: c });
    return wrap(out, o);
  }

  function house(o) {
    var s = o.s || 1, x = o.x, c = o.c || COL.ink, w = 28 * s, h = 40 * s, out = [];
    out.push({ t: 'path', d: M(x - w, G) + 'V' + (G - h) + 'H' + (x + w) + 'V' + G + 'Z', c: c, w: 3, fill: COL.ground });
    out.push({ t: 'path', d: M(x - w - 6 * s, G - h) + L(x, G - h - 26 * s) + L(x + w + 6 * s, G - h) + 'Z', c: c, w: 3, fill: COL.ground });
    var wx = x + 9 * s, wy = G - 31 * s, ww = 12 * s;
    out.push({ t: 'path', d: M(wx, wy) + 'h' + ww + 'v' + ww + 'h' + (-ww) + 'Z', c: c, w: 2, fill: o.windowFill || COL.ground });
    if (o.windowCat) { // a small cat looking out of the window
      var cx = wx + ww / 2, cy = wy + ww * 0.62, cr = 3.2 * s;
      out.push({ t: 'path', d: M(cx - 3 * s, cy - 1.5 * s) + L(cx - 2.6 * s, cy - 5.6 * s) + L(cx - 0.3 * s, cy - 3 * s) + 'Z' + M(cx + 0.3 * s, cy - 3 * s) + L(cx + 2.6 * s, cy - 5.6 * s) + L(cx + 3 * s, cy - 1.5 * s) + 'Z', c: c, w: 1.4, fill: COL.ground, op: o.windowCat });
      out.push({ t: 'path', d: ell(cx, cy, cr, cr * 0.9), c: c, w: 1.6, fill: COL.ground, op: o.windowCat });
      out.push({ t: 'circle', x: cx - 1.1 * s, y: cy - 0.4 * s, r: 0.7, fill: c, op: o.windowCat });
      out.push({ t: 'circle', x: cx + 1.1 * s, y: cy - 0.4 * s, r: 0.7, fill: c, op: o.windowCat });
    }
    out.push({ t: 'path', d: M(wx + ww / 2, wy) + 'v' + ww + M(wx, wy + ww / 2) + 'h' + ww, c: c, w: 1.6, op: o.windowCat ? 1 - o.windowCat : 1 });
    var dx = x - 18 * s, dw = 13 * s, dh = 25 * s, open = o.door || 0;
    if (open > 0) out.push({ t: 'path', d: M(dx, G) + 'V' + (G - dh) + 'h' + dw + 'V' + G + 'Z', fill: c, op: 0.82 });
    var pw = dw * (1 - 0.82 * open);
    out.push({ t: 'path', d: M(dx, G) + 'V' + (G - dh) + 'h' + pw + 'V' + G + 'Z', c: o.doorLine || c, w: o.doorLine ? 3 : 2.4, fill: o.doorFill || COL.ground });
    if (open < 0.5) out.push({ t: 'circle', x: dx + pw - 3 * s, y: G - 12 * s, r: 1.3 * s, fill: c });
    var res = wrap(out, o); res.door = [dx + dw / 2, G - dh / 2]; res.top = G - h - 26 * s; return res;
  }

  function apple(o) {
    var x = o.x, y = o.y, r = o.r || 6, c = o.c || COL.ink;
    return wrap([
      { t: 'path', d: M(x, y - r * 0.7) + 'q' + r * 0.1 + ',' + -r * 0.45 + ' ' + r * 0.35 + ',' + -r * 0.62, c: c, w: Math.max(1.4, r * 0.18) },
      { t: 'path', d: M(x, y - r * 0.7) + 'C' + (x + r * 0.9) + ',' + (y - r * 1.25) + ' ' + (x + r * 1.35) + ',' + (y + r * 0.2) + ' ' + (x + r * 0.5) + ',' + (y + r * 0.95) + 'Q' + x + ',' + (y + r * 1.12) + ' ' + (x - r * 0.5) + ',' + (y + r * 0.95) + 'C' + (x - r * 1.35) + ',' + (y + r * 0.2) + ' ' + (x - r * 0.9) + ',' + (y - r * 1.25) + ' ' + x + ',' + (y - r * 0.7) + 'Z', c: c, w: Math.max(1.8, r * 0.26), fill: o.fill || COL.ground },
      { t: 'path', d: M(x + r * 0.15, y - r * 0.98) + 'q' + r * 0.45 + ',' + -r * 0.42 + ' ' + r * 0.85 + ',' + -r * 0.08 + 'q' + -r * 0.42 + ',' + r * 0.32 + ' ' + -r * 0.85 + ',' + r * 0.08 + 'Z', c: c, w: Math.max(1, r * 0.12), fill: COL.leaf }
    ], o);
  }

  function book(o) {
    var x = o.x, y = o.y, s = o.s || 1, c = o.c || COL.ink, k = o.open || 0, out = [];
    if (k < 0.5) {
      var w = 9 * s * (1 - 1.6 * k);
      out.push({ t: 'path', d: M(x - w, y) + 'V' + (y - 13 * s) + 'H' + (x + w) + 'V' + y + 'Z', c: c, w: 2.4, fill: o.fill || COL.book });
      out.push({ t: 'path', d: M(x - w + 2.5 * s, y - 13 * s) + 'V' + y, c: c, w: 1.6 });
    } else {
      var sp = (k - 0.5) * 2, pw = 11 * s * sp;
      out.push({ t: 'path', d: M(x, y - 1 * s) + L(x - pw, y - 3 * s) + 'V' + (y - 14 * s) + L(x, y - 12 * s) + 'Z' + M(x, y - 1 * s) + L(x + pw, y - 3 * s) + 'V' + (y - 14 * s) + L(x, y - 12 * s) + 'Z', c: c, w: 2.2, fill: COL.card });
      if (sp > 0.6) [5, 8, 11].forEach(function (ly) { out.push({ t: 'path', d: M(x - pw + 2 * s, y - ly * s - 1 * s) + 'h' + (pw - 4 * s) + M(x + 2 * s, y - ly * s - 1 * s) + 'h' + (pw - 4 * s), c: c, w: 1, op: 0.6 }); });
    }
    return wrap(out, o);
  }

  function glass(o) {
    var x = o.x, y = o.y, s = o.s || 1, c = o.c || COL.ink, h = 26 * s, lv = o.level == null ? 0 : o.level, t = o.t || 0, out = [];
    if (lv > 0) {
      var yl = y - h * lv, hw = 6 * s + 2.5 * s * lv;
      out.push({ t: 'path', d: M(x - 6 * s, y) + L(x + 6 * s, y) + L(x + hw, yl) + L(x - hw, yl) + 'Z', fill: o.liquid || COL.water, op: 0.9 });
      if (o.ice) [[-3, 0.25], [2.4, 0.42]].forEach(function (q) { var iy = yl + h * q[1] * 0.4; out.push({ t: 'path', d: M(x + q[0] * s - 2.2 * s, iy) + 'h' + 4.4 * s + 'v' + 4.4 * s + 'h' + -4.4 * s + 'Z', c: COL.card, w: 1.4, fill: COL.cold, op: 0.95 }); });
    }
    out.push({ t: 'path', d: M(x - 8.5 * s, y - h) + L(x - 6 * s, y) + L(x + 6 * s, y) + L(x + 8.5 * s, y - h), c: o.line || c, w: 2.6 });
    if (o.steam) for (var i = 0; i < 3; i++) {
      var ph = ((t / 1100) + i / 3) % 1, sx = x - 5 * s + i * 5 * s, sy = y - h - 3 * s - ph * 12 * s;
      out.push({ t: 'path', d: M(sx, sy) + 'q' + 2.6 * s + ',' + -3 * s + ' 0,' + -6 * s + 'q' + -2.6 * s + ',' + -3 * s + ' 0,' + -6 * s, c: COL.hot, w: 2, op: Math.sin(Math.PI * ph) * (o.steam === true ? 1 : o.steam) });
    }
    if (o.frost) [[-14, 8], [14, 16], [-12, 22]].forEach(function (q, i) { out.push(flake(x + q[0] * s, y - h + q[1] * s, 3.2 * s, (t / 900 + i) % 1, o.frost === true ? 1 : o.frost)); });
    return wrap(out, o);
  }
  function flake(x, y, r, ph, op) {
    var d = '';
    for (var a = 0; a < 3; a++) { var an = a * 60 * DEG + ph * 0.6; d += M(x - r * Math.cos(an), y - r * Math.sin(an)) + L(x + r * Math.cos(an), y + r * Math.sin(an)); }
    return { t: 'path', d: d, c: COL.cold, w: 1.6, op: op * (0.55 + 0.45 * Math.sin(ph * Math.PI * 2)) };
  }
  function bottle(o) {
    var x = o.x, y = o.y, s = o.s || 1, c = o.c || COL.ink;
    return wrap([{ t: 'path', d: M(x - 3.5 * s, y - 30 * s) + 'V' + (y - 25 * s) + 'Q' + (x - 7 * s) + ',' + (y - 22 * s) + ' ' + (x - 7 * s) + ',' + (y - 17 * s) + 'V' + y + 'H' + (x + 7 * s) + 'V' + (y - 17 * s) + 'Q' + (x + 7 * s) + ',' + (y - 22 * s) + ' ' + (x + 3.5 * s) + ',' + (y - 25 * s) + 'V' + (y - 30 * s) + 'Z', c: c, w: 2.4, fill: COL.milk },
      { t: 'path', d: M(x - 4 * s, y - 31 * s) + 'h' + 8 * s, c: c, w: 3 }], o);
  }
  function bucket(o) {
    var x = o.x, y = o.y, s = o.s || 1, c = o.c || COL.ink, lv = o.level || 0, out = [], h = 16 * s;
    out.push({ t: 'path', d: M(x - 11 * s, y - h) + 'Q' + x + ',' + (y - h - 13 * s) + ' ' + (x + 11 * s) + ',' + (y - h), c: c, w: 1.8 });
    if (lv > 0) { var yl = y - h * lv, hw = 8 * s + 3 * s * lv; out.push({ t: 'path', d: M(x - 8 * s, y) + L(x + 8 * s, y) + L(x + hw, yl) + L(x - hw, yl) + 'Z', fill: COL.milk }); }
    out.push({ t: 'path', d: M(x - 11 * s, y - h) + L(x - 8 * s, y) + L(x + 8 * s, y) + L(x + 11 * s, y - h), c: c, w: 2.6 });
    return wrap(out, o);
  }
  function thing(o) { // an object nobody can name: a box with a crank and a spring
    var x = o.x, y = o.y || G, s = o.s || 1, c = o.c || COL.ink, a = o.tilt || 0;
    return [{ t: 'group', op: o.op == null ? 1 : o.op, transform: 'rotate(' + a + ',' + x + ',' + y + ')', prims: [
      { t: 'path', d: M(x - 11 * s, y) + 'V' + (y - 18 * s) + 'H' + (x + 9 * s) + 'V' + y + 'Z', c: c, w: 2.8, fill: COL.ground },
      { t: 'path', d: M(x - 11 * s, y - 18 * s) + L(x - 6 * s, y - 23 * s) + 'H' + (x + 14 * s) + L(x + 9 * s, y - 18 * s) + M(x + 14 * s, y - 23 * s) + 'V' + (y - 5 * s) + L(x + 9 * s, y), c: c, w: 2.4, fill: COL.ground },
      { t: 'path', d: M(x - 1 * s, y - 9 * s) + 'h' + -5 * s + 'v' + 3 * s, c: c, w: 2 },
      { t: 'circle', x: x - 1 * s, y: y - 9 * s, r: 2.2 * s, c: c, w: 1.8, fill: COL.marker },
      { t: 'path', d: M(x + 3 * s, y - 23 * s) + 'q' + 3 * s + ',' + -2 * s + ' 0,' + -4 * s + 'q' + -3 * s + ',' + -2 * s + ' 0,' + -4 * s + 'q' + 3 * s + ',' + -2 * s + ' 0,' + -4 * s, c: c, w: 1.8 },
      { t: 'circle', x: x + 3 * s, y: y - 36 * s, r: 2.4 * s, fill: COL.red }
    ] }];
  }
  function qmark(x, y, op, size) { return { t: 'text', x: x, y: y, text: '?', size: size || 20, weight: 700, fill: COL.acc, op: op == null ? 1 : op }; }
  // a thought cloud above a head, with something drawn inside it
  function thought(head, r, cx, cy, inner, op) {
    var out = [{ t: 'circle', x: head[0] + (cx - head[0]) * 0.22, y: head[1] - r - 3, r: 1.8, c: COL.ink, w: 1.4, fill: COL.card, op: op },
      { t: 'circle', x: head[0] + (cx - head[0]) * 0.45, y: head[1] - r - 8, r: 2.8, c: COL.ink, w: 1.4, fill: COL.card, op: op },
      { t: 'path', d: M(cx - 16, cy + 6) + 'q-6,-1 -5,-7 q0,-7 8,-7 q3,-7 11,-5 q6,-5 12,1 q8,0 7,8 q2,8 -6,9 q-3,5 -10,3 q-6,4 -11,0 q-7,2 -6,-2Z', c: COL.ink, w: 1.6, fill: COL.card, op: op }];
    return out.concat([{ t: 'group', op: op, prims: inner }]);
  }
  function wrap(prims, o) { return (o.op != null && o.op < 1) ? [{ t: 'group', op: o.op, prims: prims }] : prims; }

  // ---------- drawing ----------
  var smooth = d3.line().curve(d3.curveCatmullRom.alpha(0.5));
  function stroke(sel, c, w) {
    return sel.style('fill', 'none').style('stroke', c).style('stroke-width', w)
      .style('stroke-linecap', 'round').style('stroke-linejoin', 'round');
  }
  function drawHead(g, p) {
    var r = p.r, f = p.f, cx = p.c[0], cy = p.c[1], lk = p.look * r * 0.3;
    stroke(g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', r), p.col, 3).style('fill', COL.ground);
    [[cx + f * r * 0.12 + lk, cy - r * 0.12], [cx + f * r * 0.52 + lk, cy - r * 0.12]].forEach(function (q) {
      g.append('circle').attr('cx', q[0]).attr('cy', q[1]).attr('r', 1.45).style('fill', p.col);
    });
    stroke(g.append('path').attr('d', 'M' + (cx + f * r * 0.14 + lk) + ',' + (cy + r * 0.34) + 'Q' + (cx + f * r * 0.34 + lk) + ',' + (cy + r * 0.5) + ' ' + (cx + f * r * 0.56 + lk) + ',' + (cy + r * 0.3)), p.col, 1.4);
  }
  function words(textSel, text, hl) {
    var list = [].concat(hl || []);
    text.split(/(\s+)/).forEach(function (part) {
      var word = part.replace(/[.,!?]/g, '');
      var ts = textSel.append('tspan').text(part);
      if (list.indexOf(word) >= 0) ts.style('font-weight', 700).style('fill', COL.acc).style('text-decoration', 'underline');
    });
  }
  var FONT = '400 11px "Atkinson Hyperlegible", system-ui, sans-serif';
  var VW = 200; // width of the picture; films draw on a wider one (see kit.width)
  function drawBubble(g, p) {
    var h = 21, w = p.text.length * 5.8 + 18;
    var x = Math.max(4, Math.min(VW - 4 - w, p.cx - w / 2)), bottom = p.top - 7, y = bottom - h, r = 10.5;
    var tx = Math.max(x + 12, Math.min(x + w - 12, p.cx + p.f * 3)), tip = [p.cx + p.f * 1.5, p.top - 1.5];
    var d = 'M' + (x + r) + ',' + y + 'H' + (x + w - r) + 'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) + 'V' + (bottom - r) +
      'Q' + (x + w) + ',' + bottom + ' ' + (x + w - r) + ',' + bottom + 'H' + (tx + 4) + 'L' + tip[0] + ',' + tip[1] + 'L' + (tx - 4) + ',' + bottom +
      'H' + (x + r) + 'Q' + x + ',' + bottom + ' ' + x + ',' + (bottom - r) + 'V' + (y + r) + 'Q' + x + ',' + y + ' ' + (x + r) + ',' + y + 'Z';
    var b = g.append('g');
    stroke(b.append('path').attr('d', d), p.col, 1.6).style('fill', COL.card);
    words(b.append('text').attr('x', x + w / 2).attr('y', y + h / 2 + 3.8).attr('text-anchor', 'middle').style('font', FONT).style('fill', COL.ink), p.text, p.hl);
  }
  function drawCaption(g, p) { // a sentence box at the top of the picture, for scenes without a speaker
    var h = 21, w = p.text.length * 5.8 + 18, x = VW / 2 - w / 2, y = 6;
    var b = g.append('g').style('opacity', p.op == null ? 1 : p.op);
    stroke(b.append('rect').attr('x', x).attr('y', y).attr('width', w).attr('height', h).attr('rx', 10.5), COL.ink, 1.6).style('fill', COL.card);
    words(b.append('text').attr('x', VW / 2).attr('y', y + h / 2 + 3.8).attr('text-anchor', 'middle').style('font', FONT).style('fill', COL.ink), p.text, p.hl);
  }
  function draw(g, prims, late) {
    prims.forEach(function (p) {
      if (!p) return;
      if (Array.isArray(p)) { draw(g, p, late); return; }
      var op = p.op == null ? 1 : p.op;
      if (p.t === 'bubble' || p.t === 'caption') { late.push(p); return; }
      if (op <= 0.001) return;
      if (p.t === 'chain') stroke(g.append('path').attr('d', smooth(p.pts)), p.c, p.w || 3.2);
      else if (p.t === 'head') drawHead(g, p);
      else if (p.t === 'path') {
        var e = g.append('path').attr('d', p.d).style('fill', p.fill || 'none').style('opacity', op);
        if (p.c) stroke(e, p.c, p.w || 2.6).style('fill', p.fill || 'none');
        if (p.dash) e.style('stroke-dasharray', p.dash);
      } else if (p.t === 'circle') {
        var ci = g.append('circle').attr('cx', p.x).attr('cy', p.y).attr('r', p.r).style('fill', p.fill || 'none').style('opacity', op);
        if (p.c) stroke(ci, p.c, p.w || 2).style('fill', p.fill || 'none');
      } else if (p.t === 'spot') {
        g.append('ellipse').attr('cx', p.x).attr('cy', G + 1).attr('rx', p.rx || 23).attr('ry', 5.5).style('fill', COL.marker).style('opacity', op);
      } else if (p.t === 'text' || p.t === 'tag') {
        g.append('text').attr('x', p.x).attr('y', p.y).attr('text-anchor', p.anchor || 'middle').style('opacity', op)
          .style('font', (p.weight || 700) + ' ' + (p.size || 12) + 'px "Atkinson Hyperlegible", system-ui, sans-serif').style('fill', p.fill || COL.acc).text(p.text);
      } else if (p.t === 'group') {
        var sub = g.append('g').style('opacity', op);
        if (p.transform) sub.attr('transform', p.transform);
        draw(sub, p.prims, late);
      }
    });
  }
  function ground(g) { stroke(g.append('path').attr('d', 'M12,140.5H188'), COL.rule, 1.6); }

  // ---------- timing helpers ----------
  var ease = d3.easeCubicInOut;
  function clamp01(k) { return k < 0 ? 0 : k > 1 ? 1 : k; }
  function ramp(u, a, b) { return ease(clamp01((u - a) / (b - a))); }
  // 0 -> 1 over `rise` ms, hold, back to 0 over `rise` ms ending at `end`
  function envelope(u, start, end, rise) {
    if (u < start || u > end) return 0;
    if (u < start + rise) return ease((u - start) / rise);
    if (u > end - rise) return ease((end - u) / rise);
    return 1;
  }
  function between(u, a, b) { return u >= a && u <= b; }
  // one 4.4 s "beat": a gesture rises, a sentence is shown, the gesture falls back
  var BEAT = 4400;
  function beat(t, n) { var u = t % (BEAT * (n || 1)); return { i: Math.floor(u / BEAT), v: u % BEAT, e: envelope(u % BEAT, 200, 4000, 650), on: between(u % BEAT, 700, 3600) }; }
  function say(on, text, hl) { return on ? { text: text, hl: hl } : null; }
  function cap(on, text, hl) { return on ? { t: 'caption', text: text, hl: hl } : null; }
  var toChest = d3.interpolate(POSES.stand, POSES.chest), toPoint = d3.interpolate(POSES.stand, POSES.point);
  var toGive = d3.interpolate(POSES.stand, POSES.give), toHold = d3.interpolate(POSES.stand, POSES.hold);
  function nodding(t) { var p = JSON.parse(JSON.stringify(POSES.stand)); p.head = 14 * Math.max(0, Math.sin(t / 160)); return p; }
  function lerp(a, b, k) { return a + (b - a) * k; }
  function along(a, b, k) { return [lerp(a[0], b[0], k), lerp(a[1], b[1], k) - Math.sin(Math.PI * k) * 14]; }

  // Speaker A points at B and says something (one beat). Options: who/kind/facing for both.
  function pointAt(t, A, B, text, hl, extra) {
    var b = beat(t);
    return [{ t: 'spot', x: B.x, op: b.e, rx: B.rx }].concat(extra || [], [
      figure({ x: B.x, kind: B.kind, facing: B.facing || -1 }),
      figure({ x: A.x, kind: A.kind, facing: A.facing || 1, accent: true, pose: toPoint(b.e), say: say(b.on, text, hl) })
    ]);
  }

  // ---------- scenes: one per word, each acting out the word's teaching sentence ----------
  var SCENES = {
    // step 1
    I: {
      label: 'A man puts his hand on his chest and says: I am a man.',
      period: BEAT, rest: 2200,
      frame: function (t) { var b = beat(t); return [figure({ x: 100, accent: true, pose: toChest(b.e), say: say(b.on, 'I am a man.', 'I') })]; }
    },
    am: {
      label: 'A man puts his hand on his chest and says: I am a man. Then a woman does the same and says: I am a woman.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0;
        var M_ = { x: 60, facing: 1 }, W_ = { x: 142, facing: -1, kind: 'woman' }, sp = first ? M_ : W_, li = first ? W_ : M_;
        return [{ t: 'spot', x: sp.x, op: b.e }, figure({ x: li.x, facing: li.facing, kind: li.kind }),
          figure({ x: sp.x, facing: sp.facing, kind: sp.kind, accent: true, pose: toChest(b.e), say: say(b.on, first ? 'I am a man.' : 'I am a woman.', 'am') })];
      }
    },
    a: {
      label: 'Three men. One at a time, any one of them is picked out: a man.',
      period: 5400, rest: 900,
      frame: function (t) {
        var xs = [44, 100, 156], faces = [1, 1, -1], order = [0, 2, 1];
        var slot = Math.floor((t % this.period) / 1800), v = t % 1800, pick = order[slot], e = envelope(v, 0, 1800, 350);
        var out = [{ t: 'spot', x: xs[pick], op: e }];
        xs.forEach(function (x, i) { out.push({ t: 'group', op: i === pick ? 0.28 + 0.72 * e : 0.28, prims: figure({ x: x, facing: faces[i] }) }); });
        out.push({ t: 'tag', x: xs[pick], y: 36, text: 'a man', op: e });
        return out;
      }
    },
    man: {
      label: 'A man waves and says: I am a man. A woman stands next to him.',
      period: BEAT, rest: 2000,
      frame: function (t) {
        var b = beat(t), wv = mix(POSES.stand, waving(t), b.e);
        return [{ t: 'spot', x: 80, op: b.e }, { t: 'group', op: 0.35, prims: figure({ x: 150, kind: 'woman', facing: -1 }) },
          figure({ x: 80, accent: true, pose: wv, say: say(b.on, 'I am a man.', 'man') })];
      }
    },
    woman: {
      label: 'A woman waves and says: I am a woman. A man stands next to her.',
      period: BEAT, rest: 2000,
      frame: function (t) {
        var b = beat(t), wv = mix(POSES.stand, waving(t), b.e);
        return [{ t: 'spot', x: 120, op: b.e }, { t: 'group', op: 0.35, prims: figure({ x: 50, facing: 1 }) },
          figure({ x: 120, kind: 'woman', facing: -1, accent: true, pose: wv, say: say(b.on, 'I am a woman.', 'woman') })];
      }
    },
    // step 2
    you: {
      label: 'Two men. One points at the other and says: You are a man. Then the other man points back and says the same.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0, A = { x: 56, facing: 1 }, B = { x: 146, facing: -1 }, sp = first ? A : B, li = first ? B : A;
        return [{ t: 'spot', x: li.x, op: b.e }, figure({ x: li.x, facing: li.facing }),
          figure({ x: sp.x, facing: sp.facing, accent: true, pose: toPoint(b.e), say: say(b.on, 'You are a man.', 'You') })];
      }
    },
    are: {
      label: 'A man points at a woman and says: You are a woman. Then she points at him and says: You are a man.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0, A = { x: 56, facing: 1 }, B = { x: 146, facing: -1, kind: 'woman' }, sp = first ? A : B, li = first ? B : A;
        return [{ t: 'spot', x: li.x, op: b.e }, figure({ x: li.x, facing: li.facing, kind: li.kind }),
          figure({ x: sp.x, facing: sp.facing, kind: sp.kind, accent: true, pose: toPoint(b.e), say: say(b.on, first ? 'You are a woman.' : 'You are a man.', 'are') })];
      }
    },
    he: {
      label: 'A woman points at a man and says: He is a man.',
      period: BEAT, rest: 2200,
      frame: function (t) { return pointAt(t, { x: 50, kind: 'woman' }, { x: 148 }, 'He is a man.', 'He'); }
    },
    she: {
      label: 'A man points at a woman and says: She is a woman.',
      period: BEAT, rest: 2200,
      frame: function (t) { return pointAt(t, { x: 50 }, { x: 148, kind: 'woman' }, 'She is a woman.', 'She'); }
    },
    is: {
      label: 'A person in the middle points at a man and says: He is a man. Then at a woman: She is a woman.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0;
        return [{ t: 'spot', x: first ? 160 : 40, op: b.e }, figure({ x: 160, facing: -1 }), figure({ x: 40, kind: 'woman', facing: 1 }),
          figure({ x: 100, kind: 'woman', facing: first ? 1 : -1, accent: true, pose: toPoint(b.e), say: say(b.on, first ? 'He is a man.' : 'She is a woman.', 'is') })];
      }
    },
    // step 3
    boy: {
      label: 'A man points at a boy and says: He is a boy. The boy waves.',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 140, op: b.e, rx: 18 }, figure({ x: 140, kind: 'boy', facing: -1, pose: mix(POSES.stand, waving(t), b.e) }),
          figure({ x: 52, accent: true, pose: toPoint(b.e), say: say(b.on, 'He is a boy.', 'boy') })];
      }
    },
    girl: {
      label: 'A woman points at a girl and says: She is a girl. The girl waves.',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 140, op: b.e, rx: 18 }, figure({ x: 140, kind: 'girl', facing: -1, pose: mix(POSES.stand, waving(t), b.e) }),
          figure({ x: 52, kind: 'woman', accent: true, pose: toPoint(b.e), say: say(b.on, 'She is a girl.', 'girl') })];
      }
    },
    child: {
      label: 'A woman points at a small girl: She is a child. Then at a small boy: He is a child.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0;
        return [{ t: 'spot', x: first ? 120 : 165, op: b.e, rx: 17 }, figure({ x: 120, kind: 'girl', facing: -1 }), figure({ x: 165, kind: 'boy', facing: -1 }),
          figure({ x: 48, kind: 'woman', accent: true, pose: toPoint(b.e), say: say(b.on, first ? 'She is a child.' : 'He is a child.', 'child') })];
      }
    },
    'this': {
      label: 'A man puts his hand on a boy who is near him and says: This is a boy. A girl stands far away.',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t), near = mix(POSES.stand, pose([-26, -14, 60, 120]), b.e);
        return [{ t: 'spot', x: 100, op: b.e, rx: 17 }, { t: 'group', op: 0.35, prims: figure({ x: 172, kind: 'girl', facing: -1 }) },
          figure({ x: 100, kind: 'boy', facing: -1 }), figure({ x: 72, accent: true, pose: near, say: say(b.on, 'This is a boy.', 'This') })];
      }
    },
    that: {
      label: 'A man points at a girl who is far away and says: That is a girl. A boy stands near him.',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 168, op: b.e, rx: 17 }, { t: 'group', op: 0.35, prims: figure({ x: 82, kind: 'boy', facing: -1 }) },
          figure({ x: 168, kind: 'girl', facing: -1 }), figure({ x: 46, accent: true, pose: toPoint(b.e), say: say(b.on, 'That is a girl.', 'That') })];
      }
    },
    // step 4
    house: {
      label: 'A house appears. A man points at it and says: This is a house.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t), grow = ramp(b.v, 0, 700);
        return [{ t: 'spot', x: 135, op: b.e, rx: 36 }, house({ x: 135, s: 0.6 + 0.4 * grow, op: grow }),
          figure({ x: 46, accent: true, pose: toPoint(b.e), say: say(b.on, 'This is a house.', 'house') })];
      }
    },
    dog: {
      label: 'A big dog wags its tail. A man points at it and says: That is a big dog.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 140, op: b.e, rx: 30 }, dog({ x: 140, s: 1.35, f: -1, t: t }),
          figure({ x: 46, accent: true, pose: toPoint(b.e), say: say(b.on, 'That is a big dog.', 'dog') })];
      }
    },
    cat: {
      label: 'A cat moves its tail. A woman points at it and says: This is a cat.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 130, op: b.e, rx: 22 }, cat({ x: 130, s: 1.25, f: -1, t: t }),
          figure({ x: 50, kind: 'woman', accent: true, pose: toPoint(b.e), say: say(b.on, 'This is a cat.', 'cat') })];
      }
    },
    it: {
      label: 'A man points at a dog and says: It is a dog. Then at a cat: It is a cat.',
      period: 2 * BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0, show = ramp(b.v, 0, 500);
        var animal = first ? dog({ x: 140, s: 1.2, f: -1, t: t, op: show }) : cat({ x: 140, s: 1.3, f: -1, t: t, op: show });
        return [{ t: 'spot', x: 140, op: b.e, rx: 26 }, animal,
          figure({ x: 48, accent: true, pose: toPoint(b.e), say: say(b.on, first ? 'It is a dog.' : 'It is a cat.', 'It') })];
      }
    },
    big: {
      label: 'A small house and a house that grows big. The big house is marked: It is a big house.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), g = ramp(b.v, 200, 1400);
        return [{ t: 'spot', x: 135, op: b.e, rx: 44 }, house({ x: 52, s: 0.62, op: 0.45 }), house({ x: 135, s: 0.62 + 0.6 * g, c: COL.acc }),
          cap(b.on, 'It is a big house.', 'big')];
      }
    },
    // step 5
    the: {
      label: 'A man points at the dog: The dog is big. Then at the cat: The cat is small.',
      period: 2 * BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0;
        return [{ t: 'spot', x: first ? 112 : 168, op: b.e, rx: first ? 28 : 18 }, dog({ x: 112, s: 1.35, f: -1, t: t }), cat({ x: 168, s: 0.9, f: -1, t: t }),
          figure({ x: 42, accent: true, pose: toPoint(b.e), say: say(b.on, first ? 'The dog is big.' : 'The cat is small.', 'The') })];
      }
    },
    small: {
      label: 'A small cat next to a big dog. The cat is marked: The cat is small.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t), sh = 1 - 0.25 * ramp(b.v, 200, 1200);
        return [{ t: 'spot', x: 70, op: b.e, rx: 20 }, dog({ x: 140, s: 1.45, f: -1, t: t, op: 0.45 }), cat({ x: 70, s: 1.2 * sh, f: 1, t: t, c: COL.acc }),
          cap(b.on, 'The cat is small.', 'small')];
      }
    },
    we: {
      label: 'A boy and a girl put their hands on their chests and say: We are children.',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 100, op: b.e, rx: 40 }, figure({ x: 118, kind: 'girl', facing: -1, accent: true, pose: toChest(b.e) }),
          figure({ x: 82, kind: 'boy', facing: 1, accent: true, pose: toChest(b.e), say: say(b.on, 'We are children.', 'We') })];
      }
    },
    they: {
      label: 'A man points at two boys and says: They are boys.',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 145, op: b.e, rx: 38 }, figure({ x: 128, kind: 'boy', facing: -1 }), figure({ x: 162, kind: 'boy', facing: -1 }),
          figure({ x: 48, accent: true, pose: toPoint(b.e), say: say(b.on, 'They are boys.', 'They') })];
      }
    },
    and: {
      label: 'A small dog comes, then a small cat comes: The dog and the cat are small.',
      period: BEAT * 1.25, rest: 3600,
      frame: function (t) {
        var u = t % this.period, d1 = ramp(u, 0, 600), c1 = ramp(u, 1300, 1900), on = between(u, 1900, 5000), all = envelope(u, 0, 5300, 500);
        return [{ t: 'spot', x: 62, op: d1 * all, rx: 24 }, { t: 'spot', x: 140, op: c1 * all, rx: 20 },
          dog({ x: 62, s: 0.95, f: 1, t: t, op: d1 }), cat({ x: 140, s: 1.05, f: -1, t: t, op: c1 }),
          { t: 'text', x: 101, y: 122, text: '+', size: 18, op: c1 * all },
          cap(on, 'The dog and the cat are small.', 'and')];
      }
    },
    // step 6
    have: {
      label: 'A man puts his hand on his chest by his big house: I have a big house. Then he holds a dog on a lead: I have a dog.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0;
        if (first) return [{ t: 'spot', x: 138, op: b.e, rx: 40 }, house({ x: 138, s: 1.05 }), figure({ x: 52, accent: true, pose: toChest(b.e), say: say(b.on, 'I have a big house.', 'have') })];
        var m = figure({ x: 60, accent: true, pose: toHold(b.e), say: say(b.on, 'I have a dog.', 'have') });
        var d = dog({ x: 128, s: 1, f: -1, t: t });
        return [{ t: 'spot', x: 128, op: b.e, rx: 24 }, d, { t: 'path', d: M(m.hand[0], m.hand[1]) + 'Q' + (m.hand[0] + 25) + ',' + (G - 10) + ' ' + 111 + ',' + (G - 23), c: COL.acc, w: 1.6, op: b.e }, m];
      }
    },
    not: {
      label: 'A big dog fades away and a small dog is left: The dog is not big.',
      period: BEAT, rest: 3000,
      frame: function (t) {
        var b = beat(t), shrink = ramp(b.v, 300, 1400);
        return [{ t: 'spot', x: 110, op: b.e, rx: 22 }, dog({ x: 110, s: 1.6, f: -1, t: t, op: 0.35 * (1 - shrink), c: COL.ink }),
          dog({ x: 110, s: 1.6 - 0.75 * shrink, f: -1, t: t, c: COL.acc }), cap(b.on, 'The dog is not big.', 'not')];
      }
    },
    yes: {
      label: 'A woman points at a cat and asks: Is it a cat? A man nods: Yes, it is a cat.',
      period: 2 * BEAT, rest: 5400,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0;
        return [{ t: 'spot', x: 160, op: first ? b.e : 1, rx: 20 }, cat({ x: 160, s: 1.1, f: -1, t: t }),
          figure({ x: 38, kind: 'woman', accent: first, pose: toPoint(first ? b.e : 0), say: say(first && b.on, 'Is it a cat?', null) }),
          figure({ x: 96, accent: !first, pose: first ? POSES.stand : nodding(b.v), say: say(!first && b.on, 'Yes, it is a cat.', 'Yes') })];
      }
    },
    no: {
      label: 'A woman points at a cat and asks: Is it a dog? A man shakes his head: No, it is not a dog.',
      period: 2 * BEAT, rest: 5400,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0, shake = first ? 0 : Math.sin(b.v / 120) * envelope(b.v, 200, 2400, 300);
        return [{ t: 'spot', x: 160, op: first ? b.e : 1, rx: 20 }, cat({ x: 160, s: 1.1, f: -1, t: t }),
          figure({ x: 38, kind: 'woman', accent: first, pose: toPoint(first ? b.e : 0), say: say(first && b.on, 'Is it a dog?', null) }),
          figure({ x: 96, accent: !first, look: shake, dx: shake * 1.2, say: say(!first && b.on, 'No, it is not a dog.', 'No') })];
      }
    },
    what: {
      label: 'A man points at a strange box and asks: What is this? Then he points at a cat and asks: What is that? It is a cat.',
      period: 2 * BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0, wob = first ? 4 * Math.sin(t / 180) * b.e : 0;
        var out = [{ t: 'spot', x: 140, op: b.e, rx: 22 }];
        if (first) out.push(thing({ x: 140, s: 1.5, tilt: wob }), qmark(140, 72, b.e));
        else out.push(cat({ x: 140, s: 1.2, f: -1, t: t }), qmark(140, 96, b.on && b.v < 2200 ? 1 : 0));
        out.push(figure({ x: 48, accent: true, pose: toPoint(b.e), say: say(b.on, first ? 'What is this?' : (b.v < 2200 ? 'What is that?' : 'It is a cat.'), 'What') }));
        return out;
      }
    },
    // step 7
    to: {
      label: 'A woman holds out her hand and says: Give the apple to me. A man gives her the apple.',
      period: BEAT * 1.4, rest: 3000,
      frame: function (t) {
        var u = t % this.period, ask = envelope(u, 100, 5800, 500), move = ramp(u, 2200, 3600);
        var w = figure({ x: 48, kind: 'woman', accent: true, pose: toGive(ask), say: say(between(u, 500, 5400), 'Give the apple to me.', 'to') });
        var m = figure({ x: 150, facing: -1, pose: toGive(envelope(u, 1200, 4000, 600)) });
        var a = along([m.hand[0], m.hand[1] - 4], [w.hand[0] + 3, w.hand[1] - 4], move);
        return [{ t: 'spot', x: 48, op: move * ask }, m, w, { t: 'path', d: M(m.hand[0] - 6, m.hand[1] - 16) + 'Q100,' + (m.hand[1] - 34) + ' ' + (w.hand[0] + 10) + ',' + (w.hand[1] - 16), c: COL.acc, w: 1.6, dash: '3 4', op: envelope(u, 1800, 3800, 300) },
          apple({ x: a[0], y: a[1], r: 5.5, fill: COL.red })];
      }
    },
    give: {
      label: 'A man holds out his hand and says: Give me the book. A woman gives him the book.',
      period: BEAT * 1.4, rest: 3000,
      frame: function (t) {
        var u = t % this.period, ask = envelope(u, 100, 5800, 500), move = ramp(u, 2200, 3600);
        var m = figure({ x: 48, accent: true, pose: toGive(ask), say: say(between(u, 500, 5400), 'Give me the book.', 'Give') });
        var w = figure({ x: 150, kind: 'woman', facing: -1, pose: toGive(envelope(u, 1000, 4000, 600)) });
        var a = along([w.hand[0], w.hand[1] + 2], [m.hand[0] + 3, m.hand[1] + 2], move);
        return [{ t: 'spot', x: 150, op: envelope(u, 1000, 3000, 400) }, w, m, book({ x: a[0], y: a[1], s: 0.9 })];
      }
    },
    book: {
      label: 'A man holds a book and opens it: I have a book.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t), m = figure({ x: 72, accent: true, pose: toHold(b.e), say: say(b.on, 'I have a book.', 'book') });
        var k = ramp(b.v, 800, 1600) * (1 - ramp(b.v, 3300, 4000));
        return [{ t: 'spot', x: 72, op: b.e }, m, book({ x: lerp(130, m.hand[0] + 10, b.e), y: lerp(G, m.hand[1] + 6, b.e), s: 1.2, open: k })];
      }
    },
    red: {
      label: 'An apple turns red: The apple is red.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), k = ramp(b.v, 300, 1300);
        return [{ t: 'spot', x: 100, op: b.e, rx: 24 }, apple({ x: 100, y: 104, r: 22 }), apple({ x: 100, y: 104, r: 22, fill: COL.red, op: k }),
          cap(b.on, 'The apple is red.', 'red')];
      }
    },
    apple: {
      label: 'A man holds up an apple: This apple is red.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t), m = figure({ x: 82, accent: true, pose: toGive(b.e), say: say(b.on, 'This apple is red.', 'apple') });
        return [{ t: 'spot', x: 82, op: b.e }, m, apple({ x: m.hand[0] + 3, y: m.hand[1] - 6, r: 6 + 2 * b.e, fill: COL.red })];
      }
    },
    // step 8
    of: {
      label: 'The door of a house turns red: The door of the house is red.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), k = ramp(b.v, 300, 1200), h = house({ x: 100, s: 1.25, doorFill: k > 0.5 ? COL.red : COL.ground });
        return [{ t: 'spot', x: h.door[0], op: b.e, rx: 16 }, h, cap(b.on, 'The door of the house is red.', 'of')];
      }
    },
    'in': {
      label: 'A cat walks to a house and goes in. It looks out of the window: The cat is in the house.',
      period: 6400, rest: 5200,
      frame: function (t) {
        var u = t % this.period, walk = ramp(u, 0, 2400), door = envelope(u, 1600, 3600, 400), inside = ramp(u, 2700, 3300);
        var cx = lerp(18, 112, walk), catOp = 1 - ramp(u, 2300, 2700);
        return [{ t: 'spot', x: 130, op: inside * envelope(u, 0, 6300, 400), rx: 34 },
          house({ x: 130, s: 1.15, door: door, windowCat: inside }), cat({ x: cx, s: 0.95, f: 1, t: t, op: catOp }),
          cap(between(u, 3300, 6200), 'The cat is in the house.', 'in')];
      }
    },
    thing: {
      label: 'A man points at a strange thing that shakes and asks: What is that thing?',
      period: BEAT, rest: 2200,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 148, op: b.e, rx: 24 }, thing({ x: 148, s: 1.5, tilt: 5 * Math.sin(t / 160) }), qmark(170, 72, b.e, 18),
          figure({ x: 46, accent: true, pose: toPoint(b.e), say: say(b.on, 'What is that thing?', 'thing') })];
      }
    },
    open: {
      label: 'The door of a house opens: The door is open.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), k = ramp(b.v, 200, 1300) * (1 - ramp(b.v, 3700, 4300)), h = house({ x: 100, s: 1.25, door: k });
        return [{ t: 'spot', x: h.door[0], op: k, rx: 16 }, h, cap(b.on && k > 0.9, 'The door is open.', 'open')];
      }
    },
    door: {
      label: 'A man points at the door of a house and says: Open the door. The door opens.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), k = ramp(b.v, 1800, 2800) * (1 - ramp(b.v, 3800, 4300));
        var h = house({ x: 140, s: 1.15, door: k, doorLine: b.e > 0.5 ? COL.acc : null });
        return [{ t: 'spot', x: h.door[0], op: b.e, rx: 14 }, h, figure({ x: 46, accent: true, pose: toPoint(b.e), say: say(b.on, 'Open the door.', 'door') })];
      }
    },
    // step 9
    or: {
      label: 'A glass of water. A hot glass and a cold glass are marked one after the other: Is it hot or cold?',
      period: BEAT * 1.25, rest: 2000,
      frame: function (t) {
        var u = t % this.period, all = envelope(u, 0, 5300, 400), hot = envelope(u, 600, 2700, 300), cold = envelope(u, 2800, 4900, 300);
        return [{ t: 'spot', x: 45, op: hot * all, rx: 18 }, { t: 'spot', x: 155, op: cold * all, rx: 18 },
          glass({ x: 45, y: G, s: 1, level: 0.7, liquid: COL.hot, steam: 0.4 + 0.6 * hot, t: t, op: 0.45 + 0.55 * hot }),
          glass({ x: 155, y: G, s: 1, level: 0.7, liquid: COL.cold, ice: true, frost: 0.4 + 0.6 * cold, t: t, op: 0.45 + 0.55 * cold }),
          glass({ x: 100, y: G, s: 1.3, level: 0.7, t: t }), qmark(100, 92, all), cap(between(u, 300, 5100), 'Is it hot or cold?', 'or')];
      }
    },
    'do': {
      label: 'A man points at a woman and asks: What do you do? She opens a book and reads.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t), w = figure({ x: 145, kind: 'woman', facing: -1, pose: toHold(ramp(b.v, 1500, 2100) * (1 - ramp(b.v, 3900, 4300))) });
        var k = ramp(b.v, 2100, 2700) * (1 - ramp(b.v, 3700, 4100));
        return [{ t: 'spot', x: 145, op: b.e }, w, book({ x: w.hand[0] - 9, y: w.hand[1] + 6, s: 1, open: k, op: ramp(b.v, 1500, 1900) * (1 - ramp(b.v, 3900, 4300)) }),
          figure({ x: 48, accent: true, pose: toPoint(b.e), say: say(b.on, 'What do you do?', 'do') })];
      }
    },
    water: {
      label: 'Water goes into a glass. There is ice in it: The water is cold.',
      period: BEAT, rest: 3200,
      frame: function (t) {
        var b = beat(t), lv = ramp(b.v, 200, 1800), pour = envelope(b.v, 200, 1900, 200);
        return [{ t: 'spot', x: 100, op: b.e, rx: 22 },
          { t: 'path', d: M(100, 50) + 'V' + (G - 34 * lv), c: COL.water, w: 4, op: pour },
          glass({ x: 100, y: G, s: 1.5, level: 0.8 * lv, ice: lv > 0.6, t: t, line: COL.acc }), cap(b.on, 'The water is cold.', 'water')];
      }
    },
    hot: {
      label: 'A man touches a glass of hot water and pulls his hand back: The water is hot.',
      period: BEAT, rest: 2000,
      frame: function (t) {
        var b = beat(t), reach = envelope(b.v, 300, 1700, 500), back = ramp(b.v, 1600, 1900) * (1 - ramp(b.v, 3800, 4300));
        var ps = back > 0 ? mix(POSES.point, POSES.pull, back) : toPoint(reach);
        return [{ t: 'spot', x: 118, op: b.e, rx: 18 }, glass({ x: 118, y: G, s: 1.4, level: 0.75, liquid: COL.hot, steam: true, t: t, line: COL.hot }),
          figure({ x: 72, accent: true, pose: ps, dx: back * 3 * Math.sin(t / 40) * (1 - ramp(b.v, 2200, 2600)) }), cap(b.on, 'The water is hot.', 'hot')];
      }
    },
    cold: {
      label: 'A man drinks cold water and shakes with cold: The water is cold.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), shiver = envelope(b.v, 1400, 3800, 300), m = figure({ x: 80, accent: true, pose: toGive(b.e), dx: shiver * 1.4 * Math.sin(t / 30) });
        return [{ t: 'spot', x: 80, op: b.e }, m, glass({ x: m.hand[0] + 4, y: m.hand[1] + 8, s: 0.9, level: 0.7, ice: true, frost: true, t: t, line: COL.cold }),
          cap(b.on, 'The water is cold.', 'cold')];
      }
    },
    // step 10
    some: {
      label: 'A man says: I want some water. Some water goes into his glass, but not all.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), lv = ramp(b.v, 1200, 2200), pour = envelope(b.v, 1200, 2300, 200);
        return [{ t: 'spot', x: 130, op: b.e, rx: 18 }, { t: 'path', d: M(130, 66) + 'V' + (G - 20 * lv), c: COL.water, w: 3, op: pour },
          glass({ x: 130, y: G, s: 1.3, level: 0.4 * lv, t: t }), figure({ x: 52, accent: true, pose: toPoint(b.e * 0.6), say: say(b.on, 'I want some water.', 'some') })];
      }
    },
    also: {
      label: 'A man says: I want some water. A glass of water comes. Then he says: I also want some milk. Milk comes too.',
      period: 2 * BEAT, rest: 6000,
      frame: function (t) {
        var b = beat(t, 2), first = b.i === 0, wIn = first ? ramp(b.v, 900, 1500) : 1, mIn = first ? 0 : ramp(b.v, 900, 1500);
        return [{ t: 'spot', x: 118, op: wIn * (first ? b.e : 1), rx: 16 }, { t: 'spot', x: 158, op: mIn * b.e, rx: 16 },
          glass({ x: 118, y: G, s: 1.1, level: 0.7, t: t, op: wIn }), bottle({ x: 158, y: G, s: 1.1, op: mIn }),
          figure({ x: 50, accent: true, pose: toChest(b.e * 0.8), say: say(b.on, first ? 'I want some water.' : 'I also want some milk.', first ? 'want' : 'also') })];
      }
    },
    want: {
      label: 'A man thinks of a glass of water and reaches for it: I want some water.',
      period: BEAT, rest: 2600,
      frame: function (t) {
        var b = beat(t), m = figure({ x: 58, accent: true, pose: toPoint(b.e * 0.85), look: 0.6 });
        return [{ t: 'spot', x: 140, op: b.e, rx: 18 }, glass({ x: 140, y: G, s: 1.2, level: 0.7, t: t }),
          thought(m.head, m.r, 104, 52, glass({ x: 104, y: 60, s: 0.55, level: 0.7 }), ramp(b.v, 300, 900) * (1 - ramp(b.v, 3800, 4300))), m,
          cap(b.on, 'I want some water.', 'want')];
      }
    },
    milk: {
      label: 'A cow and a bucket that fills with white milk: Cows give milk.',
      period: BEAT, rest: 3200,
      frame: function (t) {
        var b = beat(t), lv = ramp(b.v, 400, 2600);
        return [{ t: 'spot', x: 150, op: b.e, rx: 18 }, cow({ x: 72, s: 1.05, f: 1, t: t }), bucket({ x: 150, y: G, s: 1.2, level: 0.85 * lv, c: COL.acc }),
          cap(b.on, 'Cows give milk.', 'milk')];
      }
    },
    cow: {
      label: 'A cow moves its head and tail, with a bucket of milk: Cows give milk.',
      period: BEAT, rest: 2400,
      frame: function (t) {
        var b = beat(t);
        return [{ t: 'spot', x: 90, op: b.e, rx: 40 }, cow({ x: 90, s: 1.3, f: 1, t: t, c: COL.acc }), bucket({ x: 165, y: G, s: 0.9, level: 0.8 }),
          cap(b.on, 'Cows give milk.', 'Cows')];
      }
    }
  };

  // ---------- mounting ----------
  var live = [];
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function render(svg, scene, t) {
    svg.selectAll('g.fig').remove();
    var g = svg.append('g').attr('class', 'fig'), late = [];
    draw(g, scene.frame(t), late);
    late.forEach(function (p) { if (p.t === 'caption') drawCaption(g, p); else drawBubble(g, p); });
  }

  function mount(el) {
    var scene = SCENES[el.getAttribute('data-scene')];
    if (!scene || el.getAttribute('data-mounted')) return;
    el.setAttribute('data-mounted', '1');
    var svg = d3.select(el).append('svg').attr('viewBox', '0 0 200 150').attr('aria-hidden', 'true');
    ground(svg.append('g'));
    if (scene.still || reduceMotion) { render(svg, scene, scene.rest || 0); return; }
    var entry = { el: el, timer: d3.timer(function (ms) { render(svg, scene, ms); }) };
    render(svg, scene, 0);
    live.push(entry);
  }

  return {
    has: function (word) { return Object.prototype.hasOwnProperty.call(SCENES, word); },
    label: function (word) { return SCENES[word] ? SCENES[word].label : ''; },
    words: function () { return Object.keys(SCENES); },
    // draws one scene at time t into an element (used by tests)
    renderAt: function (el, word, t) {
      var svg = d3.select(el).append('svg').attr('viewBox', '0 0 200 150');
      ground(svg.append('g')); render(svg, SCENES[word], t);
    },
    // the drawing kit, for films.js: people, animals, things, poses and the primitive drawer
    kit: {
      G: G, COL: COL, POSES: POSES, figure: figure, dog: dog, cat: cat, cow: cow, house: house, apple: apple, book: book,
      glass: glass, bottle: bottle, bucket: bucket, thing: thing, thought: thought, walking: walking, waving: waving,
      nodding: nodding, ramp: ramp, ease: ease, draw: function (g, prims) {
        var late = [];
        draw(g, prims, late);
        late.forEach(function (p) { if (p.t === 'caption') drawCaption(g, p); else drawBubble(g, p); });
      },
      width: function (w) { VW = w || 200; }
    },
    mountAll: function (container) {
      // stop animations whose picture has left the page
      live = live.filter(function (x) { if (!x.el.isConnected) { x.timer.stop(); return false; } return true; });
      (container || document).querySelectorAll('.scene[data-scene]').forEach(mount);
    }
  };
})();
