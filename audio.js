// Basic 1000 audio: plays a word or sentence in a woman's or man's voice.
// Clips are made once by the "tts" Supabase function (Kokoro-82M, open source) and kept in the
// public "audio" bucket. The clip address is computed here from the text, so stored clips play
// straight away with no server call. Order: stored clip -> ask the function -> browser voice.
// Every clip starts and ends with a little silence, so the first word is not swallowed.
(function () {
  'use strict';
  var BASE = 'https://duptugctgzemfczbtvgj.supabase.co';
  var CLIPS = BASE + '/storage/v1/object/public/audio/';
  var FN = BASE + '/functions/v1/tts';
  // must match VOICES, CHOICES and VERSION in supabase/functions/tts/index.ts
  var VOICES = { woman: 'af_heart', man: 'am_michael' };
  // test version: three voices for each speaker, one button each, to pick the nicest
  var CHOICES = { woman: ['af_heart', 'af_bella', 'bf_emma'], man: ['am_michael', 'am_fenrir', 'bm_george'] };
  var NAMES = { af_heart: 'Heart', af_bella: 'Bella', bf_emma: 'Emma', am_michael: 'Michael', am_fenrir: 'Fenrir', bm_george: 'George' };
  var VERSION = 'v2';

  var MALE = 'man|boy|father|brother|son|husband';
  var FEMALE = 'woman|girl|mother|sister|daughter|wife';
  var IS_MAN = new RegExp('\\bi am an? (' + MALE + ')\\b|\\bi am not an? (' + FEMALE + ')\\b');
  var IS_WOMAN = new RegExp('\\bi am an? (' + FEMALE + ')\\b|\\bi am not an? (' + MALE + ')\\b');
  // the speaker must fit the sentence: "I am a woman." is read by the woman
  function voiceFor(text, fallback) {
    var t = String(text).toLowerCase();
    if (IS_MAN.test(t)) return 'man';
    if (IS_WOMAN.test(t)) return 'woman';
    return fallback || 'woman';
  }
  function norm(t) { return String(t).replace(/\s+/g, ' ').trim(); }

  function sha256(s) {
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    });
  }
  // voiceId: one Kokoro voice from CHOICES; when missing, the speaker's main voice
  function clipUrl(text, voice, voiceId) {
    var v = voiceId || VOICES[voice] || VOICES.woman;
    return sha256(v + '|' + norm(text)).then(function (h) { return CLIPS + VERSION + '/' + v + '/' + h.slice(0, 32) + '.mp3'; });
  }

  var player = null, playing = null;
  function stop() {
    if (player) { player.pause(); player = null; }
    if (window.speechSynthesis) speechSynthesis.cancel();
    if (playing) { playing.classList.remove('playing'); playing = null; }
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
  function askServer(text, voice, voiceId) {
    return fetch(FN + '?text=' + encodeURIComponent(norm(text)) + '&voice=' + voice + (voiceId ? '&voiceId=' + voiceId : ''))
      .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error(r.status)); })
      .then(function (j) { if (!j.url) throw new Error('no url'); return j.url; });
  }

  function say(text, voice, btn, voiceId) {
    var again = btn && btn === playing;
    stop();
    if (again) return Promise.resolve(); // a second tap stops it
    voice = VOICES[voice] ? voice : 'woman';
    if (voiceId && CHOICES[voice].indexOf(voiceId) < 0) voiceId = '';
    if (btn) { btn.classList.add('playing'); playing = btn; }
    var done = function () { if (btn && playing === btn) { btn.classList.remove('playing'); playing = null; } };
    return clipUrl(text, voice, voiceId)
      .then(playUrl)
      .catch(function () { return askServer(text, voice, voiceId).then(playUrl); })
      .catch(function () { return browserVoice(norm(text), voice); })
      .then(done, done);
  }

  // speaker buttons, one per trial voice, each labelled with the voice's name;
  // the page wires every [data-say] button through one click listener
  function button(text, voice, label) {
    var esc = function (x) { return String(x).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); };
    voice = CHOICES[voice] ? voice : 'woman';
    var icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/>' +
      '<path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
    return '<span class="says">' + CHOICES[voice].map(function (id) {
      return '<button class="say" type="button" data-say="' + esc(text) + '" data-voice="' + voice + '" data-vid="' + id +
        '" aria-label="' + esc((label || 'Listen') + ', ' + NAMES[id] + '’s voice') + '">' + icon + '<span>' + NAMES[id] + '</span></button>';
    }).join('') + '</span>';
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-say]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    say(b.dataset.say, b.dataset.voice, b, b.dataset.vid);
  });

  window.BASIC_AUDIO = { say: say, stop: stop, voiceFor: voiceFor, clipUrl: clipUrl, button: button, VOICES: VOICES, CHOICES: CHOICES, NAMES: NAMES };
})();
