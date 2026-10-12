"""Common English spellings of each sound, for lining up letters with phonemes (build_pron.py).

COST[(letters, (phoneme, ...))] = cost; lower is more usual. Pairs not listed cost 9 (one letter, one
sound) or are not allowed. SILENT[letters] = cost of letters that are not pronounced at all.
"""
S = {
    # consonants
    'b': 'b bb', 'd': 'd dd ed', 'f': 'f ff ph gh', 'ɡ': 'g gg gu gh gue', 'h': 'h wh', 'dʒ': 'j g ge dg dge gi dj d gg',
    'k': 'c k ck ch q cc que', 'l': 'l ll le', 'm': 'm mm mb mn me', 'n': 'n nn kn gn ne', 'ŋ': 'ng n',
    'p': 'p pp', 'r': 'r rr wr rh re', 's': 's ss c sc ce se', 'ʃ': 'sh ti ci ss ch s si sci', 't': 't tt ed th',
    'tʃ': 'ch tch t', 'θ': 'th', 'ð': 'th the', 'v': 'v f ve', 'w': 'w wh u o', 'j': 'y i j', 'z': 'z s zz ss se ze',
    'ʒ': 's si g ge z',
    # vowels
    'æ': 'a ai', 'ɑ': 'a o au al ah ow', 'ɔ': 'o a au aw ou al oa augh ough', 'ʌ': 'u o ou oo oe a',
    'ə': 'a e i o u ou io ai y ia ea', 'ɛ': 'e ea ai a ie ue ay',
    'ɪ': 'i y e ee ui u o ie', 'i': 'e ee ea ie ei i y ey eo', 'eɪ': 'a ai ay ey ei ea eigh aigh e',
    'aɪ': 'i y igh ie ye uy ei ai eigh eye', 'oʊ': 'o oa ow oe ou ough ew eau', 'aʊ': 'ou ow ough',
    'ɔɪ': 'oi oy', 'ʊ': 'oo u ou o', 'u': 'oo u ew o ue ui ou oe ough wo',
    'ɝ': 'er ir ur or ear our yr err urr ere orr', 'ɚ': 'er or ar ur re our ure ir arr err r',
}
MULTI = {  # one spelling, two sounds
    ('k', 's'): 'x', ('ɡ', 'dʒ'): 'gg', ('k', 'ʃ'): 'x', ('ɡ', 'z'): 'x', ('k', 'w'): 'qu', ('j', 'u'): 'u ew eu ue iew you eau', ('w', 'ʌ'): 'o',
    ('j', 'ʊ'): 'u', ('j', 'ə'): 'u', ('ɑ', 'r'): 'ar', ('ɔ', 'r'): 'or ore oar our oor', ('ɛ', 'r'): 'ar are air ere ear',
    ('ɪ', 'r'): 'ear eer ere ier', ('aɪ', 'r'): 'ire', ('ʊ', 'r'): 'our ure oor', ('j', 'ʊ', 'r'): 'ure',
    ('ə', 'l'): 'le al el', ('ə', 'n'): 'en on an', ('t', 'ʃ'): 'ch',
}
COST = {}
for ph, sp in S.items():
    for k, g in enumerate(sp.split()):
        COST[(g, (ph,))] = 1 + 0.15 * k  # earlier spellings are a little more usual
COST[('re', ('r',))] = 2.5  # "here", "are"; but "break" is b-r-ea-k
for ph, sp in MULTI.items():
    for g in sp.split():
        COST[(g, ph)] = 1.5
# a weak vowel and the n / l / m after it are two groups when the spelling allows it (o=ə n=n);
# only "le" (apple) keeps them together, as its letters come in the other order
for g, ph in (('al', ('ə', 'l')), ('el', ('ə', 'l')), ('en', ('ə', 'n')), ('on', ('ə', 'n')), ('an', ('ə', 'n'))):
    COST[(g, ph)] = 2.8
SILENT = {'e': 2, 'h': 3, 'gh': 2.5, 'u': 3.5, 'w': 3.5, 'b': 3.5, 'l': 4, 't': 4, 'k': 4, 'n': 4.5, 's': 5, 'ue': 3, 'a': 5, 'o': 5, 'i': 5}
# consonant clusters that can start an English syllable (for placing the stress mark)
ONSETS = set('b d f ɡ h dʒ k l m n p r s ʃ t tʃ θ ð v w j z ʒ'.split()) | set(
    'pl pr bl br tr dr kl kr ɡl ɡr fl fr θr ʃr sp st sk sm sn sl sw spl spr str skr skw tw dw kw ɡw θw pj bj fj vj mj kj hj'.split())
