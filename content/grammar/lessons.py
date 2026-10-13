"""Full lessons for the grammar nodes, in the same order as the curriculum.

A lesson has:
  film     the stick-figure film: a list of shots (see films.js for every field)
  rule     points (the rule; the node's points are used if left out), table (optional pairs),
           examples [{t: sentence, v: 'woman' for Sarah}] - each can be played
  machine  optional: the sentence machine (people and the forms it can show)
  tasks    the exercises:
             pick  choose the right word for the gap (before ___ after), or the right choice
             build put the tiles in order
             fix   tap the wrong word, then choose the right one
             tap   tap every word of one kind
           each has: ask, why (shown after the answer), answer (the full right sentence, which is
           also recorded and played)
Every sentence that is spoken is recorded with Daniel's voice, or Sarah's when a woman or girl
speaks (v: 'woman'). Build and check with: python3 tools/grammar/build.py
"""


def L(t, **kw):  # a spoken line
    return dict(t=t, **kw)


def C(id, k, x, **kw):  # a figure or thing in a shot
    return dict(id=id, k=k, x=x, **kw)


def B(at, w, r=None, tag=None, x=None):  # a state of the word board
    out = {'at': at, 'w': w}
    if r:
        out['r'] = {str(i): v for i, v in r.items()}
    if tag:
        out['tag'] = {str(i): v for i, v in tag.items()}
    if x:
        out['x'] = x
    return out


def S(lines, cast=None, board=None, **kw):  # a shot
    out = {'lines': lines}
    if cast:
        out['cast'] = cast
    if board:
        out['board'] = board
    out.update(kw)
    return out


def pick(ask, opts, right, why, before='', after='', answer=None):
    a = answer or (' '.join(x for x in (before, right, after) if x) if (before or after) else None)
    out = {'kind': 'pick', 'ask': ask, 'opts': opts, 'right': right, 'why': why, 'before': before, 'after': after}
    if a:
        out['answer'] = a
    return out


def build(ask, tiles, right, why):
    return {'kind': 'build', 'ask': ask, 'tiles': tiles, 'right': right, 'why': why, 'answer': ' '.join(right)}


def fix(words, wrong, opts, right, why, ask='One word is wrong. Touch it.'):
    full = list(words)
    full[wrong] = right
    return {'kind': 'fix', 'ask': ask, 'words': words, 'wrong': wrong, 'opts': opts, 'right': right, 'why': why, 'answer': ' '.join(full)}


def tap(ask, words, right, why):
    return {'kind': 'tap', 'ask': ask, 'words': words, 'right': right, 'why': why, 'answer': ' '.join(words)}


PEOPLE = [
    {'s': 'I', 'be': 'am', 'rest': 'a man'},
    {'s': 'you', 'be': 'are', 'rest': 'a woman'},
    {'s': 'he', 'be': 'is', 'rest': 'a boy'},
    {'s': 'she', 'be': 'is', 'rest': 'a girl'},
    {'s': 'it', 'be': 'is', 'rest': 'a dog'},
    {'s': 'we', 'be': 'are', 'rest': 'children'},
    {'s': 'they', 'be': 'are', 'rest': 'cats'},
]

LESSONS = {}

