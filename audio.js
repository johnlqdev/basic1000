// Basic 1000 audio: plays a word or sentence in a woman's or man's voice.
// Clips are made once by the "tts" Supabase function (Kokoro-82M, open source) and kept in the
// public "audio" bucket. The clip address is computed here from the text, so stored clips play
// straight away with no server call. Order: stored clip -> ask the function -> browser voice.
(function () {
  'use strict';
  var BASE = 'https://duptugctgzemfczbtvgj.supabase.co';
  var CLIPS = BASE + '/storage/v1/object/public/audio/';
  var FN = BASE + '/functions/v1/tts';
  // must match VOICES in supabase/functions/tts/index.ts
  var VOICES = { woman: 'af_heart', man: 'am_michael' };

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
  function clipUrl(text, voice) {
    var v = VOICES[voice] || VOICES.woman;
    return sha256(v + '|' + norm(text)).then(function (h) { return CLIPS + v + '/' + h.slice(0, 32) + '.mp3'; });
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
  function askServer(text, voice) {
    return fetch(FN + '?text=' + encodeURIComponent(norm(text)) + '&voice=' + voice)
      .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error(r.status)); })
      .then(function (j) { if (!j.url) throw new Error('no url'); return j.url; });
  }

  function say(text, voice, btn) {
    var again = btn && btn === playing;
    stop();
    if (again) return Promise.resolve(); // a second tap stops it
    voice = VOICES[voice] ? voice : 'woman';
    if (btn) { btn.classList.add('playing'); playing = btn; }
    var done = function () { if (btn && playing === btn) { btn.classList.remove('playing'); playing = null; } };
    return clipUrl(text, voice)
      .then(playUrl)
      .catch(function () { return askServer(text, voice).then(playUrl); })
      .catch(function () { return browserVoice(norm(text), voice); })
      .then(done, done);
  }

  // a small speaker button; the page wires every [data-say] button through one click listener
  function button(text, voice, label) {
    var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); };
    return '<button class="say" type="button" data-say="' + esc(text) + '" data-voice="' + voice + '" aria-label="' +
      esc(label || 'Listen') + '" title="' + (voice === 'man' ? 'Man’s voice' : 'Woman’s voice') + '">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor"/>' +
      '<path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>';
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-say]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    say(b.dataset.say, b.dataset.voice, b);
  });

  window.BASIC_AUDIO = { say: say, stop: stop, voiceFor: voiceFor, clipUrl: clipUrl, button: button, VOICES: VOICES };
})();
