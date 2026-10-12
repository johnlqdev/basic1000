// Pronunciation of the words that have slow audio (steps 1-5 so far): American English IPA, split
// into sound groups. Each group is [letters, IPA]: the letters of the word, in order, that spell one
// sound. The slow button highlights a group's letters and its IPA together while that sound is heard.
// The letters of all groups, joined, must spell the word exactly (silent letters join a neighbour).
// The stress mark (ˈ) goes at the start of the stressed group, only in words of two or more syllables.
// The IPA follows what the voice (Daniel) actually says when he reads the word on its own; the phoneme
// model's transcript ("heard" in each timing file) was used to check it.
window.BASIC_PRON = {
  I: [['I', 'aɪ']],
  am: [['a', 'æ'], ['m', 'm']],
  a: [['a', 'eɪ']], // read alone, "a" has its strong form; in sentences it is usually /ə/
  man: [['m', 'm'], ['a', 'æ'], ['n', 'n']],
  woman: [['w', 'ˈw'], ['o', 'ʊ'], ['m', 'm'], ['a', 'ə'], ['n', 'n']],
  you: [['y', 'j'], ['ou', 'u']],
  are: [['a', 'ɑ'], ['re', 'r']],
  he: [['h', 'h'], ['e', 'i']],
  she: [['sh', 'ʃ'], ['e', 'i']],
  is: [['i', 'ɪ'], ['s', 'z']],
  boy: [['b', 'b'], ['oy', 'ɔɪ']],
  girl: [['g', 'ɡ'], ['ir', 'ɝ'], ['l', 'l']],
  child: [['ch', 'tʃ'], ['i', 'aɪ'], ['l', 'l'], ['d', 'd']],
  this: [['th', 'ð'], ['i', 'ɪ'], ['s', 's']],
  that: [['th', 'ð'], ['a', 'æ'], ['t', 't']],
  house: [['h', 'h'], ['ou', 'aʊ'], ['se', 's']],
  dog: [['d', 'd'], ['o', 'ɑ'], ['g', 'ɡ']],
  cat: [['c', 'k'], ['a', 'æ'], ['t', 't']],
  it: [['i', 'ɪ'], ['t', 't']],
  big: [['b', 'b'], ['i', 'ɪ'], ['g', 'ɡ']],
  the: [['th', 'ð'], ['e', 'i']], // read alone; in sentences usually /ðə/
  small: [['s', 's'], ['m', 'm'], ['a', 'ɔ'], ['ll', 'l']],
  we: [['w', 'w'], ['e', 'i']],
  they: [['th', 'ð'], ['ey', 'eɪ']],
  and: [['a', 'æ'], ['n', 'n'], ['d', 'd']],
};