# ---------------------------------------------------------------- 1. sentence
LESSONS['sentence'] = {
    'film': [
        S([L('Here are four words: dog, big, the, is.', hl=['dog', 'big', 'the', 'is']),
           L('In this order, they do not say anything.')],
          board=[B(0, ['dog', 'big', 'the', 'is'])]),
        S([L('Now put them in the right order.'),
           L('The dog is big.'),
           L('Now the words give one full idea.'),
           L('A group of words like this is a sentence.', hl=['sentence'])],
          cast=[C('d', 'dog', 160, s=1.5, in_=1)],
          board=[B(0, ['dog', 'big', 'the', 'is']), B(1, ['The', 'dog', 'is', 'big.'])]),
        S([L('A sentence begins with a big letter.', hl=['big', 'letter']),
           L('And it ends with a full stop.', hl=['full', 'stop'])],
          cast=[C('d', 'dog', 160, s=1.5)],
          board=[B(0, ['The', 'dog', 'is', 'big.'], r={0: 'ok'}, tag={0: 'big letter'}),
                 B(1, ['The', 'dog', 'is', 'big.'], r={0: 'ok', 3: 'ok'}, tag={0: 'big letter', 3: 'full stop'})]),
        S([L('Now change the order again.'),
           L('Is the dog big?', by='b'),
           L('This sentence asks something.'),
           L('So it ends with a question mark.', hl=['question', 'mark'])],
          cast=[C('b', 'boy', 90, accent=True, pose='point', poseAt=1), C('d', 'dog', 200, s=1.5, face=-1)],
          board=[B(0, ['The', 'dog', 'is', 'big.']), B(1, ['Is', 'the', 'dog', 'big?'], r={3: 'ok'}, tag={3: 'question mark'})]),
        S([L('If the words are in the wrong order, it is not a sentence.'),
           L('The words in a sentence always come in the right order.')],
          board=[B(0, ['big', 'is', 'dog', 'The'], x=[0, 1, 2, 3]), B(1, ['The', 'dog', 'is', 'big.'], r={0: 'ok', 1: 'ok', 2: 'ok', 3: 'ok'})]),
    ],
    'rule': {
        'examples': [{'t': 'The dog is big.'}, {'t': 'Is the dog big?'}, {'t': 'The cat is small.'}],
    },
    'tasks': [
        build('Put the words in the right order.', ['big.', 'The', 'is', 'house'], ['The', 'house', 'is', 'big.'],
              'A sentence begins with a big letter and ends with a full stop.'),
        pick('Which one is a sentence?', ['dog the small is', 'The dog is small.', 'is small the dog.'], 'The dog is small.',
             'Only this one has the words in the right order, with a big letter and a full stop.'),
        pick('How does a sentence begin?', ['with a big letter', 'with a full stop'], 'with a big letter',
             'The first letter of a sentence is a big letter.'),
        build('Make a question.', ['Is', 'big?', 'the', 'cat'], ['Is', 'the', 'cat', 'big?'],
              'A question ends with a question mark.'),
        fix(['the', 'dog', 'is', 'big.'], 0, ['The', 'the'], 'The', 'A sentence begins with a big letter.'),
        pick('What goes at the end?', ['.', '?'], '?', 'It asks something, so it ends with a question mark.',
             before='Is the cat small', answer='Is the cat small?'),
    ],
}

# ---------------------------------------------------------------- 2. noun
LESSONS['noun'] = {
    'film': [
        S([L('This is a man.'), L('This is a house.'), L('This is a dog.'), L('This is an apple.')],
          cast=[C('m', 'man', 60, label='man', labelAt=0), C('h', 'house', 135, in_=1, label='house', labelAt=1),
                C('d', 'dog', 215, in_=2, label='dog', labelAt=2), C('a', 'apple', 280, in_=3, s=1.2, label='apple', labelAt=3)]),
        S([L('A man is a person.'), L('A house is a place.'), L('A dog is an animal.'), L('An apple is a thing.')],
          cast=[C('m', 'man', 60, spot=True, spotAt=0), C('h', 'house', 135, spot=36, spotAt=1),
                C('d', 'dog', 215, spot=True, spotAt=2), C('a', 'apple', 280, s=1.2, spot=16, spotAt=3)]),
        S([L('Man, house, dog and apple are words that name something.'),
           L('A word that names a person, an animal, a place or a thing is a noun.', hl=['noun'])],
          cast=[C('m', 'man', 60, label='man', labelRole='n', labelAt=1), C('h', 'house', 135, label='house', labelRole='n', labelAt=1),
                C('d', 'dog', 215, label='dog', labelRole='n', labelAt=1), C('a', 'apple', 280, s=1.2, label='apple', labelRole='n', labelAt=1)]),
        S([L('Here is a sentence: the man has a dog.'),
           L('Man is a noun. Dog is a noun.', hl=['man', 'dog']),
           L('Has is not a noun. It does not name anything.')],
          cast=[C('m', 'man', 130), C('d', 'dog', 200)],
          board=[B(0, ['The', 'man', 'has', 'a', 'dog.']),
                 B(1, ['The', 'man', 'has', 'a', 'dog.'], r={1: 'n', 4: 'n'}, tag={1: 'noun', 4: 'noun'}),
                 B(2, ['The', 'man', 'has', 'a', 'dog.'], r={1: 'n', 2: 'x', 4: 'n'}, tag={1: 'noun', 2: 'not a noun', 4: 'noun'})]),
        S([L('The name of one person or one place is a noun too.'),
           L('It begins with a big letter: Mary, London.', hl=['Mary', 'London'])],
          cast=[C('w', 'woman', 120), C('h', 'house', 210, s=0.9)],
          board=[B(0, ['Mary', 'is', 'in', 'London.']),
                 B(1, ['Mary', 'is', 'in', 'London.'], r={0: 'n', 3: 'n'}, tag={0: 'noun', 3: 'noun'})]),
    ],
    'rule': {
        'examples': [{'t': 'The man has a dog.'}, {'t': 'The cat is in the house.'}, {'t': 'Mary has an apple.'}],
    },
    'tasks': [
        tap('Touch every noun.', ['The', 'boy', 'has', 'a', 'ball.'], [1, 4], 'Boy names a person. Ball names a thing.'),
        tap('Touch every noun.', ['The', 'cat', 'is', 'in', 'the', 'house.'], [1, 5], 'Cat names an animal. House names a place.'),
        pick('Which word is a noun?', ['big', 'book', 'is'], 'book', 'A book is a thing.'),
        pick('Which word is a noun?', ['tree', 'the', 'has'], 'tree', 'A tree is a thing.'),
        tap('Touch every noun.', ['Mary', 'has', 'a', 'red', 'apple.'], [0, 4], 'Mary is the name of a person. An apple is a thing.'),
        pick('A noun names...', ['a person, an animal, a place or a thing', 'what something is like'],
             'a person, an animal, a place or a thing', 'That is what a noun does: it names something.'),
    ],
}

