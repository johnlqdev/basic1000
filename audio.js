// Basic 1000 audio: one speaker button for each word and example sentence.
// Voices (Qwen3-TTS, American English): Daniel reads every word and every sentence anyone could say;
// Sarah reads sentences that only a woman can say ("I am a woman.").
// Clips are made once by the "tts" Supabase function (Qwen3-TTS on a RunPod GPU) and kept in the
// public "audio" bucket. The clip address is computed here from the text, so stored clips play
// straight away with no server call. Order: stored clip -> ask the function -> browser voice.
// Every clip starts and ends with a little silence, so the first word is not swallowed.
//
// Slow buttons (every step): a slower clip (words at 60 % speed, sentences at 70 %,
// pitch unchanged) with a timing file made by the same function. While it plays, the sound being
// heard is highlighted: in a word, its letters and IPA (sound groups from pron.js); in a sentence,
// the word being read. Both files sit next to the normal clip: slow1/{voice}/{same name}.mp3 / .json.
(function () {
  'use strict';
  var BASE = 'https://duptugctgzemfczbtvgj.supabase.co';
  var CLIPS = BASE + '/storage/v1/object/public/audio/';
  var FN = BASE + '/functions/v1/tts';
  // must match VOICES and VERSION in supabase/functions/tts/index.ts
  var VOICES = { man: 'us_daniel', woman: 'us_sarah' };
  var NAMES = { us_daniel: 'Daniel', us_sarah: 'Sarah' };
  var VERSION = 'v2';
  var MAX_STEP = 200; // steps that have clips (all of them)
  // Clips are cached for a year. When clips are made again in place (same name), raise FRESH so that
  // browsers fetch the new ones. r=2: 2026-10-14, words and sentences that end in k/p/t/d/f/th made again.
  // r=3: 2026-10-16, grammar lines with "am" (and two others) made again.
  var FRESH = '?r=3';
  var SLOW_VERSION = 'slow1'; // must match SLOW_VERSION in the tts function
  var SLOW_MAX_STEP = 200; // steps that have slow clips (all of them)
  var WORD_RE = /[A-Za-z']+/g; // how sentences are split into words (same as the voice server)

  var MALE = 'man|boy|father|brother|son|husband';
  var FEMALE = 'woman|girl|mother|sister|daughter|wife';
  var IS_MAN = new RegExp('\\bi am an? (' + MALE + ')\\b|\\bi am not an? (' + FEMALE + ')\\b');
  var IS_WOMAN = new RegExp('\\bi am an? (' + FEMALE + ')\\b|\\bi am not an? (' + MALE + ')\\b');
  // who must say this text: 'man', 'woman', or '' when anyone can
  function lockFor(text) {
    var t = String(text).toLowerCase();
    return IS_MAN.test(t) ? 'man' : IS_WOMAN.test(t) ? 'woman' : '';
  }
  // Sarah only when the sentence needs a woman; Daniel for everything else
  function voiceFor(text) { return lockFor(text) === 'woman' ? 'woman' : 'man'; }
  function norm(t) { return String(t).replace(/\s+/g, ' ').trim(); }

  function sha256(s) {
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    });
  }
  function clipUrl(text, voice) {
    var v = VOICES[voice] || VOICES.man;
    return sha256(v + '|' + norm(text)).then(function (h) { return CLIPS + VERSION + '/' + v + '/' + h.slice(0, 32) + '.mp3' + FRESH; });
  }

  function slowUrls(text, voice) {
    var v = VOICES[voice] || VOICES.man;
    return sha256(v + '|' + norm(text)).then(function (h) {
      var base = CLIPS + SLOW_VERSION + '/' + v + '/' + h.slice(0, 32);
      return { mp3: base + '.mp3' + FRESH, json: base + '.json' + FRESH };
    });
  }

  var player = null, playing = null, unhighlight = null;
  function stop() {
    if (player) { player.pause(); player = null; }
    if (window.speechSynthesis) speechSynthesis.cancel();
    if (playing) { playing.classList.remove('playing'); playing = null; }
    if (unhighlight) { unhighlight(); unhighlight = null; }
  }
  function playUrl(url) {
    return new Promise(function (ok, fail) {
      var a = new Audio(url);
      player = a;
      a.onended = function () { ok(); };
      a.onerror = function () { fail(new Error('no clip')); };
      a.play().catch(fail);
    });
  }
  function browserVoice(text, voice) {
    return new Promise(function (ok) {
      if (!window.speechSynthesis) return ok();
      var u = new SpeechSynthesisUtterance(text);
      u.lang = 'en-US'; u.rate = 0.9;
      var en = speechSynthesis.getVoices().filter(function (v) { return /^en/i.test(v.lang); });
      var want = voice === 'man' ? /male|man|david|daniel|alex|fred|guy|george/i : /female|woman|zira|samantha|karen|victoria|susan|jenny|aria/i;
      var pick = en.filter(function (v) { return want.test(v.name) && !(voice === 'man' && /female/i.test(v.name)); })[0] || en[0];
      if (pick) u.voice = pick;
      u.onend = u.onerror = function () { ok(); };
      speechSynthesis.speak(u);
    });
  }
  function askServer(text, voice) {
    return fetch(FN + '?text=' + encodeURIComponent(norm(text)) + '&voice=' + voice)
      .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error(r.status)); })
      .then(function (j) { if (!j.url) throw new Error('no url'); return j.url; });
  }

  // voice: 'man' (Daniel) or 'woman' (Sarah); left out, it follows voiceFor()
  function say(text, btn, voice) {
    var again = btn && btn === playing;
    stop();
    if (again) return Promise.resolve(); // a second tap stops it
    voice = voice === 'woman' || voice === 'man' ? voice : voiceFor(text);
    if (btn) { btn.classList.add('playing'); playing = btn; }
    var done = function () { if (btn && playing === btn) { btn.classList.remove('playing'); playing = null; } };
    return clipUrl(text, voice)
      .then(playUrl)
      .catch(function () { return askServer(text, voice).then(playUrl); })
      .catch(function () { return browserVoice(norm(text), voice); })
      .then(done, done);
  }

  // ---------- slow, with highlighting ----------
  // [start, end] seconds for each highlight group. Words: groups of letters (pron.js); sentences: one group
  // per word. The aligner marks the moment each letter is heard; a group lasts until the next one starts.
  // The first group starts when the voice starts and the last one ends when it stops (timing.speech).
  function groupTimes(timing, groups) {
    var word = timing.kind === 'word', spans;
    if (word) {
      var L = timing.letters || [], k = 0;
      spans = groups.map(function (g) {
        var s = null, e = null;
        for (var n = 0; n < g; n++, k++) {
          var t = L[k];
          if (t && t[0] != null) { if (s === null || t[0] < s) s = t[0]; if (e === null || t[1] > e) e = t[1]; }
        }
        return [s, e];
      });
    } else spans = (timing.words || []).map(function (t) { return t && t[0] != null ? [t[0], t[1]] : [null, null]; });
    var known = [];
    spans.forEach(function (sp, i) { if (sp[0] != null) known.push(i); });
    if (!known.length) return spans;
    // The aligner marks one moment inside each sound, so a boundary goes halfway between two marks,
    // except across a pause between words. The voice's own start and end bound the first and last group.
    var sp0 = timing.speech, u = known.map(function (i) { return spans[i]; }), n = u.length;
    var st = new Array(n), en = new Array(n);
    st[0] = sp0 && sp0[0] < u[0][0] ? sp0[0] : u[0][0] - 0.08;
    en[n - 1] = sp0 && sp0[1] > u[n - 1][1] ? sp0[1] + 0.06 : u[n - 1][1] + 0.15;
    for (var i = 0; i + 1 < n; i++) {
      if (!word && u[i + 1][0] - u[i][1] > 0.35) { en[i] = u[i][1] + 0.15; st[i + 1] = u[i + 1][0] - 0.08; }
      else en[i] = st[i + 1] = (u[i][1] + u[i + 1][0]) / 2;
    }
    // every group stays lit long enough to see (borrowing time from a longer neighbour)
    var MIN = word ? 0.1 : 0.12;
    for (var pass = 0; pass < 4; pass++) {
      for (i = 0; i < n; i++) {
        var need = MIN - (en[i] - st[i]);
        if (need <= 0) continue;
        if (i + 1 < n && en[i] === st[i + 1] && en[i + 1] - st[i + 1] - need >= MIN) { en[i] += need; st[i + 1] += need; }
        else if (i > 0 && st[i] === en[i - 1] && en[i - 1] - st[i - 1] - need >= MIN) { st[i] -= need; en[i - 1] -= need; }
      }
    }
    known.forEach(function (k, j) { spans[k] = [Math.max(0, st[j]), en[j]]; });
    return spans;
  }
  // the elements to light for each group: [data-c="k"] (word) or [data-t="k"] (sentence) inside the box
  function targets(box, kind, n) {
    var out = [];
    for (var k = 0; k < n; k++) out.push(box ? box.querySelectorAll(kind === 'word' ? '[data-c="' + k + '"]' : '[data-t="' + k + '"]') : []);
    return out;
  }
  function playHighlighted(urls, kind, box) {
    return fetch(urls.json).then(function (r) { return r.ok ? r.json() : Promise.reject(new Error('no timing')); }).then(function (timing) {
      var groups = null;
      if (kind === 'word') {
        groups = box ? Array.prototype.map.call(box.querySelectorAll('.headword [data-c]'), function (el) { return el.textContent.length; }) : [];
        if (!groups.length) groups = (timing.letters || []).map(function () { return 1; });
      }
      var spans = groupTimes(timing, groups);
      var els = targets(box, kind, spans.length), lit = -1;
      var light = function (k) {
        if (k === lit) return;
        if (lit >= 0) Array.prototype.forEach.call(els[lit], function (e) { e.classList.remove('hl'); });
        if (k >= 0) Array.prototype.forEach.call(els[k], function (e) { e.classList.add('hl'); });
        lit = k;
      };
      return new Promise(function (ok, fail) {
        var a = new Audio(urls.mp3), raf = 0;
        player = a;
        var tick = function () {
          var t = a.currentTime, k = -1;
          for (var i = 0; i < spans.length; i++) if (spans[i][0] != null && t >= spans[i][0] && t < spans[i][1]) { k = i; break; }
          light(k);
          raf = requestAnimationFrame(tick);
        };
        unhighlight = function () { cancelAnimationFrame(raf); light(-1); };
        a.onplaying = function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(tick); };
        a.onended = function () { if (unhighlight) { unhighlight(); unhighlight = null; } ok(); };
        a.onerror = function () { if (unhighlight) { unhighlight(); unhighlight = null; } fail(new Error('no clip')); };
        a.play().catch(fail);
      });
    });
  }
  // the normal clip played slower by the browser, without highlighting (if the slow clip is missing)
  function playSlowFallback(text, voice, rate) {
    return clipUrl(text, voice).then(function (url) {
      return new Promise(function (ok, fail) {
        var a = new Audio(url);
        player = a;
        a.preservesPitch = a.mozPreservesPitch = a.webkitPreservesPitch = true;
        a.playbackRate = rate;
        a.onended = function () { ok(); };
        a.onerror = function () { fail(new Error('no clip')); };
        a.play().catch(fail);
      });
    });
  }
  function saySlow(text, kind, btn) {
    var again = btn && btn === playing;
    stop();
    if (again) return Promise.resolve();
    var voice = voiceFor(text), box = btn && btn.closest('[data-hl]');
    if (btn) { btn.classList.add('playing'); playing = btn; }
    var done = function () { if (btn && playing === btn) { btn.classList.remove('playing'); playing = null; } };
    return slowUrls(text, voice)
      .then(function (urls) { return playHighlighted(urls, kind, box); })
      .catch(function () { return playSlowFallback(text, voice, kind === 'word' ? 0.6 : 0.7); })
      .catch(function () { return browserVoice(norm(text), voice); })
      .then(done, done);
  }

  var esc = function (x) { return String(x).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); };
  var ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/>' +
    '<path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  // one round speaker button; the page wires every [data-say] button through one click listener
  function button(text, label) {
    var who = NAMES[VOICES[voiceFor(text)]];
    return '<button class="say" type="button" data-say="' + esc(text) + '" aria-label="' + esc((label || 'Listen') + ' (' + who + ')') +
      '" title="' + who + '">' + ICON + '</button>';
  }
  // a tortoise: the slow button (kind 'word' or 'sentence'); it highlights inside its closest [data-hl] box
  var SLOW_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true">' +
    '<path d="M1.5 16.5C1.5 5 17.5 5 17.5 16.5Z" fill="currentColor"/>' +
    '<path d="M16.5 15.2h2.2" stroke="currentColor" stroke-width="2.2"/><circle cx="20.5" cy="14.3" r="2.5" fill="currentColor"/>' +
    '<path d="M5 16.5v3.2M14 16.5v3.2" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>' +
    '<path class="shell" d="M4.5 13.2q5 -2.6 10 0" fill="none" stroke-width="1.3" stroke-linecap="round"/></svg>';
  function slowButton(text, kind, label) {
    var who = NAMES[VOICES[voiceFor(text)]];
    return '<button class="say slow" type="button" data-slow="' + esc(text) + '" data-kind="' + kind + '" aria-label="' +
      esc((label || 'Listen slowly') + ' (' + who + ')') + '" title="Slowly, with highlighting">' + SLOW_ICON + '</button>';
  }
  // a sentence as HTML with every word in its own span (data-t = word number), for the slow button
  function tokens(text) {
    var out = '', pos = 0, n = 0, m;
    WORD_RE.lastIndex = 0;
    while ((m = WORD_RE.exec(text))) {
      out += esc(text.slice(pos, m.index)) + '<span class="tk" data-t="' + (n++) + '">' + esc(m[0]) + '</span>';
      pos = m.index + m[0].length;
    }
    return out + esc(text.slice(pos));
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-say],[data-slow]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    if (b.dataset.slow != null) saySlow(b.dataset.slow, b.dataset.kind, b);
    else say(b.dataset.say, b);
  });

  window.BASIC_AUDIO = { say: say, saySlow: saySlow, stop: stop, voiceFor: voiceFor, lockFor: lockFor, clipUrl: clipUrl,
    slowUrls: slowUrls, button: button, slowButton: slowButton, tokens: tokens, groupTimes: groupTimes,
    VOICES: VOICES, MAX_STEP: MAX_STEP, SLOW_MAX_STEP: SLOW_MAX_STEP };
})();
