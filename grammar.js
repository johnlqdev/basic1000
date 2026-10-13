// Basic 1000 grammar: how the words fit together, explained only with the 1,000 words.
// The topics and lessons are data (grammar-data.js, built from content/grammar/ by tools/grammar/build.py):
//   nodes   [{id, band, title, needs: [ids], goal, terms: {term: meaning}, points, examples}]
//           - the "needs" make a dependency tree: a topic opens when every topic it needs is done;
//   lessons {id: {film: [shots], rule: {table, examples}, machine: {people, forms}, tasks: [...]}}
//           - only some topics have a full lesson so far; the others show as "coming soon".
// A lesson page: 1 Watch (a stick-figure film), 2 The rule, 3 Play (the sentence machine, for some
// topics), then Try it. Getting at least two thirds of the exercises right finishes the topic.
// Public API: BASIC_GRAMMAR.home(container, ctx), BASIC_GRAMMAR.lesson(container, ctx, topicId)
//   ctx = { say(text, button, voice), result(id) -> best score or undefined, save(id, score), open(id), back(),
//           link(text) -> html with every Basic 1000 word as a button that opens its word page }
// The courses are one site: every word in a rule, an example or a film line opens that word's page
// (which counts a visit), and from there its step in Basic 1000.
var BASIC_GRAMMAR = (function () {
  'use strict';
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var D = window.BASIC_GRAMMAR_DATA || { bands: {}, nodes: [], lessons: {} };
  var NODES = D.nodes, LESSONS = D.lessons, BY = {}, KIDS = {}, DEPTH = {}, ANC = {};
  NODES.forEach(function (n, i) { n.no = i + 1; BY[n.id] = n; KIDS[n.id] = []; });
  NODES.forEach(function (n) {
    n.needs.forEach(function (d) { KIDS[d].push(n.id); });
    DEPTH[n.id] = n.needs.reduce(function (m, d) { return Math.max(m, DEPTH[d] + 1); }, 0);
    var a = {};
    n.needs.forEach(function (d) { a[d] = 1; Object.keys(ANC[d]).forEach(function (x) { a[x] = 1; }); });
    ANC[n.id] = a;
  });
  // lines on the map: only the direct links (a -> c is left out when a -> b -> c is there)
  var EDGES = [];
  NODES.forEach(function (n) {
    n.needs.forEach(function (d) {
      if (!n.needs.some(function (o) { return o !== d && ANC[o][d]; })) EDGES.push([d, n.id]);
    });
  });

  var SAY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var ICON = {
    done: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.4l3 3 6-6.6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    open: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5.5 3.8v8.4L12.3 8z" fill="currentColor"/></svg>',
    locked: '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3.5" y="7" width="9" height="6.5" rx="1.5" fill="currentColor"/><path d="M5.5 7V5.5a2.5 2.5 0 0 1 5 0V7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    soon: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="2.4" fill="currentColor"/></svg>'
  };
  var LINK = function (t) { return esc(t); };
  function useLinks(ctx) { LINK = ctx.link || function (t) { return esc(t); }; }
  function sayBtn(text, voice, label) {
    return '<button type="button" class="say" data-say="' + esc(text) + '"' + (voice ? ' data-voice="' + voice + '"' : '') +
      ' aria-label="' + esc(label || 'Listen') + '" title="Listen">' + SAY_ICON + '</button>';
  }

  // ---------- progress ----------
  function total(id) { return LESSONS[id] ? LESSONS[id].tasks.length : 0; }
  function passMark(id) { return Math.ceil(total(id) * 2 / 3); }
  function isDone(ctx, id) { var r = ctx.result(id); return r != null && total(id) > 0 && r >= passMark(id); }
  function stateOf(ctx, id) {
    if (isDone(ctx, id)) return 'done';
    if (!LESSONS[id]) return 'soon';
    return BY[id].needs.every(function (d) { return isDone(ctx, d); }) ? 'open' : 'locked';
  }
  function missing(ctx, id) { return BY[id].needs.filter(function (d) { return !isDone(ctx, d); }); }
  var STATE_WORD = { done: 'Done', open: 'Open', locked: 'Locked', soon: 'Coming soon' };

  // ---------- the map ----------
  function home(el, ctx) {
    var states = {};
    NODES.forEach(function (n) { states[n.id] = stateOf(ctx, n.id); });
    var done = NODES.filter(function (n) { return states[n.id] === 'done'; }).length;
    var ready = Object.keys(LESSONS).length;
    var next = NODES.filter(function (n) { return states[n.id] === 'open'; })[0];

    // rows: by band, then by depth in the tree; inside a row, children sit under their parents
    var place = {}, bands = Object.keys(D.bands);
    var rows = bands.map(function (b) {
      var depths = {};
      NODES.forEach(function (n) { if (n.band === b) (depths[DEPTH[n.id]] = depths[DEPTH[n.id]] || []).push(n); });
      return { band: b, rows: Object.keys(depths).map(Number).sort(function (a, c) { return a - c; }).map(function (d) { return depths[d]; }) };
    });
    // order by the mean place of the parents, so lines cross less
    var flat = [];
    rows.forEach(function (b) { b.rows.forEach(function (r) { flat.push(r); }); });
    flat.sort(function (a, c) { return DEPTH[a[0].id] - DEPTH[c[0].id]; });
    flat.forEach(function (r) {
      var key = function (n) { return n.needs.length ? n.needs.reduce(function (s, d) { return s + (place[d] != null ? place[d] : 0.5); }, 0) / n.needs.length : 0.5; };
      r.sort(function (a, c) { return key(a) - key(c) || a.no - c.no; });
      r.forEach(function (n, i) { place[n.id] = r.length === 1 ? 0.5 : i / (r.length - 1); });
    });

    var pill = function (n) {
      var s = states[n.id];
      return '<button type="button" class="g-node is-' + s + '" data-id="' + n.id + '" aria-label="' + esc(n.title + ', ' + STATE_WORD[s]) + '">' +
        '<span class="g-node-ic">' + ICON[s] + '</span><span class="g-node-t">' + esc(n.title) + '</span></button>';
    };
    el.innerHTML = '<section class="g-head"><h1 class="g-title">Grammar</h1>' +
      '<p class="g-lede">How the words you know fit together, from your first sentence to high school. Every rule is explained with the 1,000 words.</p>' +
      '<p class="g-stats"><span class="num">' + done + '</span> of <span class="num">' + NODES.length + '</span> topics done' +
      ' <span class="muted">· ' + ready + ' have full lessons so far</span></p></section>' +
      (next ? '<div class="g-next panel"><div><p class="eyebrow">Next for you</p><h2 class="g-next-t">' + esc(next.title) + '</h2><p class="muted">' + esc(next.goal) + '</p></div>' +
        '<button type="button" class="btn primary" data-start="' + next.id + '">' + (ctx.result(next.id) != null ? 'Try again' : 'Start') + '</button></div>'
        : '<div class="g-next panel"><div><p class="eyebrow">All caught up</p><p class="muted">You have finished every topic that has a lesson. More are on the way.</p></div></div>') +
      '<div class="g-map-head"><h2 class="g-map-title">The map</h2><p class="muted g-note">Each topic builds on the ones above it, joined by lines. Finish a topic to open the ones under it. Touch any topic to see what it needs and what it opens.</p>' +
      '<ul class="g-legend">' + ['done', 'open', 'locked', 'soon'].map(function (s) { return '<li><span class="g-node is-' + s + ' g-key"><span class="g-node-ic">' + ICON[s] + '</span></span>' + STATE_WORD[s] + '</li>'; }).join('') + '</ul></div>' +
      '<div class="g-map"><svg class="g-edges" aria-hidden="true"></svg>' +
      rows.map(function (b) {
        var count = b.rows.reduce(function (s, r) { return s + r.length; }, 0);
        var bdone = b.rows.reduce(function (s, r) { return s + r.filter(function (n) { return states[n.id] === 'done'; }).length; }, 0);
        return '<section class="g-band"><h3 class="g-band-t"><span>' + esc(D.bands[b.band]) + '</span><small class="num">' + bdone + ' / ' + count + '</small></h3>' +
          b.rows.map(function (r) { return '<div class="g-row">' + r.map(pill).join('') + '</div>'; }).join('') + '</section>';
      }).join('') + '</div>';

    var map = el.querySelector('.g-map'), svg = map.querySelector('.g-edges');
    var focus = null;
    function draw() {
      if (!map.isConnected) { if (ro) ro.disconnect(); return; }
      var box = map.getBoundingClientRect(), pos = {};
      map.querySelectorAll('.g-row .g-node').forEach(function (b) {
        var r = b.getBoundingClientRect();
        pos[b.dataset.id] = { x: r.left - box.left + r.width / 2, top: r.top - box.top, bottom: r.bottom - box.top };
      });
      svg.setAttribute('width', box.width); svg.setAttribute('height', box.height);
      svg.setAttribute('viewBox', '0 0 ' + box.width + ' ' + box.height);
      var lit = focus ? Object.assign({}, ANC[focus], (function () { var o = {}; o[focus] = 1; return o; })()) : null;
      svg.innerHTML = EDGES.map(function (e) {
        var a = pos[e[0]], c = pos[e[1]];
        if (!a || !c) return '';
        var y1 = a.bottom, y2 = c.top, m = Math.max(18, (y2 - y1) / 2);
        var cls = states[e[0]] === 'done' && states[e[1]] === 'done' ? 'on' : states[e[0]] === 'done' && states[e[1]] === 'open' ? 'next' : '';
        if (focus) cls += lit[e[0]] && lit[e[1]] ? ' need' : e[0] === focus ? ' kid' : ' dim';
        return '<path class="' + cls + '" d="M' + a.x + ',' + y1 + 'C' + a.x + ',' + (y1 + m) + ' ' + c.x + ',' + (y2 - m) + ' ' + c.x + ',' + y2 + '"/>';
      }).join('');
    }
    function setFocus(id) {
      focus = id;
      map.classList.toggle('has-focus', !!id);
      map.querySelectorAll('.g-row .g-node').forEach(function (b) {
        var k = b.dataset.id;
        b.classList.toggle('hl-self', k === id);
        b.classList.toggle('hl-need', !!id && !!ANC[id][k]);
        b.classList.toggle('hl-kid', !!id && KIDS[id].indexOf(k) >= 0);
      });
      draw();
    }
    var ro = window.ResizeObserver ? new ResizeObserver(function () { draw(); }) : null;
    if (ro) ro.observe(map); else window.addEventListener('resize', draw);
    requestAnimationFrame(draw);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);

    el.querySelectorAll('[data-start]').forEach(function (b) { b.addEventListener('click', function () { ctx.open(b.dataset.start); }); });
    map.addEventListener('click', function (e) {
      var b = e.target.closest('.g-node[data-id]');
      if (b) openSheet(ctx, b.dataset.id, states, setFocus);
    });
    map.addEventListener('mouseover', function (e) {
      var b = e.target.closest('.g-node[data-id]');
      if (b && !sheetOpen()) setFocus(b.dataset.id);
    });
    map.addEventListener('mouseleave', function () { if (!sheetOpen()) setFocus(null); });
  }

  // ---------- the topic card (opens over the map) ----------
  var scrim = null;
  function sheetOpen() { return scrim && !scrim.hidden; }
  function closeSheet() {
    if (!scrim) return;
    scrim.hidden = true; scrim.innerHTML = '';
    if (window.BASIC_AUDIO) BASIC_AUDIO.stop();
    if (scrim.onclose) scrim.onclose();
  }
  function chipList(ids, states) {
    if (!ids.length) return '<p class="muted g-sheet-none">Nothing. This is a place to begin.</p>';
    return '<div class="g-links">' + ids.map(function (id) {
      var s = states[id];
      return '<button type="button" class="g-node is-' + s + '" data-go="' + id + '"><span class="g-node-ic">' + ICON[s] + '</span><span class="g-node-t">' + esc(BY[id].title) + '</span></button>';
    }).join('') + '</div>';
  }
  function openSheet(ctx, id, states, setFocus) {
    if (!scrim) {
      scrim = document.createElement('div');
      scrim.className = 'scrim g-scrim';
      scrim.hidden = true;
      document.body.appendChild(scrim);
      scrim.addEventListener('click', function (e) { if (e.target === scrim) closeSheet(); });
      // Escape closes only the top card: a word page opened from this card closes first (capture runs before the page's own handler)
      window.addEventListener('keydown', function (e) {
        var word = document.getElementById('scrim');
        if (e.key === 'Escape' && sheetOpen() && !(word && !word.hidden)) closeSheet();
      }, true);
    }
    useLinks(ctx);
    var n = BY[id], s = states[id], best = ctx.result(id), les = LESSONS[id];
    var status = s === 'done' ? 'Done. Your best: <b class="num">' + best + ' / ' + total(id) + '</b>'
      : s === 'open' ? (best != null ? 'Your best so far: <b class="num">' + best + ' / ' + total(id) + '</b>. Get ' + passMark(id) + ' right to finish it.' : 'Ready for you.')
      : s === 'locked' ? 'Opens when you finish ' + missing(ctx, id).map(function (d) { return '<b>' + esc(BY[d].title) + '</b>'; }).join(' and ') + '.'
      : 'The full lesson is coming soon. Here is what it will teach.';
    var actions = s === 'soon' ? ''
      : '<div class="row g-sheet-go"><button type="button" class="btn ' + (s === 'locked' ? '' : 'primary') + '" data-lesson="' + id + '">' +
        (s === 'locked' ? 'Look inside' : s === 'done' ? 'Do it again' : best != null ? 'Try again' : 'Start') + '</button></div>';
    var terms = Object.keys(n.terms || {});
    scrim.innerHTML = '<div class="sheet g-sheet" role="dialog" aria-modal="true" aria-label="' + esc(n.title) + '">' +
      '<button class="btn quiet sheet-close" type="button" data-close>Close</button>' +
      '<p class="eyebrow">' + esc(D.bands[n.band]) + ' · topic ' + n.no + ' of ' + NODES.length + '</p>' +
      '<h2 class="g-sheet-t">' + esc(n.title) + '</h2>' +
      '<p class="g-sheet-goal">' + LINK(n.goal) + '</p>' +
      '<p class="g-sheet-status is-' + s + '"><span class="g-node-ic">' + ICON[s] + '</span><span>' + status + '</span></p>' +
      (s === 'soon' ? '<ul class="g-points">' + n.points.map(function (p) { return '<li>' + LINK(p) + '</li>'; }).join('') + '</ul>' +
        '<ul class="g-examples">' + n.examples.map(function (e) { return '<li>' + sayBtn(e) + '<span>' + LINK(e) + '</span></li>'; }).join('') + '</ul>' : '') +
      (terms.length ? '<p class="g-sheet-terms muted">New grammar words: ' + terms.map(function (t) { return '<b>' + esc(t) + '</b>'; }).join(', ') + '</p>' : '') +
      actions +
      '<h3 class="g-sheet-h">First learn</h3>' + chipList(n.needs, states) +
      '<h3 class="g-sheet-h">Then you can learn</h3>' + chipList(KIDS[id], states) +
      (les ? '' : '') + '</div>';
    scrim.hidden = false;
    scrim.onclose = function () { setFocus(null); };
    setFocus(id);
    scrim.querySelector('[data-close]').focus();
    scrim.querySelector('[data-close]').addEventListener('click', closeSheet);
    scrim.querySelectorAll('[data-go]').forEach(function (b) { b.addEventListener('click', function () { openSheet(ctx, b.dataset.go, states, setFocus); }); });
    scrim.querySelectorAll('[data-lesson]').forEach(function (b) { b.addEventListener('click', function () { var to = b.dataset.lesson; closeSheet(); ctx.open(to); }); });
    scrim.querySelectorAll('[data-say]').forEach(function (b) { b.addEventListener('click', function () { ctx.say(b.dataset.say, b); }); });
  }

  // ---------- the sentence machine ----------
  // One sentence as tiles. Pick who it is about; make it plain, "not", or a question.
  // The tiles keep their identity, so when the form changes they glide to their new places:
  // in a question, the "be" tile jumps to the front.
  var cap = function (w) { return w.charAt(0).toUpperCase() + w.slice(1); };
  var subj = function (w, first) { return w === 'I' ? 'I' : first ? cap(w) : w; };
  function machineTiles(p, form) {
    if (form === 'question') return [['be', cap(p.be)], ['s', subj(p.s, false)], ['rest', p.rest + '?']];
    var t = [['s', subj(p.s, true)], ['be', p.be]];
    if (form === 'not') t.push(['not', 'not']);
    return t.concat([['rest', p.rest + '.']]); // the full stop rides on the last tile, so it never wraps alone
  }
  function answers(p, form) {
    if (form !== 'question') return [];
    var s = p.s === 'I' ? 'you' : p.s === 'you' ? 'I' : p.s;
    var be = s === 'I' ? 'am' : s === 'you' || s === 'we' || s === 'they' ? 'are' : 'is';
    return ['Yes, ' + subj(s, false) + ' ' + be + '.', 'No, ' + subj(s, false) + ' ' + be + ' not.'];
  }
  // move tiles to their new order with a FLIP animation (first, last, invert, play)
  function flip(line, tiles) {
    var old = {};
    Array.prototype.forEach.call(line.children, function (el) { old[el.dataset.k] = { el: el, r: el.getBoundingClientRect() }; });
    var keep = {};
    tiles.forEach(function (t) {
      var el = old[t[0]] ? old[t[0]].el : null;
      if (!el) {
        el = document.createElement('span');
        el.className = 'gm-tile gm-' + t[0];
        el.dataset.k = t[0];
        el.dataset.enter = '1';
      }
      if (el.textContent !== t[1]) { el.textContent = t[1]; if (t[0] === 'be' && old.be) el.dataset.swap = '1'; }
      keep[t[0]] = true;
      line.appendChild(el); // appending in order also reorders the existing tiles
    });
    Object.keys(old).forEach(function (k) { if (!keep[k]) old[k].el.remove(); });
    if (reduce) {
      Array.prototype.forEach.call(line.children, function (el) { delete el.dataset.enter; delete el.dataset.swap; });
      return;
    }
    Array.prototype.forEach.call(line.children, function (el) {
      var o = old[el.dataset.k];
      if (el.dataset.enter) {
        el.animate([{ transform: 'translateY(-14px) scale(.7)', opacity: 0 }, { transform: 'none', opacity: 1 }], { duration: 380, easing: 'cubic-bezier(.2,1.3,.4,1)' });
        delete el.dataset.enter;
        return;
      }
      var r = el.getBoundingClientRect(), dx = o.r.left - r.left, dy = o.r.top - r.top;
      var frames = [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }];
      if (el.dataset.k === 'be' && Math.abs(dx) > 20) { // the word that moves to the front of a question takes a hop
        frames = [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'translate(' + dx / 2 + 'px,' + (dy / 2 - 28) + 'px)', offset: 0.5 }, { transform: 'none' }];
      }
      if (dx || dy) el.animate(frames, { duration: 520, easing: 'cubic-bezier(.3,.7,.2,1)' });
      if (el.dataset.swap) { el.animate([{ transform: 'rotateX(90deg)' }, { transform: 'none' }], { duration: 300, easing: 'ease-out' }); delete el.dataset.swap; }
    });
  }
  var FORM_NAMES = { plain: 'Say it', not: 'Say it with not', question: 'Ask it' };
  function machine(box, ctx, m) {
    var people = m.people, forms = m.forms;
    var state = { p: Math.min(3, people.length - 1), form: forms[forms.length - 1] };
    box.innerHTML =
      '<div class="gm-who" role="group" aria-label="Who is it about?">' +
      people.map(function (p, i) { return '<button type="button" class="gm-chip" data-p="' + i + '" aria-pressed="false">' + esc(subj(p.s, true)) + '</button>'; }).join('') + '</div>' +
      '<div class="gm-stage"><div class="gm-line" aria-live="polite"></div>' +
      '<button type="button" class="say gm-say" aria-label="Listen to the sentence" title="Listen">' + SAY_ICON + '</button></div>' +
      '<p class="gm-answer"></p>' +
      (forms.length > 1 ? '<div class="gm-forms" role="group" aria-label="Make it">' +
        forms.map(function (f) { return '<button type="button" class="gm-form" data-f="' + f + '" aria-pressed="false">' + FORM_NAMES[f] + '</button>'; }).join('') + '</div>' : '');
    var line = box.querySelector('.gm-line');
    function draw(first) {
      var p = people[state.p], tiles = machineTiles(p, state.form);
      if (first) line.innerHTML = tiles.map(function (t) { return '<span class="gm-tile gm-' + t[0] + '" data-k="' + t[0] + '">' + esc(t[1]) + '</span>'; }).join('');
      else flip(line, tiles);
      box.querySelector('.gm-answer').innerHTML = answers(p, state.form).map(function (a) { return '<span class="gm-reply">' + sayBtn(a, null, 'Listen to the answer') + esc(a) + '</span>'; }).join('');
      box.querySelectorAll('[data-p]').forEach(function (b) { b.setAttribute('aria-pressed', String(+b.dataset.p === state.p)); });
      box.querySelectorAll('[data-f]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.f === state.form)); });
      box.dataset.sentence = tiles.map(function (t) { return t[1]; }).join(' ');
    }
    box.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      if (b.dataset.p != null) { state.p = +b.dataset.p; draw(); }
      else if (b.dataset.f) { state.form = b.dataset.f; draw(); }
      else if (b.classList.contains('gm-say')) ctx.say(box.dataset.sentence, b);
      else if (b.dataset.say) ctx.say(b.dataset.say, b);
    });
    draw(true);
    return {
      pick: function (word) {
        var i = people.findIndex(function (p) { return p.s.toLowerCase() === word.toLowerCase(); });
        if (i >= 0) { state.p = i; draw(); return true; }
        return false;
      }
    };
  }

  // ---------- try it ----------
  // kinds: pick (choose the word for the space, or the right answer), build (touch the tiles in order),
  // fix (touch the wrong word, then pick the right one), tap (touch every word of one kind)
  function runTasks(box, ctx, tasks, done) {
    var n = 0, right = 0;
    function show() {
      var t = tasks[n];
      var dots = tasks.map(function (_, i) { return '<i class="' + (i < n ? 'on' : i === n ? 'cur' : '') + '"></i>'; }).join('');
      var body;
      if (t.kind === 'pick') {
        var gap = t.before || t.after;
        var long = t.opts.some(function (o) { return o.length > 14; });
        body = (gap ? '<p class="gt-sent">' + (t.before ? esc(t.before) + ' ' : '') + '<span class="gt-gap">&nbsp;</span>' + (t.after ? (/^[.?!,]/.test(t.after) ? '' : ' ') + esc(t.after) : '') + '</p>' : '') +
          '<div class="gt-opts' + (long ? ' gt-long' : '') + '">' + t.opts.map(function (o) { return '<button type="button" class="gm-tile gt-opt" data-o="' + esc(o) + '">' + esc(o) + '</button>'; }).join('') + '</div>';
      } else if (t.kind === 'build') {
        body = '<p class="gt-sent gt-built" aria-live="polite"><span class="muted gt-hint">Touch the words below.</span></p>' +
          '<div class="gt-opts">' + t.tiles.map(function (o, i) { return '<button type="button" class="gm-tile gt-opt" data-i="' + i + '">' + esc(o) + '</button>'; }).join('') + '</div>';
      } else if (t.kind === 'tap') {
        body = '<p class="gt-sent gt-taps">' + t.words.map(function (w, i) { return '<button type="button" class="gt-word" data-w="' + i + '" aria-pressed="false">' + esc(w) + '</button>'; }).join(' ') + '</p>' +
          (t.right.length > 1 ? '<div class="row"><button type="button" class="btn" id="gtCheck" disabled>Check</button></div>' : '');
      } else {
        body = '<p class="gt-sent">' + t.words.map(function (w, i) { return '<button type="button" class="gt-word" data-w="' + i + '">' + esc(w) + '</button>'; }).join(' ') + '</p>' +
          '<div class="gt-opts" hidden>' + t.opts.map(function (o) { return '<button type="button" class="gm-tile gt-opt" data-o="' + esc(o) + '">' + esc(o) + '</button>'; }).join('') + '</div>';
      }
      box.innerHTML = '<div class="gt-top"><span class="muted">' + (n + 1) + ' of ' + tasks.length + '</span><span class="dots" aria-hidden="true">' + dots + '</span></div>' +
        '<p class="gt-ask">' + esc(t.ask) + '</p>' + body + '<div class="feedback" aria-live="polite"></div>' +
        '<div class="row"><button type="button" class="btn primary" id="gtNext" hidden>' + (n + 1 < tasks.length ? 'Next' : 'See how you did') + '</button></div>';
      var fb = box.querySelector('.feedback'), next = box.querySelector('#gtNext');
      function finish(ok, full) {
        if (ok) right++;
        fb.className = 'feedback ' + (ok ? 'good' : 'bad');
        fb.innerHTML = '<p>' + (ok ? 'Right. ' : 'Not quite. ' + (full ? '<b>' + esc(full) + '</b> ' : '')) + '<span class="muted">' + esc(t.why) + '</span></p>' +
          (t.answer ? '<p class="gt-listen">' + sayBtn(t.answer, t.v, 'Listen to the sentence') + '<span>' + LINK(t.answer) + '</span></p>' : '');
        box.querySelectorAll('.gt-opt, .gt-word, #gtCheck').forEach(function (b) { b.disabled = true; });
        var s = fb.querySelector('[data-say]');
        if (s) s.addEventListener('click', function () { ctx.say(s.dataset.say, s, s.dataset.voice); });
        next.hidden = false;
        next.focus();
      }
      next.addEventListener('click', function () { n++; if (n < tasks.length) show(); else done(right, tasks.length); });
      if (t.kind === 'pick') {
        box.querySelectorAll('.gt-opt').forEach(function (b) {
          b.addEventListener('click', function () {
            var ok = b.dataset.o === t.right, g = box.querySelector('.gt-gap');
            if (g) { g.textContent = b.dataset.o; g.classList.add(ok ? 'is-right' : 'is-wrong'); }
            b.classList.add(ok ? 'is-right' : 'is-wrong');
            if (!ok) box.querySelectorAll('.gt-opt').forEach(function (o) { if (o.dataset.o === t.right) o.classList.add('is-right'); });
            finish(ok, t.answer || t.right);
          });
        });
      } else if (t.kind === 'build') {
        var built = [], sent = box.querySelector('.gt-built');
        box.querySelectorAll('.gt-opt').forEach(function (b) {
          b.addEventListener('click', function () {
            if (!built.length) sent.innerHTML = '';
            built.push(t.tiles[+b.dataset.i]);
            var r = b.getBoundingClientRect(), tile = document.createElement('span');
            tile.className = 'gm-tile gt-placed';
            tile.textContent = t.tiles[+b.dataset.i];
            sent.appendChild(tile);
            if (!reduce) {
              var r2 = tile.getBoundingClientRect();
              tile.animate([{ transform: 'translate(' + (r.left - r2.left) + 'px,' + (r.top - r2.top) + 'px)' }, { transform: 'none' }], { duration: 320, easing: 'cubic-bezier(.3,.7,.2,1)' });
            }
            b.disabled = true;
            b.classList.add('gt-used');
            if (built.length === t.tiles.length) {
              var ok = built.join(' ') === t.right.join(' ');
              sent.classList.add(ok ? 'is-right' : 'is-wrong');
              finish(ok, t.right.join(' '));
            }
          });
        });
      } else if (t.kind === 'tap') {
        var check = box.querySelector('#gtCheck');
        var judge = function () {
          var picked = [];
          box.querySelectorAll('.gt-word').forEach(function (w, i) {
            var on = w.getAttribute('aria-pressed') === 'true', want = t.right.indexOf(i) >= 0;
            if (on) picked.push(i);
            if (on && want) w.classList.add('is-right');
            else if (on) w.classList.add('is-wrong');
            else if (want) w.classList.add('is-missed');
          });
          var ok = picked.length === t.right.length && picked.every(function (i) { return t.right.indexOf(i) >= 0; });
          finish(ok, ok ? '' : t.right.map(function (i) { return t.words[i].replace(/[.,?!]$/, ''); }).join(', '));
        };
        box.querySelectorAll('.gt-word').forEach(function (w) {
          w.addEventListener('click', function () {
            w.setAttribute('aria-pressed', String(w.getAttribute('aria-pressed') !== 'true'));
            if (!check) { judge(); return; }
            check.disabled = !box.querySelector('.gt-word[aria-pressed="true"]');
          });
        });
        if (check) check.addEventListener('click', judge);
      } else {
        var opts = box.querySelector('.gt-opts');
        box.querySelectorAll('.gt-word').forEach(function (b) {
          b.addEventListener('click', function () {
            if (+b.dataset.w !== t.wrong) {
              b.classList.add('is-wrong');
              fb.className = 'feedback bad';
              fb.textContent = 'That word is fine. Look for another one.';
              return;
            }
            box.querySelectorAll('.gt-word').forEach(function (w) { w.classList.remove('is-wrong'); });
            b.classList.add('is-picked');
            fb.className = 'feedback';
            fb.textContent = 'Yes, that one. What should it be?';
            opts.hidden = false;
          });
        });
        opts.querySelectorAll('.gt-opt').forEach(function (b) {
          b.addEventListener('click', function () {
            var ok = b.dataset.o === t.right, w = box.querySelector('.gt-word.is-picked');
            w.textContent = b.dataset.o;
            w.classList.add(ok ? 'is-right' : 'is-wrong');
            finish(ok, t.answer);
          });
        });
      }
    }
    show();
  }

  // ---------- a topic page ----------
  function partTitle(no, text) { return '<h2 class="g-part-title"><span class="num">' + no + '</span>' + text + '</h2>'; }
  function lesson(el, ctx, id) {
    var n = BY[id];
    if (!n) { home(el, ctx); return; }
    useLinks(ctx);
    var les = LESSONS[id], s = stateOf(ctx, id), preview = s === 'locked';
    var states = {};
    NODES.forEach(function (m) { states[m.id] = stateOf(ctx, m.id); });
    var terms = Object.keys(n.terms || {});
    var no = 0, html = '<div class="lesson-top"><button class="btn quiet" type="button" id="gBack">← Grammar map</button></div>' +
      '<article class="g-lesson">' +
      '<header class="g-lesson-head"><p class="eyebrow">' + esc(D.bands[n.band]) + ' · topic ' + n.no + ' of ' + NODES.length + '</p>' +
      '<h1 class="g-title">' + esc(n.title) + '</h1><p class="g-lede">' + LINK(n.goal) + '</p>' +
      (n.needs.length ? '<div class="g-builds"><span class="muted">Builds on</span>' + chipList(n.needs, states) + '</div>' : '') + '</header>';
    if (preview) {
      html += '<p class="g-preview">' + ICON.locked + '<span>You are looking inside before this topic opens. First finish ' +
        missing(ctx, id).map(function (d) { return '<b>' + esc(BY[d].title) + '</b>'; }).join(' and ') + '. Your answers here are not saved.</span></p>';
    }
    if (les && les.film) html += '<section class="g-part">' + partTitle(++no, 'Watch') + '<div class="g-film" id="gFilm"></div></section>';
    html += '<section class="g-part">' + partTitle(++no, 'The rule') +
      (terms.length ? '<dl class="g-terms">' + terms.map(function (t) { return '<div><dt>' + esc(t) + '</dt><dd>' + LINK(n.terms[t]) + '</dd></div>'; }).join('') + '</dl>' : '') +
      '<ul class="g-points">' + n.points.map(function (p) { return '<li>' + LINK(p) + '</li>'; }).join('') + '</ul>';
    if (les && les.rule && les.rule.table) {
      html += '<div class="g-rule">' + les.rule.table.map(function (r) {
        var left = r[0].split(/,\s*/).map(function (w) {
          return les.machine ? '<button type="button" class="gm-chip" data-pick="' + esc(w) + '">' + esc(w) + '</button>' : '<span class="gm-chip g-chip-flat">' + esc(w) + '</span>';
        }).join('');
        return '<div class="g-rule-row"><span class="g-who">' + left + '</span><span class="g-arrow" aria-hidden="true"></span><span class="gm-tile gm-be">' + esc(r[1]) + '</span></div>';
      }).join('') + '</div>' + (les.machine ? '<p class="muted g-note">Touch a word on the left to see it in the machine below.</p>' : '');
    }
    var examples = les && les.rule && les.rule.examples ? les.rule.examples : n.examples.map(function (t) { return { t: t }; });
    html += '<h3 class="g-sub">Examples</h3><ul class="g-examples">' + examples.map(function (e) { return '<li>' + sayBtn(e.t, e.v) + '<span>' + LINK(e.t) + '</span></li>'; }).join('') + '</ul>' +
      '<p class="muted g-note g-tip">Touch any word to open its page in Basic 1000.</p></section>';
    if (les && les.machine) {
      html += '<section class="g-part">' + partTitle(++no, 'Play') +
        '<p class="muted g-note">Pick who it is about' + (les.machine.forms.length > 1 ? ', then change the sentence. Watch the words move.' : '. Watch the words change.') + '</p>' +
        '<div class="gm" id="gm"></div></section>';
    }
    if (les) html += '<section class="g-part">' + partTitle(++no, 'Try it') + '<p class="muted g-note">Get ' + passMark(id) + ' of ' + total(id) + ' right to finish this topic.</p><div class="q g-try" id="gTry"></div></section>';
    else html += '<section class="g-part g-coming"><p class="muted">The film and exercises for this topic are coming soon.</p></section>';
    html += '</article>';
    el.innerHTML = html;

    var film = null;
    var say = function (text, btn, voice) { if (film && film.pause) film.pause(); ctx.say(text, btn, voice); };
    if (les && les.film && window.BASIC_FILMS) film = BASIC_FILMS.mount(el.querySelector('#gFilm'), les.film, { link: ctx.link });
    el.querySelector('#gBack').addEventListener('click', ctx.back);
    el.querySelectorAll('.g-builds [data-go]').forEach(function (b) { b.addEventListener('click', function () { ctx.open(b.dataset.go); }); });
    el.querySelectorAll('.g-examples [data-say]').forEach(function (b) { b.addEventListener('click', function () { say(b.dataset.say, b, b.dataset.voice); }); });
    var m = les && les.machine ? machine(el.querySelector('#gm'), { say: say }, les.machine) : null;
    el.querySelectorAll('[data-pick]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (m && m.pick(b.dataset.pick)) el.querySelector('#gm').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
      });
    });
    if (!les) return;
    var tryBox = el.querySelector('#gTry');
    runTasks(tryBox, { say: say }, les.tasks, function (right, all) {
      var pass = right >= passMark(id), wasDone = isDone(ctx, id);
      if (!preview) ctx.save(id, right);
      var opened = !preview && pass && !wasDone ? KIDS[id].filter(function (k) { return LESSONS[k] && stateOf(ctx, k) === 'open'; }) : [];
      var nowStates = {};
      NODES.forEach(function (x) { nowStates[x.id] = stateOf(ctx, x.id); });
      tryBox.innerHTML = '<p class="g-done-score"><span class="score num">' + right + '/' + all + '</span></p>' +
        '<p>' + (preview ? 'This was a look inside, so it is not saved.' : pass ? (right === all ? 'All right! ' : 'Well done. ') + 'This topic is done.' : 'You need ' + passMark(id) + ' right. Look at the rule again, then try once more.') + '</p>' +
        (opened.length ? '<p class="g-opened">Now open:</p>' + chipList(opened, nowStates)
          : !preview && pass && KIDS[id].length ? '<p class="g-opened muted">Next on the map:</p>' + chipList(KIDS[id], nowStates) : '') +
        '<div class="row" style="margin-top:16px"><button type="button" class="btn" id="gAgain">Try again</button><button type="button" class="btn quiet" id="gHome">Back to the map</button></div>';
      tryBox.querySelectorAll('[data-go]').forEach(function (b) { b.addEventListener('click', function () { ctx.open(b.dataset.go); }); });
      tryBox.querySelector('#gAgain').addEventListener('click', function () { lesson(el, ctx, id); el.querySelector('#gTry').scrollIntoView({ block: 'start' }); });
      tryBox.querySelector('#gHome').addEventListener('click', ctx.back);
    });
  }

  return { home: home, lesson: lesson, nodes: NODES, lessons: LESSONS, stateOf: stateOf, passMark: passMark };
})();