# ---------------------------------------------------------------- 3. pronoun
LESSONS['pronoun'] = {
    'film': [
        S([L('The boy is tall.'), L('The boy is happy.'), L('The boy has a dog.'), L('We say the boy again and again.')],
          cast=[C('b', 'boy', 130), C('d', 'dog', 200, in_=2)],
          board=[B(0, ['The', 'boy', 'is', 'tall.']), B(1, ['The', 'boy', 'is', 'happy.']), B(2, ['The', 'boy', 'has', 'a', 'dog.'])]),
        S([L('In place of the boy, we can say he.', hl=['he']),
           L('He has a dog.'),
           L('He is a pronoun: a short word we use in place of a noun.', hl=['pronoun'])],
          cast=[C('b', 'boy', 130), C('d', 'dog', 200)],
          board=[B(0, ['The', 'boy', 'has', 'a', 'dog.'], r={1: 'n'}), B(1, ['He', 'has', 'a', 'dog.'], r={0: 'p'}, tag={0: 'pronoun'})]),
        S([L('For a man or a boy, we say he.', hl=['he']),
           L('For a woman or a girl, we say she.', hl=['she']),
           L('For an animal, we say it.', hl=['it']),
           L('For a thing, we also say it.', hl=['it'])],
          cast=[C('m', 'man', 60, label='he', labelRole='p', labelAt=0), C('w', 'woman', 130, in_=1, label='she', labelRole='p', labelAt=1),
                C('d', 'dog', 205, in_=2, label='it', labelRole='p', labelAt=2), C('a', 'apple', 275, s=1.2, in_=3, label='it', labelRole='p', labelAt=3)]),
        S([L('I am a teacher.', by='m'),
           L('I is the person who is talking.', hl=['I']),
           L('You are a doctor.', by='m'),
           L('You is the person you talk to.', hl=['you'])],
          cast=[C('m', 'man', 110, accent=True, pose='chest', poseAt=0, poseEnd=2), C('w', 'woman', 210, face=-1),
                C('m2', 'man', 110, accent=True, pose='point', poseAt=2, in_=2)]),
        S([L('We is you and other people together.', hl=['we']),
           L('They is other people, or other things.', hl=['they'])],
          cast=[C('m', 'man', 70, accent=True, label='we', labelRole='p', labelAt=0), C('w', 'woman', 105, accent=True),
                C('b', 'boy', 215, in_=1, label='they', labelRole='p', labelAt=1, n=2, gap=34)]),
    ],
    'rule': {
        'examples': [{'t': 'The girl is happy. She is happy.'}, {'t': 'The dog is small. It is small.'},
                     {'t': 'I am a teacher.'}, {'t': 'You are my friend.'}],
    },
    'tasks': [
        pick('Which word can we use in place of "the man"?', ['he', 'she', 'it'], 'he', 'He is for a man or a boy.'),
        pick('Which word can we use in place of "the girl"?', ['he', 'she', 'it'], 'she', 'She is for a woman or a girl.'),
        pick('Which word can we use in place of "the dog"?', ['he', 'she', 'it'], 'it', 'It is for an animal or a thing.'),
        pick('Which word can we use in place of "the boy and the girl"?', ['he', 'it', 'they'], 'they', 'They is for other people or things.'),
        tap('Touch the pronoun.', ['She', 'has', 'a', 'cat.'], [0], 'She is used in place of a woman or a girl.'),
        build('Put the words in the right order.', ['is', 'He', 'a', 'man.'], ['He', 'is', 'a', 'man.'], 'He comes first, then is.'),
    ],
}

