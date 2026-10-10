// Basic 1000 teaching pictures: stick figures in the "Faces" style, drawn live with D3.
// Each figure is a skeleton of joints; a pose is a list of angles. Scenes are short
// timelines that move between poses and show who is speaking.
// Public API: BASIC_FIGURES.has(word), .label(word), .mountAll(container)
var BASIC_FIGURES = (function () {
  var d3 = window.d3;
  if (!d3) return { has: function () { return false; }, label: function () { return ''; }, mountAll: function () {} };

  // ---------- geometry ----------
  var DEG = Math.PI / 180, GROUND = 140;
  function P(o, len, a) { return [o[0] + len * Math.sin(a * DEG), o[1] + len * Math.cos(a * DEG)]; }
  var DIMS = { head: 9, neck: 3, torso: 30, upper: 15, fore: 14, thigh: 21, shin: 20 };
  var HEAD_SCALE = 1.32;
  // angles in degrees: 0 points down, 90 points forward, 180 points up
  var POSES = {
    stand: { lean: 0, head: 0, arms: [-26, -14, 26, 14], legs: [-14, -6, 14, 6] },
    chest: { lean: 0, head: 0, arms: [-26, -14, 58, -112], legs: [-14, -6, 14, 6] },
    point: { lean: 0, head: 0, arms: [-26, -14, 84, 88], legs: [-14, -6, 14, 6] }
  };

  function skeleton(pose, f) {
    var d = DIMS, up = f * (180 - pose.lean), hip = [0, 0];
    var sh = P(hip, d.torso - 3, up), neck = P(hip, d.torso, up);
    var eL = P(sh, d.upper, f * pose.arms[0]), eR = P(sh, d.upper, f * pose.arms[2]);
    var kL = P(hip, d.thigh, f * pose.legs[0]), kR = P(hip, d.thigh, f * pose.legs[2]);
    return {
      hip: hip, neck: neck, sh: sh, headDir: f * (180 - pose.lean - pose.head),
      eL: eL, hL: P(eL, d.fore, f * pose.arms[1]), eR: eR, hR: P(eR, d.fore, f * pose.arms[3]),
      kL: kL, fL: P(kL, d.shin, f * pose.legs[1]), kR: kR, fR: P(kR, d.shin, f * pose.legs[3])
    };
  }

  // A figure becomes primitives: chains (lines through points), a head, an optional speech bubble.
  function figure(o) {
    var f = o.facing || 1, k = skeleton(o.pose || POSES.stand, f);
    var dy = GROUND - Math.max(k.fL[1], k.fR[1]);
    Object.keys(k).forEach(function (key) { if (Array.isArray(k[key])) k[key] = [k[key][0] + o.x, k[key][1] + dy]; });
    var r = DIMS.head * HEAD_SCALE, hc = P(k.neck, DIMS.neck + r, k.headDir), neckEnd = P(k.neck, DIMS.neck, k.headDir);
    var c = o.accent ? 'var(--tab)' : 'var(--ink)';
    var out = [];
    // women wear their hair in a bun at the back of the head (drawn first so the head covers its edge)
    if (o.kind === 'woman') out.push({ t: 'bun', c: [hc[0] - f * r * 0.62, hc[1] - r * 0.88], r: r * 0.4, col: c });
    out.push(
      { t: 'chain', pts: [k.hip, k.kL, k.fL], c: c },
      { t: 'chain', pts: [k.hip, k.kR, k.fR], c: c },
      { t: 'chain', pts: [k.hip, neckEnd], c: c },
      { t: 'chain', pts: [k.sh, k.eL, k.hL], c: c },
      { t: 'chain', pts: [k.sh, k.eR, k.hR], c: c },
      { t: 'head', c: hc, r: r, f: f, col: c }
    );
    if (o.say) out.push({ t: 'bubble', text: o.say.text, hl: o.say.hl, cx: hc[0], top: hc[1] - r, f: f, col: c, op: o.say.op == null ? 1 : o.say.op });
    return out;
  }

  // ---------- drawing (style E: rounded 3 px line, big head, dot eyes) ----------
  var smooth = d3.line().curve(d3.curveCatmullRom.alpha(0.5));
  function stroke(sel, c, w) {
    return sel.style('fill', 'none').style('stroke', c).style('stroke-width', w)
      .style('stroke-linecap', 'round').style('stroke-linejoin', 'round');
  }
  function drawHead(g, p) {
    var r = p.r, f = p.f, cx = p.c[0], cy = p.c[1];
    stroke(g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', r), p.col, 3).style('fill', 'var(--fig-ground)');
    [[cx + f * r * 0.12, cy - r * 0.12], [cx + f * r * 0.52, cy - r * 0.12]].forEach(function (q) {
      g.append('circle').attr('cx', q[0]).attr('cy', q[1]).attr('r', 1.45).style('fill', p.col);
    });
    stroke(g.append('path').attr('d', 'M' + (cx + f * r * 0.14) + ',' + (cy + r * 0.34) + 'Q' + (cx + f * r * 0.34) + ',' + (cy + r * 0.5) + ' ' + (cx + f * r * 0.56) + ',' + (cy + r * 0.3)), p.col, 1.4);
  }
  function drawBubble(g, p) {
    var h = 21, w = p.text.length * 5.8 + 18;
    var x = Math.max(4, Math.min(196 - w, p.cx - w / 2)), bottom = p.top - 7, y = bottom - h, r = 10.5;
    var tx = Math.max(x + 12, Math.min(x + w - 12, p.cx + p.f * 3)), tip = [p.cx + p.f * 1.5, p.top - 1.5];
    var d = 'M' + (x + r) + ',' + y + 'H' + (x + w - r) + 'Q' + (x + w) + ',' + y + ' ' + (x + w) + ',' + (y + r) + 'V' + (bottom - r) +
      'Q' + (x + w) + ',' + bottom + ' ' + (x + w - r) + ',' + bottom + 'H' + (tx + 4) + 'L' + tip[0] + ',' + tip[1] + 'L' + (tx - 4) + ',' + bottom +
      'H' + (x + r) + 'Q' + x + ',' + bottom + ' ' + x + ',' + (bottom - r) + 'V' + (y + r) + 'Q' + x + ',' + y + ' ' + (x + r) + ',' + y + 'Z';
    var b = g.append('g').style('opacity', p.op);
    stroke(b.append('path').attr('d', d), p.col, 1.6).style('fill', 'var(--card)');
    var text = b.append('text').attr('x', x + w / 2).attr('y', y + h / 2 + 3.8).attr('text-anchor', 'middle')
      .style('font', '400 11px "Atkinson Hyperlegible", system-ui, sans-serif').style('fill', 'var(--ink)');
    p.text.split(/(\s+)/).forEach(function (part) {
      var word = part.replace(/[.,!?]/g, '');
      var ts = text.append('tspan').text(part);
      if (p.hl && word === p.hl) ts.style('font-weight', 700).style('fill', 'var(--tab)').style('text-decoration', 'underline');
    });
  }
  function draw(g, prims) {
    prims.forEach(function (p) {
      if (p.t === 'chain') stroke(g.append('path').attr('d', smooth(p.pts)), p.c, 3.2);
      else if (p.t === 'head') drawHead(g, p);
      else if (p.t === 'bun') stroke(g.append('circle').attr('cx', p.c[0]).attr('cy', p.c[1]).attr('r', p.r), p.col, 2.6).style('fill', 'var(--fig-ground)');
      else if (p.t === 'spot') g.append('ellipse').attr('cx', p.x).attr('cy', GROUND + 1).attr('rx', 23).attr('ry', 5.5)
        .style('fill', 'var(--marker)').style('opacity', p.op);
      else if (p.t === 'tag') g.append('text').attr('x', p.x).attr('y', p.y).attr('text-anchor', 'middle').style('opacity', p.op)
        .style('font', '700 12px "Atkinson Hyperlegible", system-ui, sans-serif').style('fill', 'var(--tab)').text(p.text);
    });
  }
  function ground(g) { stroke(g.append('path').attr('d', 'M12,140.5H188'), 'var(--rule)', 1.6); }

  // ---------- scenes ----------
  var ease = d3.easeCubicInOut;
  // 0 -> 1 over `rise` ms, hold, back to 0 over `rise` ms ending at `end`
  function envelope(u, start, end, rise) {
    if (u < start || u > end) return 0;
    if (u < start + rise) return ease((u - start) / rise);
    if (u > end - rise) return ease((end - u) / rise);
    return 1;
  }
  function between(u, a, b) { return u >= a && u <= b; }
  var toChest = d3.interpolate(POSES.stand, POSES.chest), toPoint = d3.interpolate(POSES.stand, POSES.point);

  var SCENES = {
    man: {
      label: 'A man standing.',
      still: true,
      frame: function () { return [figure({ x: 100 })]; }
    },
    woman: {
      label: 'A woman standing.',
      still: true,
      frame: function () { return [figure({ x: 100, kind: 'woman' })]; }
    },
    I: {
      label: 'A man puts his hand on his chest and says: I am a man.',
      period: 4400, rest: 2200,
      frame: function (t) {
        var u = t % this.period, e = envelope(u, 200, 4000, 650);
        return [figure({ x: 100, accent: true, pose: toChest(e), say: between(u, 700, 3600) ? { text: 'I am a man.', hl: 'I' } : null })];
      }
    },
    am: {
      label: 'A man puts his hand on his chest and says: I am a man. Then a woman puts her hand on her chest and says: I am a woman.',
      period: 8800, rest: 2200,
      frame: function (t) {
        var u = t % this.period, first = u < 4400, v = u % 4400, e = envelope(v, 200, 4000, 650);
        var M = { x: 60, facing: 1 }, Wo = { x: 142, facing: -1, kind: 'woman' };
        var sp = first ? M : Wo, li = first ? Wo : M;
        var say = between(v, 700, 3600) ? { text: first ? 'I am a man.' : 'I am a woman.', hl: 'am' } : null;
        return [
          { t: 'spot', x: sp.x, op: e },
          figure({ x: li.x, facing: li.facing, kind: li.kind }),
          figure({ x: sp.x, facing: sp.facing, kind: sp.kind, accent: true, pose: toChest(e), say: say })
        ];
      }
    },
    you: {
      label: 'Two men. One points at the other and says: You are a man. Then the other man points back and says the same.',
      period: 8800, rest: 2200,
      frame: function (t) {
        var u = t % this.period, first = u < 4400, v = u % 4400, e = envelope(v, 200, 4000, 650);
        var A = { x: 56, facing: 1 }, B = { x: 146, facing: -1 }, sp = first ? A : B, li = first ? B : A;
        return [
          { t: 'spot', x: li.x, op: e },
          figure({ x: li.x, facing: li.facing }),
          figure({ x: sp.x, facing: sp.facing, accent: true, pose: toPoint(e), say: between(v, 700, 3600) ? { text: 'You are a man.', hl: 'You' } : null })
        ];
      }
    },
    a: {
      label: 'Three men. One at a time, any one of them is picked out: a man.',
      period: 5400, rest: 900,
      frame: function (t) {
        var xs = [44, 100, 156], faces = [1, 1, -1], order = [0, 2, 1];
        var slot = Math.floor((t % this.period) / 1800), v = t % 1800, pick = order[slot];
        var e = envelope(v, 0, 1800, 350);
        var out = [{ t: 'spot', x: xs[pick], op: e }];
        xs.forEach(function (x, i) {
          out.push({ t: 'group', op: i === pick ? 0.28 + 0.72 * e : 0.28, prims: figure({ x: x, facing: faces[i] }) });
        });
        out.push({ t: 'tag', x: xs[pick], y: 36, text: 'a man', op: e });
        return out;
      }
    }
  };

  // ---------- mounting ----------
  var live = [];
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function render(svg, scene, t) {
    svg.selectAll('g.fig').remove();
    var g = svg.append('g').attr('class', 'fig');
    var prims = scene.frame(t);
    var bubbles = [];
    prims.forEach(function (p) {
      if (Array.isArray(p)) { p.forEach(function (q) { if (q.t === 'bubble') bubbles.push(q); }); draw(g, p.filter(function (q) { return q.t !== 'bubble'; })); }
      else if (p.t === 'group') { var sub = g.append('g').style('opacity', p.op); draw(sub, p.prims); }
      else draw(g, [p]);
    });
    bubbles.forEach(function (b) { drawBubble(g, b); });
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
    mountAll: function (container) {
      // stop animations whose picture has left the page
      live = live.filter(function (x) { if (!x.el.isConnected) { x.timer.stop(); return false; } return true; });
      (container || document).querySelectorAll('.scene[data-scene]').forEach(mount);
    }
  };
})();
