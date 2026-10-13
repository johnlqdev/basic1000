// Basic 1000 films: narrated stick-figure videos that explain a grammar rule.
// A film is data (content/grammar/lessons.py): a list of shots. Each shot has
//   lines  [{t: text, v: 'woman' (Sarah; Daniel by default), by: cast id (the line is that figure's
//          speech bubble), hl: [words to mark in the subtitle]}]  - spoken one after another;
//   cast   [{id, k: man|woman|boy|girl|dog|cat|cow|house|apple|book|glass|ball|box|egg|bird|tree|sun,
//           x, face: 1|-1, s: size, n: copies, gap, in/out: line number when it comes / goes,
//           enter: 'walk'|'pop', pose, poseAt, to: new x, toAt, holds: thing in the hand,
//           accent: true (teal), label, labelAt, spot, spotAt}];
//   board  [{at: line number, w: [words], r: {index: role}, tag: {index: label}, x: [crossed out]}]
//          - a row of word tiles at the top; when the next state comes, the same words glide
//          to their new places, new words appear and missing words fade.
// Events are tied to lines ("at line 2"), so a shot keeps time with the real recordings.
// Public API: BASIC_FILMS.mount(element, film, opts) -> { stop(), pause() }
//   opts.link(text) -> html: makes the words of the subtitle buttons (word pages); touching one pauses the film.
var BASIC_FILMS = (function () {
  'use strict';
  var W = 320, H = 180;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var ROLE = { n: 'noun', p: 'pron', v: 'verb', b: 'be', a: 'adj', art: 'art', neg: 'neg', q: 'q', x: 'bad', ok: 'good' };

  // ---------- drawing a shot at time t ----------
  function kit() { return BASIC_FIGURES.kit; }
  var widths = {}, measurer = null;
  function textWidth(svg, text) {
    if (widths[text] != null) return widths[text];
    if (!measurer || !measurer.isConnected) {
      measurer = d3.select(svg).append('text').attr('class', 'film-word').attr('x', -999).attr('y', -999).node();
    }
    measurer.textContent = text;
    widths[text] = measurer.getComputedTextLength() || text.length * 7.5;
    return widths[text];
  }
  // seconds since line k began, or -1 if it has not begun yet
  function since(state, k) { return k == null ? state.t : state.starts[k] == null ? -1 : state.t - state.starts[k]; }
  function lerp(a, b, k) { return a + (b - a) * k; }
  function ease(k) { return k <= 0 ? 0 : k >= 1 ? 1 : kit().ease(k); }

  function boardLayout(svg, words) {
    var gap = 7, pad = 8, ws = words.map(function (w) { return textWidth(svg, w) + pad * 2; });
    var total = ws.reduce(function (a, b) { return a + b; }, 0) + gap * (words.length - 1);
    var x = W / 2 - total / 2, out = [];
    ws.forEach(function (w) { out.push({ x: x, w: w }); x += w + gap; });
    return out;
  }
  function keys(words) {
    var seen = {};
    return words.map(function (w) {
      var k = w.toLowerCase().replace(/[^a-z']/g, '');
      seen[k] = (seen[k] || 0) + 1;
      return k + '#' + seen[k];
    });
  }
  function drawBoard(g, svg, shot, st) {
    var states = (shot.board || []).filter(function (b) { return since(st, b.at || 0) >= 0; });
    if (!states.length) return false;
    var cur = states[states.length - 1], prev = states.length > 1 ? states[states.length - 2] : null;
    var k = reduce ? 1 : ease(since(st, cur.at || 0) / 700);
    var L = boardLayout(svg, cur.w), K = keys(cur.w), pos = {};
    if (prev) {
      var PL = boardLayout(svg, prev.w), PK = keys(prev.w);
      PK.forEach(function (key, i) { pos[key] = { x: PL[i].x, w: PL[i].w, i: i }; });
      // words that are leaving fade out where they were
      PK.forEach(function (key, i) {
        if (K.indexOf(key) < 0 && k < 1) tile(g, prev.w[i], PL[i].x, PL[i].w, (prev.r || {})[i], 1 - k, 0, null, false);
      });
    }
    var y = 0;
    cur.w.forEach(function (w, i) {
      var p = pos[K[i]], x = L[i].x, wd = L[i].w, op = 1, dy = 0;
      if (p) { x = lerp(p.x, L[i].x, k); wd = lerp(p.w, L[i].w, k); }
      else if (prev) { op = k; dy = -10 * (1 - k); }
      else { var k0 = reduce ? 1 : ease((since(st, cur.at || 0) - i * 260) / 400); op = k0; dy = -10 * (1 - k0); }
      tile(g, w, x, wd, (cur.r || {})[i], op, dy + y, (cur.tag || {})[i], (cur.x || []).indexOf(i) >= 0);
    });
    return true;
  }
  function tile(g, word, x, w, role, op, dy, tag, crossed) {
    if (op <= 0.01) return;
    var t = g.append('g').attr('class', 'film-tile ' + (role ? 'r-' + (ROLE[role] || role) : '')).style('opacity', op)
      .attr('transform', 'translate(0,' + dy + ')');
    t.append('rect').attr('x', x).attr('y', 12).attr('width', w).attr('height', 27).attr('rx', 6);
    t.append('text').attr('class', 'film-word').attr('x', x + w / 2).attr('y', 31).attr('text-anchor', 'middle').text(word);
    if (tag) t.append('text').attr('class', 'film-tag').attr('x', x + w / 2).attr('y', 52).attr('text-anchor', 'middle').text(tag);
    if (crossed) t.append('path').attr('class', 'film-cross').attr('d', 'M' + (x + 3) + ',35L' + (x + w - 3) + ',16');
  }

  var PEOPLE = { man: 1, woman: 1, boy: 1, girl: 1 };
  function poseOf(c, st, moving) {
    var K = kit(), P = K.POSES, t = st.t;
    if (moving) return c.k === 'man' || c.k === 'woman' || c.k === 'boy' || c.k === 'girl' ? K.walking(t * (c.pose === 'run' ? 1.7 : 1)) : null;
    var name = c.pose, at = since(st, c.poseAt || 0);
    if (c.poseEnd != null && since(st, c.poseEnd) >= 0) name = null;
    if (!name || at < 0) return P.stand;
    if (name === 'wave') return K.waving(t);
    if (name === 'walk' || name === 'run') return K.walking(t * (name === 'run' ? 1.7 : 1));
    if (name === 'nod') return K.nodding(t);
    var target = P[name] || P.stand;
    return d3.interpolate(P.stand, target)(reduce ? 1 : ease(at / 500));
  }
  function drawThing(c, x, st, out) {
    var K = kit(), G = K.G, s = c.s || 1, f = c.face || 1, t = st.t;
    if (c.k === 'dog' || c.k === 'cat' || c.k === 'cow') out.push(K[c.k]({ x: x, s: s, f: f, t: t, c: c.accent ? K.COL.acc : null }));
    else if (c.k === 'house') out.push(K.house({ x: x, s: s }));
    else if (c.k === 'apple') out.push(K.apple({ x: x, y: (c.y || G) - 7 * s, r: 7 * s, c: c.accent ? K.COL.acc : null }));
    else if (c.k === 'book') out.push(K.book({ x: x, y: c.y || G, s: s }));
    else if (c.k === 'glass') out.push(K.glass({ x: x, y: c.y || G, s: s, level: 0.6 }));
    else if (c.k === 'ball') out.push([{ t: 'circle', x: x, y: (c.y || G) - 7 * s, r: 7 * s, c: K.COL.ink, w: 2.4, fill: K.COL.marker },
      { t: 'path', d: 'M' + (x - 7 * s) + ',' + ((c.y || G) - 7 * s) + 'q' + 7 * s + ',' + 5 * s + ' ' + 14 * s + ',0', c: K.COL.ink, w: 1.6 }]);
    else if (c.k === 'box') out.push({ t: 'path', d: 'M' + (x - 10 * s) + ',' + G + 'v' + (-16 * s) + 'h' + 20 * s + 'v' + 16 * s + 'Z', c: K.COL.ink, w: 2.6, fill: K.COL.ground });
    else if (c.k === 'egg') out.push({ t: 'path', d: 'M' + x + ',' + (G - 16 * s) + 'c' + 7 * s + ',0 ' + 8 * s + ',' + 15 * s + ' 0,' + 16 * s + 'c' + -8 * s + ',' + -1 * s + ' ' + -7 * s + ',' + -16 * s + ' 0,' + -16 * s + 'Z', c: K.COL.ink, w: 2.2, fill: K.COL.milk });
    else if (c.k === 'tree') out.push([{ t: 'path', d: 'M' + x + ',' + G + 'V' + (G - 30 * s), c: K.COL.ink, w: 3.4 },
      { t: 'circle', x: x, y: G - 44 * s, r: 18 * s, c: K.COL.ink, w: 2.6, fill: K.COL.leaf }]);
    else if (c.k === 'sun') {
      var sy = c.y || 34, rays = '';
      for (var a = 0; a < 8; a++) { var an = a * Math.PI / 4 + t / 3000; rays += 'M' + (x + 14 * Math.cos(an)) + ',' + (sy + 14 * Math.sin(an)) + 'L' + (x + 19 * Math.cos(an)) + ',' + (sy + 19 * Math.sin(an)); }
      out.push([{ t: 'circle', x: x, y: sy, r: 10, fill: K.COL.marker, c: K.COL.hot, w: 2 }, { t: 'path', d: rays, c: K.COL.hot, w: 2 }]);
    } else if (c.k === 'bird') {
      var by = (c.y || 60) + 3 * Math.sin(t / 300), fl = 4 * Math.sin(t / 120);
      out.push({ t: 'path', d: 'M' + (x - 8) + ',' + (by - fl) + 'Q' + (x - 4) + ',' + (by - 4) + ' ' + x + ',' + by + 'Q' + (x + 4) + ',' + (by - 4) + ' ' + (x + 8) + ',' + (by - fl), c: K.COL.ink, w: 2 });
    }
  }
  function drawCast(g, shot, st, boardShown) {
    var K = kit(), G = K.G, out = [], late = [];
    var speaking = null;
    (shot.lines || []).forEach(function (l, i) { if (l.by && st.line === i) speaking = l; });
    (shot.cast || []).forEach(function (c) {
      var tin = since(st, c.in || 0);
      if (tin < 0) return;
      if (c.out != null && since(st, c.out) >= 0) return;
      var op = c.enter === 'walk' || reduce ? 1 : ease(tin / 450), x = c.x, moving = false;
      if (c.enter === 'walk' && !reduce) {
        var k = ease(tin / 1500), from = (c.face || 1) > 0 ? -30 : W + 30;
        x = lerp(from, c.x, k); moving = k < 1;
      }
      if (c.to != null && since(st, c.toAt || 0) >= 0) {
        var km = reduce ? 1 : ease(since(st, c.toAt || 0) / 1300);
        x = lerp(c.x, c.to, km); moving = moving || (km > 0 && km < 1);
      }
      var n = c.n || 1, gap = c.gap || 26;
      for (var j = 0; j < n; j++) {
        var xj = x + j * gap, prims = [];
        if (c.spot && since(st, c.spotAt || 0) >= 0) prims.push({ t: 'spot', x: xj, rx: c.spot === true ? 22 : c.spot, op: ease(since(st, c.spotAt || 0) / 400) });
        if (PEOPLE[c.k]) {
          var say = speaking && speaking.by === c.id && !boardShown && j === 0 ? { text: speaking.t, hl: speaking.hl } : null;
          var fig = K.figure({ x: xj, kind: c.k, facing: c.face || 1, pose: poseOf(c, st, moving), accent: c.accent, say: say, s: c.s });
          prims.push(fig);
          if (c.holds) drawThing({ k: c.holds, s: 0.7, y: fig.hand[1] + 6 }, fig.hand[0], st, prims);
        } else drawThing(c, xj, st, prims);
        out.push(op < 1 ? [{ t: 'group', op: op, prims: prims }] : prims);
      }
      if (c.label && since(st, c.labelAt || 0) >= 0) {
        late.push({ x: x + (n - 1) * gap / 2, text: c.label, role: c.labelRole, op: ease(since(st, c.labelAt || 0) / 400) });
      }
    });
    K.width(W);
    K.draw(g, out);
    K.width(200);
    late.forEach(function (l) {
      g.append('text').attr('class', 'film-label ' + (l.role ? 'r-' + (ROLE[l.role] || l.role) : '')).attr('x', l.x).attr('y', G + 17)
        .attr('text-anchor', 'middle').style('opacity', l.op).text(l.text);
    });
  }
  function render(svg, shot, st) {
    var root = d3.select(svg).select('g.film-scene');
    root.selectAll('*').remove();
    root.append('path').attr('class', 'film-ground').attr('d', 'M12,' + (kit().G + 0.5) + 'H' + (W - 12));
    // the cast first, then the word board on top of it, so tags under the words stay readable
    var castG = root.append('g'), b = root.append('g');
    var shown = drawBoard(b, svg, shot, st);
    drawCast(castG, shot, st, shown);
  }

  // ---------- sound ----------
  function speak(line, ctl) {
    var A = window.BASIC_AUDIO, voice = line.v === 'woman' ? 'woman' : 'man';
    return new Promise(function (done) {
      var finished = false, finish = function () { if (!finished) { finished = true; ctl.audio = null; done(); } };
      var fallback = function () {
        if (!window.speechSynthesis) { setTimeout(finish, 450 * line.t.split(' ').length + 600); return; }
        // some browsers never end an utterance; do not let the film hang on one
        setTimeout(finish, 650 * line.t.split(' ').length + 2500);
        var u = new SpeechSynthesisUtterance(line.t);
        u.lang = 'en-US'; u.rate = 0.9;
        u.onend = u.onerror = finish;
        ctl.utter = u;
        speechSynthesis.speak(u);
      };
      if (!A) { fallback(); return; }
      A.clipUrl(line.t, voice).then(function (url) {
        var a = new Audio(url);
        ctl.audio = a;
        a.onended = finish;
        a.onerror = function () { ctl.audio = null; fallback(); };
        if (!ctl.paused) a.play().catch(function () { ctl.audio = null; fallback(); });
      }, fallback);
    });
  }

  // mark the words in hl: linked words get a class, plain words are wrapped in <mark>
  function markWords(root, hl) {
    if (!hl.length) return;
    var bare = function (s) { return s.toLowerCase().replace(/[^a-z']/g, ''); };
    root.querySelectorAll('[data-word]').forEach(function (b) { if (hl.indexOf(bare(b.textContent)) >= 0) b.classList.add('film-mark'); });
    var walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), texts = [];
    while (walk.nextNode()) if (!walk.currentNode.parentNode.closest('[data-word]')) texts.push(walk.currentNode);
    texts.forEach(function (t) {
      var parts = t.nodeValue.split(/([A-Za-z']+)/);
      if (!parts.some(function (p) { return hl.indexOf(bare(p)) >= 0 && p; })) return;
      var frag = document.createDocumentFragment();
      parts.forEach(function (p) {
        if (p && hl.indexOf(bare(p)) >= 0) { var m = document.createElement('mark'); m.textContent = p; frag.appendChild(m); }
        else if (p) frag.appendChild(document.createTextNode(p));
      });
      t.parentNode.replaceChild(frag, t);
    });
  }

  // ---------- the player ----------
  function mount(el, film, opts) {
    opts = opts || {};
    var PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/></svg>';
    var PAUSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" fill="currentColor"/></svg>';
    var secs = film.reduce(function (n, s) { return n + (s.lines || []).reduce(function (m, l) { return m + 0.42 * l.t.split(' ').length + 1; }, 1); }, 0);
    el.innerHTML = '<div class="film"><div class="film-screen"><svg class="film-svg" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="A film that shows the rule"><g class="film-scene"></g></svg>' +
      '<button type="button" class="film-big" aria-label="Play the film">' + PLAY + '<span>Watch · about ' + Math.max(1, Math.round(secs / 60)) + ' min</span></button></div>' +
      '<p class="film-sub" aria-live="polite"></p>' +
      '<div class="film-bar"><button type="button" class="film-play" aria-label="Play">' + PLAY + '</button>' +
      '<div class="film-segs">' + film.map(function (_, i) { return '<button type="button" class="film-seg" data-i="' + i + '" aria-label="Part ' + (i + 1) + '"><i></i></button>'; }).join('') + '</div>' +
      '<span class="film-count num"></span></div></div>';
    var svg = el.querySelector('svg'), sub = el.querySelector('.film-sub'), big = el.querySelector('.film-big');
    var playBtn = el.querySelector('.film-play'), count = el.querySelector('.film-count');
    var ctl = { shot: 0, playing: false, paused: true, started: false, token: 0, audio: null, utter: null, raf: 0 };
    var st = { t: 0, starts: [], line: -1 }, clock = { base: 0, at: 0 };
    function now() { return ctl.paused ? clock.at : clock.at + (performance.now() - clock.base); }
    function setPaused(p) {
      if (p === ctl.paused) return;
      if (p) { clock.at = now(); ctl.paused = true; if (ctl.audio) ctl.audio.pause(); if (window.speechSynthesis) speechSynthesis.pause(); }
      else { clock.base = performance.now(); ctl.paused = false; if (ctl.audio) ctl.audio.play().catch(function () {}); if (window.speechSynthesis) speechSynthesis.resume(); }
      playBtn.innerHTML = p ? PLAY : PAUSE;
      playBtn.setAttribute('aria-label', p ? 'Play' : 'Pause');
    }
    function waitWhilePaused(token) {
      return new Promise(function (ok) { (function check() { if (token !== ctl.token) return ok(false); if (!ctl.paused) return ok(true); setTimeout(check, 120); })(); });
    }
    function sleep(ms, token) {
      var end = now() + ms;
      return new Promise(function (ok) { (function check() { if (token !== ctl.token) return ok(false); if (now() >= end) return ok(true); setTimeout(check, 50); })(); });
    }
    function showSub(line) {
      if (!line) { sub.innerHTML = ''; return; }
      var hl = (line.hl || []).map(function (w) { return w.toLowerCase(); });
      var html = opts.link ? opts.link(line.t) : esc(line.t);
      sub.innerHTML = line.by ? '<span class="film-quote">' + html + '</span>' : html;
      markWords(sub, hl);
    }
    function segs() {
      el.querySelectorAll('.film-seg').forEach(function (b, i) {
        var lines = (film[i].lines || []).length || 1;
        var k = i < ctl.shot ? 1 : i > ctl.shot ? 0 : st.line >= lines ? 1 : Math.max(0, (st.line + 0.5) / lines);
        b.firstChild.style.width = (k * 100) + '%';
        if (i === ctl.shot) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
      });
      count.textContent = (ctl.shot + 1) + ' / ' + film.length;
    }
    async function playShot(i) {
      var token = ++ctl.token;
      if (ctl.audio) { ctl.audio.pause(); ctl.audio = null; }
      if (window.speechSynthesis) speechSynthesis.cancel();
      ctl.shot = i; st.starts = []; st.line = -1; clock.at = 0; clock.base = performance.now();
      segs();
      var shot = film[i], lines = shot.lines || [];
      if (!(await sleep(500, token))) return;
      for (var k = 0; k < lines.length; k++) {
        if (!(await waitWhilePaused(token))) return;
        st.starts[k] = now(); st.line = k; showSub(lines[k]); segs();
        await speak(lines[k], ctl);
        if (token !== ctl.token) return;
        if (!(await sleep(380, token))) return;
      }
      st.line = lines.length; segs();
      el.firstChild.dataset.held = i; // every line of shot i has been said (tests wait for this)
      if (!(await sleep(Math.max(900, (shot.min || 0) - now()), token))) return;
      if (i + 1 < film.length) playShot(i + 1);
      else { setPaused(true); showSub(null); big.hidden = false; big.querySelector('span').textContent = 'Watch again'; ctl.started = false; }
    }
    function frame() {
      if (!el.isConnected) { stop(); return; }
      st.t = now();
      render(svg, film[ctl.shot], st);
      ctl.raf = requestAnimationFrame(frame);
    }
    function start(i) {
      if (window.BASIC_AUDIO) BASIC_AUDIO.stop();
      big.hidden = true; ctl.started = true;
      setPaused(false);
      playShot(i || 0);
    }
    function stop() {
      ctl.token++;
      cancelAnimationFrame(ctl.raf);
      if (ctl.audio) ctl.audio.pause();
      if (window.speechSynthesis) speechSynthesis.cancel();
    }
    big.addEventListener('click', function () { start(0); });
    sub.addEventListener('click', function (e) { if (e.target.closest('[data-word]') && ctl.started) setPaused(true); });
    playBtn.addEventListener('click', function () { if (!ctl.started) start(ctl.shot); else setPaused(!ctl.paused); });
    el.querySelectorAll('.film-seg').forEach(function (b) { b.addEventListener('click', function () { start(+b.dataset.i); }); });
    // before playing, show the first shot with everything in it
    st.t = 0; st.starts = (film[0].lines || []).map(function () { return -100000; }); st.line = -1;
    render(svg, film[0], st);
    st.starts = [];
    segs();
    ctl.raf = requestAnimationFrame(function loop() {
      if (!ctl.started && !el.isConnected) return;
      if (ctl.started) frame(); else ctl.raf = requestAnimationFrame(loop);
    });
    return { stop: stop, pause: function () { if (ctl.started) setPaused(true); } };
  }

  return { mount: mount, render: render };
})();
