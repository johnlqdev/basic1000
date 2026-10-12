// Basic 1000 audio: one speaker button for each word and example sentence.
// Voices (Qwen3-TTS, American English): Daniel reads every word and every sentence anyone could say;
// Sarah reads sentences that only a woman can say ("I am a woman.").
// Clips are made once by the "tts" Supabase function (Qwen3-TTS on a RunPod GPU) and kept in the
// public "audio" bucket. The clip address is computed here from the text, so stored clips play
// straight away with no server call. Order: stored clip -> ask the function -> browser voice.
// Every clip starts and ends with a little silence, so the first word is not swallowed.
(function () {
  'use strict';
  var BASE = 'https://duptugctgzemfczbtvgj.supabase.co';
  var CLIPS = BASE + '/storage/v1/object/public/audio/';
  var FN = BASE + '/functions/v1/tts';
  // must match VOICES and VERSION in supabase/functions/tts/index.ts
  var VOICES = { man: 'us_daniel', woman: 'us_sarah' };
  var NAMES = { us_daniel: 'Daniel', us_sarah: 'Sarah' };
  var VERSION = 'v2';
  var MAX_STEP = 10; // steps that have clips so far (Unit 1)

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
  function askServer(text, voice) {
    return fetch(FN + '?text=' + encodeURIComponent(norm(text)) + '&voice=' + voice)
      .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error(r.status)); })
      .then(function (j) { if (!j.url) throw new Error('no url'); return j.url; });
  }

  function say(text, btn) {
    var again = btn && btn === playing;
    stop();
    if (again) return Promise.resolve(); // a second tap stops it
    var voice = voiceFor(text);
    if (btn) { btn.classList.add('playing'); playing = btn; }
    var done = function () { if (btn && playing === btn) { btn.classList.remove('playing'); playing = null; } };
    return clipUrl(text, voice)
      .then(playUrl)
      .catch(function () { return askServer(text, voice).then(playUrl); })
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
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-say]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    say(b.dataset.say, b);
  });

  window.BASIC_AUDIO = { say: say, stop: stop, voiceFor: voiceFor, lockFor: lockFor, clipUrl: clipUrl, button: button,
    VOICES: VOICES, MAX_STEP: MAX_STEP };
})();
