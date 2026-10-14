// Mother-language annotations: a short translation of each Basic 1000 word, in the sense its
// examples teach. Words only, never sentences.
//
// Each language is one resource file, lang/<code>.json = { code, name, english, tag, dir, words: { headword: text } },
// listed in lang/index.json = { default, languages: [{ code, name, english, tag?, dir? }] }. tag is the
// BCP 47 language tag (fonts, screen readers), dir is "rtl" for right-to-left scripts. Adding a language
// needs no change here (see tools/lang/build.py).
//
// The page puts <span class="ml" data-ml="headword"></span> wherever a translation belongs; fill()
// writes the text into every such span once the file has loaded, and again whenever the language
// changes, so no part of the page has to be drawn again.
(function () {
  var BASE = '/lang/';
  var index = null, current = null, cache = {}, wanted = null, ready = null;

  function getJSON(url) {
    return fetch(url).then(function (r) { if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); });
  }
  function langs() { return index ? index.languages.slice() : []; }
  function info(code) { return langs().filter(function (l) { return l.code === code; })[0] || null; }
  // the stored choice: undefined = never chosen (use the default), '' = none (English only)
  function resolve(choice) {
    if (choice === '' || !index) return choice === '' ? '' : null;
    if (choice && info(choice)) return choice;
    return index.default && info(index.default) ? index.default : '';
  }

  function word(w) { return current && current.words[w] || ''; }

  // the slot's inner HTML: a code chip (always left to right) and the text in its own language and direction
  function inner(t) {
    if (!t || !current) return '';
    var tag = current.tag || current.code, dir = current.dir === 'rtl' ? 'rtl' : 'ltr';
    var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    return '<b class="ml-code">' + esc(current.code.toUpperCase()) + '</b><span class="ml-text" lang="' + esc(tag) + '" dir="' + dir + '">' + esc(t) + '</span>';
  }
  function fill(root) {
    (root || document).querySelectorAll('[data-ml]').forEach(function (el) {
      var t = word(el.getAttribute('data-ml'));
      el.hidden = !t;
      el.title = t && current ? current.english : '';
      el.innerHTML = inner(t);
    });
  }

  // choose a language (a code, '' for none, or undefined for the default); resolves to the code in use
  function use(choice) {
    wanted = choice;
    return ready.then(function () {
      var code = resolve(choice);
      if (!code) { current = null; fill(); return ''; }
      var load = cache[code] || (cache[code] = getJSON(BASE + code + '.json').catch(function (e) { delete cache[code]; throw e; }));
      return load.then(function (data) {
        if (wanted !== choice) return current ? current.code : '';  // another choice came in meanwhile
        current = data; fill(); return code;
      });
    }).catch(function () { current = null; fill(); return ''; });
  }

  ready = getJSON(BASE + 'index.json').then(function (d) { index = d; }).catch(function () { index = { default: '', languages: [] }; });

  window.BASIC_LANG = {
    ready: function () { return ready; },
    languages: langs, info: info, resolve: resolve, use: use, word: word, fill: fill, html: function (w) { return inner(word(w)); },
    current: function () { return current ? current.code : ''; }
  };
})();