# ---------------------------------------------------------------- 4. be
LESSONS['be'] = {
    'film': [
        S([L('I am a man.', by='m'), L('I am a woman.', by='w', v='woman'), L('With I, we use am.', hl=['am'])],
          cast=[C('m', 'man', 110, accent=True, pose='chest', poseAt=0), C('w', 'woman', 210, face=-1, pose='chest', poseAt=1)]),
        S([L('I am a man.'), L('He is a man.'), L('She is a woman.'), L('It is a dog.'),
           L('With he, she and it, we use is.', hl=['is'])],
          cast=[C('m', 'man', 90), C('w', 'woman', 170, in_=2), C('d', 'dog', 250, in_=3)],
          board=[B(0, ['I', 'am', 'a', 'man.'], r={0: 'p', 1: 'b'}), B(1, ['He', 'is', 'a', 'man.'], r={0: 'p', 1: 'b'}),
                 B(2, ['She', 'is', 'a', 'woman.'], r={0: 'p', 1: 'b'}), B(3, ['It', 'is', 'a', 'dog.'], r={0: 'p', 1: 'b'})]),
        S([L('You are a child.'), L('We are children.'), L('They are children.'),
           L('With you, we and they, we use are.', hl=['are'])],
          cast=[C('b', 'boy', 120, n=3, gap=36)],
          board=[B(0, ['You', 'are', 'a', 'child.'], r={0: 'p', 1: 'b'}), B(1, ['We', 'are', 'children.'], r={0: 'p', 1: 'b'}),
                 B(2, ['They', 'are', 'children.'], r={0: 'p', 1: 'b'})]),
        S([L('So: I am.', hl=['am']), L('He is, she is, it is.', hl=['is']), L('You are, we are, they are.', hl=['are'])],
          board=[B(0, ['I', 'am'], r={0: 'p', 1: 'b'}), B(1, ['he', 'she', 'it', 'is'], r={0: 'p', 1: 'p', 2: 'p', 3: 'b'}),
                 B(2, ['you', 'we', 'they', 'are'], r={0: 'p', 1: 'p', 2: 'p', 3: 'b'})]),
    ],
    'rule': {
        'table': [['I', 'am'], ['he, she, it', 'is'], ['you, we, they', 'are']],
        'examples': [{'t': 'I am a man.'}, {'t': 'She is a girl.'}, {'t': 'They are children.'}, {'t': 'It is a cat.'}],
    },
    'machine': {'people': PEOPLE, 'forms': ['plain']},
    'tasks': [
        pick('Put the right word in the space.', ['am', 'is', 'are'], 'is', 'With he, she and it, use is.', before='He', after='a boy.'),
        pick('Put the right word in the space.', ['am', 'is', 'are'], 'are', 'With you, we and they, use are.', before='We', after='children.'),
        build('Put the words in the right order.', ['are', 'dogs.', 'They'], ['They', 'are', 'dogs.'], 'They, then are.'),
        fix(['You', 'is', 'a', 'woman.'], 1, ['am', 'is', 'are'], 'are', 'With you, use are, even for one person.'),
        pick('Put the right word in the space.', ['am', 'is', 'are'], 'am', 'With I, use am.', before='I', after='a boy.'),
        pick('Put the right word in the space.', ['am', 'is', 'are'], 'is', 'The cat is one animal, like it: use is.', before='The cat', after='small.'),
    ],
}

