// Basic 1000 grammar: how the words fit together. Each topic uses only words the learner already has.
// A topic is one page in three parts: see it (the sentence machine), the rule, and try it (exercises).
// Public API: BASIC_GRAMMAR.home(container, ctx), BASIC_GRAMMAR.lesson(container, ctx, topicId)
//   ctx = { say(text, button), result(id) -> best score or undefined, save(id, score), open(id), back(), maxStep }
var BASIC_GRAMMAR = (function () {
  'use strict';
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // The topics in learning order. Only "be" is written so far; the others show when they will come.
  var TOPICS = [
    { id: 'be', title: 'Am, is, are', what: 'Say who someone is, and what something is.' },
    { id: 'not', title: 'Not', what: 'Say that something is not so.' },
    { id: 'questions', title: 'Is it? Are you?', what: 'Ask about someone or something.' },
    { id: 'have', title: 'Have and has', what: 'Say what someone has.' },
    { id: 'an', title: 'A and an', what: 'Which one to use before a word.' },
    { id: 'plural', title: 'One cat, two cats', what: 'Talk about more than one.' },
    { id: 'this', title: 'This, that, these, those', what: 'Point to things near and far.' },
    { id: 'the', title: 'A or the', what: 'A new thing, or one we already know.' }
  ];

  // ---------- the sentence machine ----------
  // One sentence as tiles. Pick who it is about; make it plain, "not", or a question.
  // The tiles keep their identity, so when the form changes they glide to their new places:
  // in a question, the "be" tile jumps to the front.
  var PEOPLE = [
    { s: 'I', be: 'am', rest: 'a man' },
    { s: 'you', be: 'are', rest: 'a woman' },
    { s: 'he', be: 'is', rest: 'a boy' },
    { s: 'she', be: 'is', rest: 'a girl' },
    { s: 'it', be: 'is', rest: 'a dog' },
    { s: 'we', be: 'are', rest: 'children' },
    { s: 'they', be: 'are', rest: 'cats' }
  ];
  var cap = function (w) { return w.charAt(0).toUpperCase() + w.slice(1); };
  var subj = function (w, first) { return w === 'I' ? 'I' : first ? cap(w) : w; };

  function machineTiles(p, form) {
    if (form === 'question') {
      return [['be', cap(p.be)], ['s', subj(p.s, false)], ['rest', p.rest + '?']];
    }
    var t = [['s', subj(p.s, true)], ['be', p.be]];
    if (form === 'not') t.push(['not', 'not']);
    return t.concat([['rest', p.rest + '.']]); // the full stop rides on the last tile, so it never wraps alone
  }
  function sentence(tiles) {
    return tiles.map(function (t) { return t[1]; }).join(' ');
  }
  function answer(p, form) {
    if (form !== 'question') return '';
    var s = p.s === 'I' ? 'you' : p.s === 'you' ? 'I' : p.s;
    var be = s === 'I' ? 'am' : s === 'you' || s === 'we' || s === 'they' ? 'are' : 'is';
    return 'Yes, ' + subj(s, false) + ' ' + be + '. &nbsp; No, ' + subj(s, false) + ' ' + be + ' not.';
  }

  // move tiles to their new order with a FLIP animation (first, last, invert, play)
  function flip(line, tiles, onBeChange) {
    var old = {};
    Array.prototype.forEach.call(line.children, function (el) { old[el.dataset.k] = { el: el, r: el.getBoundingClientRect(), text: el.textContent }; });
    var keep = {};
    tiles.forEach(function (t) {
      var el = old[t[0]] ? old[t[0]].el : null;
      if (!el) {
        el = document.createElement('span');
        el.className = 'gm-tile gm-' + t[0];
        el.dataset.k = t[0];
        el.dataset.enter = '1';
      }
      if (el.textContent !== t[1]) {
        el.textContent = t[1];
        if (t[0] === 'be' && old.be && onBeChange) el.dataset.swap = '1';
      }
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
      // the word that moves to the front of a question takes a little hop on its way
      if (el.dataset.k === 'be' && Math.abs(dx) > 20) {
        frames = [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'translate(' + dx / 2 + 'px,' + (dy / 2 - 28) + 'px)', offset: 0.5 }, { transform: 'none' }];
      }
      if (dx || dy) el.animate(frames, { duration: 520, easing: 'cubic-bezier(.3,.7,.2,1)' });
      if (el.dataset.swap) {
        el.animate([{ transform: 'rotateX(90deg)' }, { transform: 'none' }], { duration: 300, easing: 'ease-out' });
        delete el.dataset.swap;
      }
    });
  }

  function machine(box, ctx) {
    var state = { p: 3, form: 'plain' };
    box.innerHTML =
      '<div class="gm-who" role="group" aria-label="Who is it about?">' +
      PEOPLE.map(function (p, i) { return '<button type="button" class="gm-chip" data-p="' + i + '" aria-pressed="false">' + esc(subj(p.s, true)) + '</button>'; }).join('') +
      '</div>' +
      '<div class="gm-stage"><div class="gm-line" aria-live="polite"></div>' +
      '<button type="button" class="say gm-say" aria-label="Listen to the sentence" title="Listen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></div>' +
      '<p class="gm-answer muted"></p>' +
      '<div class="gm-forms" role="group" aria-label="Make it">' +
      [['plain', 'Say it'], ['not', 'Say it with not'], ['question', 'Ask it']].map(function (f) {
        return '<button type="button" class="gm-form" data-f="' + f[0] + '" aria-pressed="false">' + f[1] + '</button>';
      }).join('') + '</div>';
    var line = box.querySelector('.gm-line');
    function draw(first) {
      var p = PEOPLE[state.p], tiles = machineTiles(p, state.form);
      if (first) {
        line.innerHTML = tiles.map(function (t) { return '<span class="gm-tile gm-' + t[0] + '" data-k="' + t[0] + '">' + esc(t[1]) + '</span>'; }).join('');
      } else flip(line, tiles, true);
      box.querySelector('.gm-answer').innerHTML = answer(p, state.form);
      box.querySelectorAll('[data-p]').forEach(function (b) { b.setAttribute('aria-pressed', String(+b.dataset.p === state.p)); });
      box.querySelectorAll('[data-f]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.f === state.form)); });
      box.dataset.sentence = sentence(tiles);
    }
    box.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      if (b.dataset.p != null) { state.p = +b.dataset.p; draw(); }
      else if (b.dataset.f) { state.form = b.dataset.f; draw(); }
      else if (b.classList.contains('gm-say')) ctx.say(box.dataset.sentence, b);
    });
    draw(true);
    return { pick: function (word) { var i = PEOPLE.findIndex(function (p) { return p.s.toLowerCase() === word.toLowerCase(); }); if (i >= 0) { state.p = i; draw(); } } };
  }

  // ---------- try it ----------
  // kinds: pick (choose the word for the gap), build (tap the tiles in order), fix (tap the wrong word, then pick)
  var TASKS = [
    { kind: 'pick', ask: 'Fill the gap.', before: 'He', after: 'a boy.', opts: ['am', 'is', 'are'], right: 'is', why: 'he, she, it → is' },
    { kind: 'pick', ask: 'Fill the gap.', before: 'We', after: 'children.', opts: ['am', 'is', 'are'], right: 'are', why: 'you, we, they → are' },
    { kind: 'build', ask: 'Put the words in order.', tiles: ['are', 'dogs.', 'They'], right: ['They', 'are', 'dogs.'], why: 'they → are, and it comes after they.' },
    { kind: 'fix', ask: 'One word is wrong. Tap it.', words: ['You', 'is', 'a', 'woman.'], wrong: 1, opts: ['am', 'is', 'are'], right: 'are', why: 'you → are, always, even for one person.' },
    { kind: 'build', ask: 'Say it with not: "It is a cat."', tiles: ['not', 'a cat.', 'It', 'is'], right: ['It', 'is', 'not', 'a cat.'], why: '"not" comes right after am, is or are.' },
    { kind: 'build', ask: 'Ask it: "She is a child."', tiles: ['she', 'a child?', 'Is'], right: ['Is', 'she', 'a child?'], why: 'To ask, is comes first.' }
  ];

  function shuffleFixed(a) { return a.slice(); } // tiles are listed already mixed, so every learner sees the same task

  function runTasks(box, ctx, done) {
    var n = 0, right = 0;
    function show() {
      var t = TASKS[n];
      var dots = TASKS.map(function (_, i) { return '<i class="' + (i < n ? 'on' : i === n ? 'cur' : '') + '"></i>'; }).join('');
      var body;
      if (t.kind === 'pick') {
        body = '<p class="gt-sent">' + esc(t.before) + ' <span class="gt-gap">&nbsp;</span> ' + esc(t.after) + '</p>' +
          '<div class="gt-opts">' + t.opts.map(function (o) { return '<button type="button" class="gm-tile gt-opt" data-o="' + esc(o) + '">' + esc(o) + '</button>'; }).join('') + '</div>';
      } else if (t.kind === 'build') {
        body = '<p class="gt-sent gt-built" aria-live="polite"><span class="muted gt-hint">Tap the words below.</span></p>' +
          '<div class="gt-opts">' + shuffleFixed(t.tiles).map(function (o, i) { return '<button type="button" class="gm-tile gt-opt" data-i="' + i + '">' + esc(o) + '</button>'; }).join('') + '</div>';
      } else {
        body = '<p class="gt-sent">' + t.words.map(function (w, i) { return '<button type="button" class="gt-word" data-w="' + i + '">' + esc(w) + '</button>'; }).join(' ') + '</p>' +
          '<div class="gt-opts" hidden>' + t.opts.map(function (o) { return '<button type="button" class="gm-tile gt-opt" data-o="' + esc(o) + '">' + esc(o) + '</button>'; }).join('') + '</div>';
      }
      box.innerHTML = '<div class="gt-top"><span class="muted">' + (n + 1) + ' of ' + TASKS.length + '</span><span class="dots" aria-hidden="true">' + dots + '</span></div>' +
        '<p class="gt-ask">' + esc(t.ask) + '</p>' + body + '<p class="feedback" aria-live="polite"></p>' +
        '<div class="row"><button type="button" class="btn primary" id="gtNext" hidden>' + (n + 1 < TASKS.length ? 'Next' : 'See how you did') + '</button></div>';
      var fb = box.querySelector('.feedback'), next = box.querySelector('#gtNext');
      function finish(ok, full) {
        if (ok) right++;
        fb.className = 'feedback ' + (ok ? 'good' : 'bad');
        fb.innerHTML = (ok ? 'Right. ' : 'Not quite. <b>' + esc(full) + '</b> ') + '<span class="muted">' + esc(t.why) + '</span>';
        box.querySelectorAll('.gt-opt, .gt-word').forEach(function (b) { b.disabled = true; });
        next.hidden = false;
        next.focus();
      }
      next.addEventListener('click', function () { n++; if (n < TASKS.length) show(); else done(right, TASKS.length); });
      if (t.kind === 'pick') {
        box.querySelectorAll('.gt-opt').forEach(function (b) {
          b.addEventListener('click', function () {
            var ok = b.dataset.o === t.right;
            box.querySelector('.gt-gap').textContent = b.dataset.o;
            box.querySelector('.gt-gap').classList.add(ok ? 'is-right' : 'is-wrong');
            finish(ok, t.before + ' ' + t.right + ' ' + t.after);
          });
        });
      } else if (t.kind === 'build') {
        var built = [], sent = box.querySelector('.gt-built');
        box.querySelectorAll('.gt-opt').forEach(function (b) {
          b.addEventListener('click', function () {
            if (!built.length) sent.innerHTML = '';
            built.push(t.tiles[+b.dataset.i]);
            var r = b.getBoundingClientRect();
            var tile = document.createElement('span');
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
            b.classList.add('is-picked');
            fb.className = 'feedback';
            fb.textContent = 'Yes, that one. What should it be?';
            opts.hidden = false;
          });
        });
        opts.querySelectorAll('.gt-opt').forEach(function (b) {
          b.addEventListener('click', function () {
            var ok = b.dataset.o === t.right;
            var w = box.querySelector('.gt-word.is-picked');
            w.textContent = b.dataset.o;
            w.classList.add(ok ? 'is-right' : 'is-wrong');
            var full = t.words.slice(); full[t.wrong] = t.right;
            finish(ok, full.join(' '));
          });
        });
      }
    }
    show();
  }

  // ---------- pages ----------
  function home(el, ctx) {
    var first = TOPICS[0];
    el.innerHTML = '<section class="g-head"><h1 class="g-title">Grammar</h1>' +
      '<p class="g-lede">How the words you know fit together. Every example uses only words you have already learned.</p></section>' +
      '<ol class="g-contents">' + TOPICS.map(function (t, i) {
        var ready = t.id === first.id, best = ctx.result(t.id);
        return '<li class="g-topic' + (ready ? ' ready' : '') + '">' +
          '<span class="g-no num">' + (i + 1) + '</span>' +
          '<span class="g-name"><b>' + esc(t.title) + '</b><span class="muted">' + esc(t.what) + '</span></span>' +
          (ready
            ? '<button type="button" class="btn ' + (best == null ? 'primary' : '') + '" data-topic="' + t.id + '">' + (best == null ? 'Start' : 'Again') + '</button>' +
              (best != null ? '<span class="g-best num">' + best + '/' + TASKS.length + '</span>' : '')
            : '<span class="g-soon muted">Coming soon</span>') +
          '</li>';
      }).join('') + '</ol>';
    el.querySelectorAll('[data-topic]').forEach(function (b) { b.addEventListener('click', function () { ctx.open(b.dataset.topic); }); });
  }

  function lesson(el, ctx, id) {
    el.innerHTML = '<div class="lesson-top"><button class="btn quiet" type="button" id="gBack">← Grammar</button></div>' +
      '<article class="g-lesson">' +
      '<header><h1 class="g-title">Am, is, are</h1><p class="g-lede">Use them to say who someone is, or what something is.</p></header>' +
      '<section class="g-part"><h2 class="g-part-title"><span class="num">1</span>See it</h2>' +
      '<p class="muted g-note">Pick who it is about, then say it, say it with <i>not</i>, or ask it. Watch the words move.</p>' +
      '<div class="gm" id="gm"></div></section>' +
      '<section class="g-part"><h2 class="g-part-title"><span class="num">2</span>The rule</h2>' +
      '<div class="g-rule">' +
      [['I', 'am'], ['he she it', 'is'], ['you we they', 'are']].map(function (r) {
        return '<div class="g-rule-row"><span class="g-who">' + r[0].split(' ').map(function (w) { return '<button type="button" class="gm-chip" data-pick="' + w + '">' + esc(w) + '</button>'; }).join('') +
          '</span><span class="g-arrow" aria-hidden="true"></span><span class="gm-tile gm-be">' + r[1] + '</span></div>';
      }).join('') + '</div>' +
      '<p class="muted g-note">Tap a word on the left to see it in the machine above.</p></section>' +
      '<section class="g-part"><h2 class="g-part-title"><span class="num">3</span>Try it</h2><div class="q g-try" id="gTry"></div></section>' +
      '</article>';
    var m = machine(el.querySelector('#gm'), ctx);
    el.querySelector('#gBack').addEventListener('click', ctx.back);
    el.querySelectorAll('[data-pick]').forEach(function (b) {
      b.addEventListener('click', function () {
        m.pick(b.dataset.pick);
        el.querySelector('#gm').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
      });
    });
    var tryBox = el.querySelector('#gTry');
    runTasks(tryBox, ctx, function (right, total) {
      ctx.save(id, right);
      tryBox.innerHTML = '<p class="g-done-score"><span class="score num">' + right + '/' + total + '</span></p>' +
        '<p>' + (right === total ? 'All right. You can now say who someone is and what something is, say it with not, and ask about it.'
          : 'Look at the rule again, then try once more.') + '</p>' +
        '<div class="row" style="margin-top:14px"><button type="button" class="btn" id="gAgain">Try again</button><button type="button" class="btn quiet" id="gHome">Back to grammar</button></div>';
      tryBox.querySelector('#gAgain').addEventListener('click', function () { lesson(el, ctx, id); el.querySelector('#gTry').scrollIntoView({ block: 'start' }); });
      tryBox.querySelector('#gHome').addEventListener('click', ctx.back);
    });
  }

  return { home: home, lesson: lesson, topics: TOPICS, tasks: TASKS.length };
})();