# ---------------------------------------------------------------- 5. a-an
LESSONS['a-an'] = {
    'film': [
        S([L('This is a dog.', hl=['a']), L('This is a cat.', hl=['a']), L('We use a before one person or thing.')],
          cast=[C('d', 'dog', 110, label='a dog', labelRole='art', labelAt=0), C('c', 'cat', 210, in_=1, label='a cat', labelRole='art', labelAt=1)]),
        S([L('This is an apple.', hl=['an']), L('This is an egg.', hl=['an']),
           L('Apple and egg begin with the sound of a and e. So we use an.', hl=['an'])],
          cast=[C('a', 'apple', 110, s=1.4, label='an apple', labelRole='art', labelAt=0), C('e', 'egg', 210, s=1.3, in_=1, label='an egg', labelRole='art', labelAt=1)]),
        S([L('Before the sound of a, e, i, o or u, we use an.'), L('A dog.'), L('An apple.'), L('An egg.'), L('A house.')],
          board=[B(1, ['a', 'dog'], r={0: 'art'}), B(2, ['an', 'apple'], r={0: 'art'}), B(3, ['an', 'egg'], r={0: 'art'}), B(4, ['a', 'house'], r={0: 'art'})]),
        S([L('Hour begins with h, but we do not say the h. So: an hour.', hl=['an']),
           L('University begins with u, but it sounds like you. So: a university.', hl=['a']),
           L('It is the first sound that matters, not the first letter.')],
          board=[B(0, ['an', 'hour'], r={0: 'art'}, tag={1: 'sounds like our'}), B(1, ['a', 'university'], r={0: 'art'}, tag={1: 'sounds like you'})]),
    ],
    'rule': {
        'examples': [{'t': 'I have a dog and an apple.'}, {'t': 'It is an old house.'}, {'t': 'She has an egg.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['a', 'an'], 'an', 'Apple begins with the sound of a.', after='apple', answer='an apple'),
        pick('Put the right word in the space.', ['a', 'an'], 'a', 'Cat begins with the sound of c.', after='cat', answer='a cat'),
        pick('Put the right word in the space.', ['a', 'an'], 'an', 'Egg begins with the sound of e.', after='egg', answer='an egg'),
        pick('Put the right word in the space.', ['a', 'an'], 'an', 'Old begins with the sound of o.', before='It is', after='old house.'),
        pick('Put the right word in the space.', ['a', 'an'], 'a', 'Big begins with b, so: a.', before='It is', after='big apple.'),
        fix(['She', 'has', 'a', 'egg.'], 2, ['a', 'an'], 'an', 'Egg begins with the sound of e, so: an egg.'),
    ],
}

# ---------------------------------------------------------------- 6. plural
LESSONS['plural'] = {
    'film': [
        S([L('One cat.'), L('Two cats.', hl=['cats']), L('For more than one, we add s: cat, cats.')],
          cast=[C('c', 'cat', 100, label='one cat', labelAt=0), C('c2', 'cat', 190, n=2, gap=40, in_=1, label='two cats', labelRole='n', labelAt=1)],
          board=[B(2, ['cat', 'cats'], r={1: 'n'})]),
        S([L('One box.'), L('Three boxes.', hl=['boxes']), L('After s, sh, ch and x, we add es: box, boxes.')],
          cast=[C('x', 'box', 90, label='one box', labelAt=0), C('x2', 'box', 175, n=3, gap=28, in_=1, label='three boxes', labelRole='n', labelAt=1)],
          board=[B(2, ['box', 'boxes'], r={1: 'n'})]),
        S([L('One man.'), L('Two men.', hl=['men']), L('Some nouns change: man, men.')],
          cast=[C('m', 'man', 90, label='one man', labelAt=0), C('m2', 'man', 180, n=2, gap=40, in_=1, label='two men', labelRole='n', labelAt=1)],
          board=[B(2, ['man', 'men'], r={1: 'n'})]),
        S([L('One child.'), L('Three children.', hl=['children']), L('Child, children. Woman, women.')],
          cast=[C('g', 'girl', 80, label='one child', labelAt=0), C('b', 'boy', 165, n=3, gap=34, in_=1, label='three children', labelRole='n', labelAt=1)],
          board=[B(2, ['child', 'children'], r={1: 'n'})]),
        S([L('The plural is the form of a noun for more than one.', hl=['plural']),
           L('Two apples, three boxes, four children.')],
          cast=[C('a', 'apple', 40, n=2, gap=24, s=1.2, in_=1), C('x', 'box', 115, n=3, gap=26, in_=1),
                C('c', 'boy', 208, n=4, gap=26, in_=1)],
          board=[B(0, ['apples', 'boxes', 'children'], r={0: 'n', 1: 'n', 2: 'n'}, tag={0: 'plural', 1: 'plural', 2: 'plural'})]),
    ],
    'rule': {
        'table': [['cat', 'cats'], ['box', 'boxes'], ['man', 'men'], ['child', 'children']],
        'examples': [{'t': 'I have two cats.'}, {'t': 'The children are in the garden.'}, {'t': 'Two men and a woman.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['dog', 'dogs', 'doges'], 'dogs', 'For most nouns, add s.', before='one dog, two', answer='one dog, two dogs'),
        pick('Put the right word in the space.', ['boxs', 'boxes', 'box'], 'boxes', 'After x, add es.', before='one box, two', answer='one box, two boxes'),
        pick('Put the right word in the space.', ['mans', 'men', 'manes'], 'men', 'Man changes: men.', before='one man, two', answer='one man, two men'),
        pick('Put the right word in the space.', ['childs', 'children', 'child'], 'children', 'Child changes: children.', before='one child, three', answer='one child, three children'),
        fix(['I', 'have', 'two', 'cat.'], 3, ['cat.', 'cats.'], 'cats.', 'Two means more than one, so: cats.'),
        tap('Touch the plural nouns.', ['The', 'boys', 'have', 'two', 'dogs.'], [1, 4], 'Boys and dogs mean more than one.'),
    ],
}

# ---------------------------------------------------------------- 7. be-not
LESSONS['be-not'] = {
    'film': [
        S([L('The dog is big.'), L('Now look at this dog.'), L('The dog is not big.', hl=['not']), L('We put not after is.', hl=['not'])],
          cast=[C('d', 'dog', 160, s=1.5, out=1), C('d2', 'dog', 160, s=0.75, in_=1)],
          board=[B(0, ['The', 'dog', 'is', 'big.'], r={2: 'b'}), B(2, ['The', 'dog', 'is', 'not', 'big.'], r={2: 'b', 3: 'neg'})]),
        S([L('I am not a woman.', by='m'), L('I am not a man.', by='w', v='woman'),
           L('After am, is and are, we put not.', hl=['not'])],
          cast=[C('m', 'man', 110, accent=True, pose='chest', poseAt=0), C('w', 'woman', 210, face=-1, pose='chest', poseAt=1)]),
        S([L('They are here.'), L('They are not here.', hl=['not'])],
          cast=[C('b', 'boy', 140, n=2, gap=40, out=1)],
          board=[B(0, ['They', 'are', 'here.'], r={1: 'b'}), B(1, ['They', 'are', 'not', 'here.'], r={1: 'b', 2: 'neg'})]),
        S([L('In talk, we often make is not shorter.'), L('Is not becomes isn\'t.'),
           L('Are not becomes aren\'t.'), L('I am not becomes I\'m not.')],
          board=[B(0, ['is', 'not'], r={0: 'b', 1: 'neg'}), B(1, ['isn\'t'], r={0: 'neg'}), B(2, ['aren\'t'], r={0: 'neg'}),
                 B(3, ['I\'m', 'not'], r={0: 'b', 1: 'neg'})]),
    ],
    'rule': {
        'examples': [{'t': 'I am not a child.'}, {'t': 'The dog is not big.'}, {'t': 'They are not here.'}],
    },
    'machine': {'people': PEOPLE, 'forms': ['plain', 'not']},
    'tasks': [
        build('Say it with not.', ['not', 'She', 'a', 'girl.', 'is'], ['She', 'is', 'not', 'a', 'girl.'], 'Not comes right after is.'),
        pick('Put the right word in the space.', ['am', 'is', 'are'], 'am', 'With I, use am, then not.', before='I', after='not a dog.'),
        fix(['They', 'is', 'not', 'here.'], 1, ['am', 'is', 'are'], 'are', 'With they, use are.'),
        pick('Put the right word in the space.', ['is', 'are'], 'are', 'The cats are more than one, so: are.', before='The cats', after='not big.'),
        build('Say it with not.', ['a', 'dog.', 'not', 'is', 'It'], ['It', 'is', 'not', 'a', 'dog.'], 'It, is, then not.'),
        pick('In talk, "is not" is often...', ['isn\'t', 'aren\'t'], 'isn\'t', 'Is not becomes isn\'t. Are not becomes aren\'t.'),
    ],
}

# ---------------------------------------------------------------- 8. be-question
LESSONS['be-question'] = {
    'film': [
        S([L('She is a girl.'), L('To ask, we put is first: is she a girl?', hl=['is']),
           L('Now it is a question. It ends with a question mark.')],
          cast=[C('g', 'girl', 160)],
          board=[B(0, ['She', 'is', 'a', 'girl.'], r={0: 'p', 1: 'b'}), B(1, ['Is', 'she', 'a', 'girl?'], r={0: 'b', 1: 'p'})]),
        S([L('Is she a girl?', by='m'), L('Yes, she is.', by='w', v='woman'),
           L('A short answer uses the same word: yes, she is.', hl=['is'])],
          cast=[C('m', 'man', 70, accent=True, pose='point', poseAt=0), C('g', 'girl', 160), C('w', 'woman', 240, face=-1, pose='nod', poseAt=1, poseEnd=2)]),
        S([L('You are a teacher.'), L('Are you a teacher?', by='m'), L('No, I am not.', by='w', v='woman'),
           L('With are, it is the same: are goes first.', hl=['are'])],
          cast=[C('m', 'man', 100, accent=True), C('w', 'woman', 210, face=-1)],
          board=[B(0, ['You', 'are', 'a', 'teacher.'], r={0: 'p', 1: 'b'}), B(1, ['Are', 'you', 'a', 'teacher?'], r={0: 'b', 1: 'p'})]),
        S([L('Is it big?'), L('Am I late?'), L('Am, is and are go first in a question.', hl=['am', 'is', 'are'])],
          cast=[C('d', 'dog', 150, s=1.4)],
          board=[B(0, ['Is', 'it', 'big?'], r={0: 'b', 1: 'p'}), B(1, ['Am', 'I', 'late?'], r={0: 'b', 1: 'p'})]),
    ],
    'rule': {
        'examples': [{'t': 'Is she a girl? Yes, she is.'}, {'t': 'Are you a teacher? No, I am not.'}, {'t': 'Is it big?'}],
    },
    'machine': {'people': PEOPLE, 'forms': ['plain', 'question']},
    'tasks': [
        build('Make a question.', ['a', 'boy?', 'he', 'Is'], ['Is', 'he', 'a', 'boy?'], 'Is goes first.'),
        pick('Put the right word in the space.', ['Is', 'Are', 'Am'], 'Are', 'With they, use are.', after='they children?'),
        pick('Put the right word in the space.', ['is', 'are', 'am'], 'is', 'The answer uses the same word as the question.', before='Is the dog small? Yes, it', after='.', answer='Is the dog small? Yes, it is.'),
        build('Make a question.', ['you', 'a', 'doctor?', 'Are'], ['Are', 'you', 'a', 'doctor?'], 'Are goes first.'),
        pick('Put the right word in the space.', ['Am', 'Is', 'Are'], 'Am', 'With I, use am.', after='I late?'),
        fix(['Is', 'they', 'here?'], 0, ['Is', 'Are'], 'Are', 'With they, use are: Are they here?'),
    ],
}

# ---------------------------------------------------------------- 9. adjective
LESSONS['adjective'] = {
    'film': [
        S([L('This dog is big.', hl=['big']), L('This dog is small.', hl=['small']), L('Big and small say what the dog is like.')],
          cast=[C('d', 'dog', 100, s=1.6, label='big', labelRole='a', labelAt=0), C('d2', 'dog', 225, s=0.7, in_=1, label='small', labelRole='a', labelAt=1)]),
        S([L('A big house.', hl=['big']), L('A small house.', hl=['small']),
           L('A word that says what a person or a thing is like is an adjective.', hl=['adjective'])],
          cast=[C('h', 'house', 100, s=1.25, label='big', labelRole='a', labelAt=0), C('h2', 'house', 220, s=0.7, in_=1, label='small', labelRole='a', labelAt=1)]),
        S([L('An adjective can come before a noun: a big dog.'), L('Or after is: the dog is big.')],
          cast=[C('d', 'dog', 160, s=1.5)],
          board=[B(0, ['a', 'big', 'dog'], r={1: 'a', 2: 'n'}, tag={1: 'adjective', 2: 'noun'}),
                 B(1, ['The', 'dog', 'is', 'big.'], r={1: 'n', 3: 'a'}, tag={1: 'noun', 3: 'adjective'})]),
        S([L('One big dog.'), L('Two big dogs.'), L('The adjective does not change. Only the noun gets s.', hl=['big', 'dogs'])],
          cast=[C('d', 'dog', 110, s=1.4, out=1), C('d2', 'dog', 110, s=1.4, n=2, gap=90, in_=1)],
          board=[B(0, ['one', 'big', 'dog'], r={1: 'a', 2: 'n'}), B(1, ['two', 'big', 'dogs'], r={1: 'a', 2: 'n'})]),
        S([L('The man is happy.', hl=['happy']), L('The woman is tired.', hl=['tired']), L('Happy and tired are adjectives too.')],
          cast=[C('m', 'man', 110, pose='wave', poseAt=0, label='happy', labelRole='a', labelAt=0),
                C('w', 'woman', 210, face=-1, pose='shrug', poseAt=1, in_=1, label='tired', labelRole='a', labelAt=1)]),
    ],
    'rule': {
        'examples': [{'t': 'It is a small house.'}, {'t': 'The children are happy.'}, {'t': 'She has a red bag.'}],
    },
    'tasks': [
        tap('Touch every adjective.', ['The', 'big', 'dog', 'is', 'happy.'], [1, 4], 'Big and happy say what the dog is like.'),
        pick('Which word is an adjective?', ['tall', 'table', 'run'], 'tall', 'Tall says what a person or thing is like.'),
        build('Put the words in the right order.', ['big', 'It', 'is', 'a', 'house.'], ['It', 'is', 'a', 'big', 'house.'], 'The adjective comes before the noun.'),
        fix(['I', 'have', 'two', 'bigs', 'dogs.'], 3, ['big', 'bigs'], 'big', 'An adjective does not get s.'),
        pick('Put the right word in the space.', ['small', 'smalls'], 'small', 'An adjective has the same form for one and more than one.', before='The cats are', after='.', answer='The cats are small.'),
        tap('Touch the adjective.', ['She', 'has', 'a', 'red', 'bag.'], [3], 'Red says what the bag is like.'),
    ],
}

# ---------------------------------------------------------------- 10. verb
LESSONS['verb'] = {
    'film': [
        S([L('The boy runs.', hl=['runs'])],
          cast=[C('b', 'boy', 50, to=270, toAt=0, pose='run', accent=True)], min=2600),
        S([L('The girl eats an apple.', hl=['eats'])],
          cast=[C('g', 'girl', 160, pose='eat', poseAt=0, holds='apple', accent=True)], min=2400),
        S([L('The man sits.', hl=['sits']), L('The dog runs.', hl=['runs'])],
          cast=[C('m', 'man', 90, pose='sit', poseAt=0, accent=True), C('d', 'dog', 150, in_=1, to=280, toAt=1)]),
        S([L('Runs, eats and sits are words for things we do.'),
           L('A word for something we do, or something that happens, is a verb.', hl=['verb'])],
          board=[B(0, ['The', 'boy', 'runs.'], r={2: 'v'}, tag={2: 'verb'}),
                 B(1, ['The', 'girl', 'eats', 'an', 'apple.'], r={2: 'v'}, tag={2: 'verb'})]),
        S([L('Every sentence has a verb.'), L('Am, is and are are verbs too.', hl=['am', 'is', 'are'])],
          cast=[C('d', 'dog', 160, s=1.5)],
          board=[B(0, ['The', 'dog', 'runs.'], r={2: 'v'}, tag={2: 'verb'}), B(1, ['The', 'dog', 'is', 'big.'], r={2: 'v'}, tag={2: 'verb'})]),
        S([L('I walk.'), L('I walked.'),
           L('A verb can change its form to show the time. This is called the tense.', hl=['tense'])],
          cast=[C('m', 'man', 90, to=230, toAt=0, accent=True)],
          board=[B(0, ['I', 'walk.'], r={1: 'v'}, tag={1: 'now'}), B(1, ['I', 'walked.'], r={1: 'v'}, tag={1: 'before now'})]),
    ],
    'rule': {
        'examples': [{'t': 'The children play in the garden.'}, {'t': 'I eat an apple.'}, {'t': 'The dog runs.'}],
    },
    'tasks': [
        tap('Touch the verb.', ['The', 'dog', 'runs.'], [2], 'Runs is what the dog does.'),
        tap('Touch the verb.', ['I', 'eat', 'an', 'apple.'], [1], 'Eat is what I do.'),
        pick('Which word is a verb?', ['eat', 'apple', 'red'], 'eat', 'Eat is something we do.'),
        tap('Touch the verb.', ['The', 'children', 'play', 'in', 'the', 'garden.'], [2], 'Play is what the children do.'),
        pick('Which word is a verb?', ['sleep', 'bed', 'happy'], 'sleep', 'Sleep is something we do.'),
        build('Put the words in the right order.', ['sleeps.', 'The', 'cat'], ['The', 'cat', 'sleeps.'], 'First the cat, then the verb.'),
    ],
}


def _fix_in(obj):
    """'in' is a Python word, so shots write in_=...; store it as 'in'."""
    if isinstance(obj, dict):
        return {('in' if k == 'in_' else k): _fix_in(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fix_in(v) for v in obj]
    return obj


LESSONS = _fix_in(LESSONS)
