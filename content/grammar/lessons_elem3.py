"""Elementary school lessons, part 3: irregular past forms, did and did not, going to, will,
comparatives and superlatives, adverbs, how much and how many, must and have to, should, the
past continuous, clauses."""
from lessons_kit import L, C, B, S, pick, build, fix, tap, TOP  # noqa: F401

LESSONS = {}

# ---------------------------------------------------------------- went, saw, came
LESSONS['past-irregular'] = {
    'film': [
        S([L('Today I go to the shop.'), L('Yesterday I went to the shop.', hl=['went'])],
          cast=[C('m', 'man', 50, accent=True, to=190, toAt=0), C('h', 'house', 265, s=0.8, label='shop', labelAt=0)],
          board=[B(0, ['I', 'go'], r={1: 'v'}, tag={1: 'now'}), B(1, ['I', 'went'], r={1: 'v'}, tag={1: 'past'})]),
        S([L('Some verbs do not add “ed”. They have their own past form.'), L('Go, went. See, saw.', hl=['went', 'saw']),
           L('Come, came. Eat, ate.', hl=['came', 'ate'])],
          board=[B(0, ['go', 'goed'], x=[1]), B(1, ['go', 'went', 'see', 'saw'], r={1: 'v', 3: 'v'}),
                 B(2, ['come', 'came', 'eat', 'ate'], r={1: 'v', 3: 'v'})]),
        S([L('We saw a big cow.', by='g', v='woman'), L('“See” becomes “saw”.', hl=['saw'])],
          cast=[C('g', 'girl', 80, accent=True, pose='point'), C('b', 'boy', 115), C('c', 'cow', 240, s=1.2, face=-1)]),
        S([L('She came home and ate an apple.', hl=['came', 'ate'])],
          cast=[C('h', 'house', 250, s=0.9), C('w', 'woman', 40, accent=True, to=180, toAt=0, dur=2200)], min=2800),
        S([L('Take, took. Give, gave. Make, made.', hl=['took', 'gave', 'made']), L('We learn these forms one by one.')],
          board=[B(0, ['take', 'took', 'give', 'gave', 'make', 'made'], r={1: 'v', 3: 'v', 5: 'v'})]),
    ],
    'rule': {
        'table': [['go', 'went'], ['see', 'saw'], ['come', 'came'], ['eat', 'ate'], ['take', 'took'], ['give', 'gave'], ['make', 'made']],
        'examples': [{'t': 'I went to the shop.'}, {'t': 'We saw a big ship.'}, {'t': 'She came home at six.'}, {'t': 'They ate some bread.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['goed', 'went'], 'went', 'Go has its own past form: went.', before='I', after='to the shop yesterday.'),
        pick('Put the right word in the space.', ['see', 'saw'], 'saw', 'The past of see is saw.', before='Last week we', after='a big ship.'),
        pick('Put the right word in the space.', ['came', 'comed'], 'came', 'The past of come is came.', before='She', after='home at six.'),
        pick('Put the right word in the space.', ['eated', 'ate'], 'ate', 'The past of eat is ate.', before='They', after='some bread.'),
        fix(['He', 'goed', 'to', 'school.'], 1, ['goed', 'went'], 'went', 'Go has its own past form: went.'),
        build('Put the words in the right order.', ['a', 'We', 'ship.', 'saw', 'big'], ['We', 'saw', 'a', 'big', 'ship.'], 'We, then saw, then what.'),
    ],
}

# ---------------------------------------------------------------- did you? I did not
LESSONS['past-not-question'] = {
    'film': [
        S([L('Did you sleep well?', by='w', v='woman'), L('Yes, I did.', by='m')],
          cast=[C('s', 'sun', 40, y=70), C('w', 'woman', 120, accent=True), C('m', 'man', 220, face=-1, pose='nod', poseAt=1)]),
        S([L('You slept well.'), L('Did you sleep well?', hl=['did']), L('Put “did” first. Then the verb goes back to its simple form.')],
          board=[B(0, ['You', 'slept', 'well.'], r={1: 'v'}, tag={1: 'past'}),
                 B(1, ['Did', 'you', 'sleep', 'well?'], r={0: 'q', 2: 'v'}, tag={2: 'simple form'})]),
        S([L('He came to school.'), L('He did not come to school.', hl=['did', 'not']), L('“Did not”, then the simple form.')],
          board=[B(0, ['He', 'came', 'to', 'school.'], r={1: 'v'}),
                 B(1, ['He', 'did', 'not', 'come', 'to', 'school.'], r={1: 'neg', 2: 'neg', 3: 'v'}, tag={3: 'simple form'})]),
        S([L('Did she go?'), L('Did they go?'), L('“Did” is the same with every subject.')],
          board=[B(0, ['Did', 'she', 'go?'], r={0: 'q', 2: 'v'}), B(1, ['Did', 'they', 'go?'], r={0: 'q', 2: 'v'})]),
        S([L('Did you see the dog?', by='g', v='woman'), L('No, I did not.', by='b')],
          cast=[C('g', 'girl', 90, accent=True), C('b', 'boy', 190, face=-1, pose='shrug', poseAt=1), C('d', 'dog', 290, in_=1, face=-1)]),
    ],
    'rule': {
        'table': [['not', 'did not + simple form'], ['question', 'did + subject + simple form']],
        'examples': [{'t': 'Did you sleep well? Yes, I did.'}, {'t': 'He did not come to school.'}, {'t': 'Did they eat the bread?'},
                     {'t': 'I did not go out.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['go', 'went'], 'go', 'After did not, use the simple form.', before='I did not', after='to school.'),
        pick('Put the right word in the space.', ['Did', 'Do'], 'Did', 'Yesterday is past: did.', after='you see him yesterday?'),
        pick('Put the right word in the space.', ['see', 'saw'], 'see', 'After did, use the simple form.', before='Did you', after='the dog?'),
        build('Make a question.', ['you', 'Did', 'well?', 'sleep'], ['Did', 'you', 'sleep', 'well?'], 'Did comes first.'),
        fix(['She', 'did', 'not', 'came.'], 3, ['come', 'came'], 'come', 'After did not, use the simple form.'),
        pick('Put the right word in the space.', ['did', 'do'], 'did', 'The answer uses did again.',
             before='Did you eat? Yes, I', after='.', answer='Did you eat? Yes, I did.'),
    ],
}

# ---------------------------------------------------------------- going to
LESSONS['going-to'] = {
    'film': [
        S([L('I am going to visit my mother.', by='m'), L('This is a plan for the future.')],
          cast=[C('m', 'man', 90, accent=True, holds='bag', pose='hold'), C('h', 'house', 250, s=0.8)]),
        S([L('I am going to swim.'), L('“Am”, “is” or “are”, then “going to”, then the verb.', hl=['going', 'to'])],
          board=[B(0, ['I', 'am', 'going', 'to', 'swim.'], r={1: 'b', 4: 'v'}),
                 B(1, ['I', 'am', 'going', 'to', 'swim.'], r={1: 'b', 4: 'v'}, tag={2: 'going to', 4: 'verb'})]),
        S([L('Look at the clouds. It is going to rain.', by='w', v='woman'), L('We can see that it will happen.')],
          cast=[C('c', 'cloud', 200, y=36), C('c2', 'cloud', 250, y=46, s=0.8), C('w', 'woman', 90, accent=True, pose='reach')]),
        S([L('We are going to play a game after school.', by='g', v='woman')],
          cast=[C('g', 'girl', 90, accent=True), C('b', 'boy', 140), C('o', 'ball', 210), C('h', 'house', 275, s=0.6, label='school', labelAt=0)]),
        S([L('She is not going to come.', hl=['not']), L('Is she going to come?', hl=['is'])],
          board=[B(0, ['She', 'is', 'not', 'going', 'to', 'come.'], r={1: 'b', 2: 'neg', 5: 'v'}),
                 B(1, ['Is', 'she', 'going', 'to', 'come?'], r={0: 'b', 4: 'v'})]),
    ],
    'rule': {
        'examples': [{'t': 'We are going to play a game after school.', 'v': 'woman'}, {'t': 'She is not going to come.'},
                     {'t': 'Look at the clouds. It is going to rain.', 'v': 'woman'}, {'t': 'I am going to visit my mother.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'am', 'rest': 'going to swim'}, {'s': 'you', 'be': 'are', 'rest': 'going to cook'},
        {'s': 'he', 'be': 'is', 'rest': 'going to sleep'}, {'s': 'she', 'be': 'is', 'rest': 'going to come'},
        {'s': 'it', 'be': 'is', 'rest': 'going to rain'}, {'s': 'we', 'be': 'are', 'rest': 'going to play'},
        {'s': 'they', 'be': 'are', 'rest': 'going to help'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right word in the space.', ['going', 'go'], 'going', 'Am, then going to.', before='I am', after='to visit my mother.'),
        pick('Put the right word in the space.', ['is', 'are'], 'are', 'With we: are.', before='We', after='going to play a game.'),
        pick('Put the right word in the space.', ['rain', 'raining'], 'rain', 'After going to, use the simple form.',
             before='Look at the clouds. It is going to', after='.'),
        build('Put the words in the right order.', ['going', 'is', 'She', 'to', 'come.', 'not'], ['She', 'is', 'not', 'going', 'to', 'come.'],
              'Not comes after is.'),
        build('Make a question.', ['you', 'Are', 'going', 'to', 'swim?'], ['Are', 'you', 'going', 'to', 'swim?'], 'Are comes first.'),
        fix(['They', 'is', 'going', 'to', 'swim.'], 1, ['is', 'are'], 'are', 'With they: are.'),
    ],
}

# ---------------------------------------------------------------- will
LESSONS['will'] = {
    'film': [
        S([L('It will be cold tomorrow.', hl=['will']), L('We use “will” and a verb to say what we think will happen.')],
          cast=[C('c', 'cloud', 160, y=40, rain=True), C('m', 'man', 90, accent=True, pose='shrug', poseAt=0)]),
        S([L('This bag is very heavy.', by='w', v='woman'), L('I will help you.', by='m'),
           L('He chooses to help at that moment, so he says “will”.', hl=['will'])],
          cast=[C('w', 'woman', 110, pose='hold', holds='bag', out=2), C('w2', 'woman', 110, in_=2, pose='wave'),
                C('m', 'man', 220, face=-1, accent=True, to=165, toAt=1, out=2), C('m2', 'man', 165, face=-1, accent=True, in_=2, pose='hold', holds='bag')]),
        S([L('I will help.'), L('She will help.'), L('They will help.'), L('“Will” is the same with every subject. The verb has no “s”.')],
          board=[B(0, ['I', 'will', 'help.'], r={1: 'b', 2: 'v'}), B(1, ['She', 'will', 'help.'], r={1: 'b', 2: 'v'}),
                 B(2, ['They', 'will', 'help.'], r={1: 'b', 2: 'v'}), B(3, ['She', 'will', 'help.'], r={1: 'b', 2: 'v'}, tag={2: 'no s'})]),
        S([L('The shop will not open on Sunday.', hl=['not']), L("In talk, “will not” becomes “won't”.")],
          cast=[C('h', 'house', 160, s=0.9, label='shop', labelAt=0)],
          board=[B(1, ['will', 'not', "won't"], r={1: 'neg', 2: 'neg'})]),
        S([L('I will call you tonight.', by='w', v='woman')],
          cast=[C('n', 'moon', 260, y=36), C('w', 'woman', 110, accent=True, pose='wave'), C('m', 'man', 200, face=-1)]),
    ],
    'rule': {
        'examples': [{'t': 'I will call you tonight.', 'v': 'woman'}, {'t': 'The shop will not open on Sunday.'},
                     {'t': 'It will be cold tomorrow.'}, {'t': 'I will help you.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'will', 'rest': 'help you'}, {'s': 'you', 'be': 'will', 'rest': 'be late'},
        {'s': 'he', 'be': 'will', 'rest': 'call'}, {'s': 'she', 'be': 'will', 'rest': 'come'},
        {'s': 'it', 'be': 'will', 'rest': 'be cold'}, {'s': 'we', 'be': 'will', 'rest': 'wait'},
        {'s': 'they', 'be': 'will', 'rest': 'win'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right words in the space.', ['will be', 'will is'], 'will be', 'After will, use the simple form: be.',
             before='It', after='cold tomorrow.'),
        pick('Put the right word in the space.', ['help', 'helps'], 'help', 'After will, the verb has no s.', before='She will', after='you.'),
        build('Put the words in the right order.', ['call', 'I', 'you', 'will', 'tonight.'], ['I', 'will', 'call', 'you', 'tonight.'],
              'Will comes before the verb.'),
        fix(['He', 'wills', 'come.'], 1, ['will', 'wills'], 'will', 'Will is the same with every subject.'),
        pick('Put the right words in the space.', ['will not', 'not will'], 'will not', 'Not comes after will.',
             before='The shop', after='open on Sunday.'),
        build('Make a question.', ['Will', 'come?', 'you'], ['Will', 'you', 'come?'], 'Will comes first.'),
    ],
}

# ---------------------------------------------------------------- bigger, more beautiful
LESSONS['comparative'] = {
    'film': [
        S([L('This dog is big. That dog is small.'), L('The big dog is bigger than the small dog.', hl=['bigger'])],
          cast=[C('d1', 'dog', 110, s=1.7, label='big', labelRole='a', labelAt=0), C('d2', 'dog', 230, s=0.8, face=-1, label='small', labelRole='a', labelAt=0)]),
        S([L('For short adjectives, add “er”.', hl=['er']), L('Big, bigger. Small, smaller.', hl=['bigger', 'smaller'])],
          board=[B(0, ['big', 'bigger'], r={1: 'a'}, tag={1: '+ er'}),
                 B(1, ['big', 'bigger', 'small', 'smaller'], r={1: 'a', 3: 'a'}, tag={1: '+ er', 3: '+ er'})]),
        S([L('For long adjectives, use “more”.', hl=['more']), L('Beautiful, more beautiful.', hl=['more'])],
          cast=[C('f1', 'flower', 120, s=0.8), C('f2', 'flower', 200, s=1.3, accent=True)],
          board=[B(1, ['beautiful', 'more', 'beautiful'], r={1: 'a', 2: 'a'}, tag={1: 'more'})]),
        S([L('A cow is bigger than a dog.', hl=['than']), L('Use “than” after it.', hl=['than'])],
          cast=[C('c', 'cow', 110, s=1.1), C('d', 'dog', 240, face=-1)],
          board=[B(1, ['bigger', 'than'], r={0: 'a'}, tag={1: 'compare'})]),
        S([L('Some are different: good, better; bad, worse.', hl=['better', 'worse'])],
          board=[B(0, ['good', 'better', 'bad', 'worse'], r={1: 'a', 3: 'a'})]),
        S([L('My brother is taller than me.', by='g', v='woman')],
          cast=[C('g', 'girl', 110, accent=True, pose='point'), C('m', 'boy', 200, s=0.95, face=-1)]),
    ],
    'rule': {
        'table': [['big', 'bigger'], ['small', 'smaller'], ['beautiful', 'more beautiful'], ['good', 'better'], ['bad', 'worse']],
        'examples': [{'t': 'My brother is taller than me.', 'v': 'woman'}, {'t': 'This book is more interesting than that one.'},
                     {'t': 'A cow is bigger than a dog.'}, {'t': 'Your bag is better than mine.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['big', 'bigger'], 'bigger', 'We compare two animals: bigger.', before='A cow is', after='than a dog.'),
        pick('Put the right words in the space.', ['beautifuller', 'more beautiful'], 'more beautiful', 'Beautiful is long: use more.',
             before='This flower is', after='than that one.'),
        pick('Put the right word in the space.', ['gooder', 'better'], 'better', 'Good, better.', before='Your bag is', after='than mine.'),
        pick('Put the right word in the space.', ['than', 'that'], 'than', 'Use than after a comparative.', before='He is taller', after='me.'),
        fix(['My', 'house', 'is', 'small', 'than', 'yours.'], 3, ['small', 'smaller'], 'smaller', 'Before than, use the comparative: smaller.'),
        build('Put the words in the right order.', ['is', 'than', 'bigger', 'A', 'cow', 'a', 'dog.'], ['A', 'cow', 'is', 'bigger', 'than', 'a', 'dog.'],
              'Bigger, then than.'),
    ],
}

# ---------------------------------------------------------------- the biggest, the most beautiful
LESSONS['superlative'] = {
    'film': [
        S([L('This boy is tall.'), L('This boy is taller.'), L('This boy is the tallest.', hl=['tallest'])],
          cast=[C('a', 'boy', 90, s=0.6, label='tall', labelRole='a', labelAt=0), C('b', 'boy', 160, s=0.72, in_=1, label='taller', labelRole='a', labelAt=1),
                C('c', 'boy', 230, s=0.86, in_=2, accent=True, label='the tallest', labelRole='a', labelAt=2)]),
        S([L('For short adjectives, use “the” and “est”.', hl=['est']), L('Tall, taller, the tallest.', hl=['tallest'])],
          board=[B(0, ['the', 'tallest'], r={1: 'a'}, tag={1: '+ est'}),
                 B(1, ['tall', 'taller', 'the', 'tallest'], r={0: 'a', 1: 'a', 3: 'a'}, tag={1: 'two', 3: 'top of a group'})]),
        S([L('For long adjectives, use “the most”.', hl=['most']), L('This is the most beautiful flower.', hl=['most'])],
          cast=[C('f1', 'flower', 100, s=0.8), C('f2', 'flower', 160, s=0.9), C('f3', 'flower', 230, s=1.4, accent=True)],
          board=[B(1, ['the', 'most', 'beautiful'], r={1: 'a', 2: 'a'})]),
        S([L('Good, better, the best.', hl=['best']), L('Bad, worse, the worst.', hl=['worst'])],
          board=[B(0, ['good', 'better', 'the', 'best'], r={3: 'a'}), B(1, ['bad', 'worse', 'the', 'worst'], r={3: 'a'})]),
        S([L('She is the tallest girl in the class.', hl=['tallest'])],
          cast=[C('g1', 'girl', 80, s=0.66), C('g2', 'girl', 130, s=0.7), C('g3', 'girl', 190, s=0.86, accent=True), C('g4', 'girl', 245, s=0.68)]),
    ],
    'rule': {
        'table': [['tall', 'taller, the tallest'], ['big', 'bigger, the biggest'], ['beautiful', 'more beautiful, the most beautiful'],
                  ['good', 'better, the best'], ['bad', 'worse, the worst']],
        'examples': [{'t': 'She is the tallest girl in the class.'}, {'t': 'This is the best day of my life.'},
                     {'t': 'The cow is the biggest animal here.'}, {'t': 'This is the most beautiful flower.'}],
    },
    'tasks': [
        pick('Put the right words in the space.', ['taller', 'the tallest'], 'the tallest', 'The top of the class: the tallest.',
             before='She is', after='girl in the class.'),
        pick('Put the right words in the space.', ['the most beautiful', 'the beautifulest'], 'the most beautiful',
             'Beautiful is long: the most.', before='This is', after='flower.'),
        pick('Put the right words in the space.', ['the best', 'the goodest'], 'the best', 'Good, better, the best.',
             before='This is', after='day of my life.'),
        pick('Put the right words in the space.', ['bigger', 'the biggest'], 'bigger', 'Two animals and than: bigger.',
             before='A cow is', after='than a dog.'),
        fix(['It', 'is', 'the', 'small', 'house', 'here.'], 3, ['small', 'smallest'], 'smallest', 'After the, use est: the smallest.'),
        build('Put the words in the right order.', ['the', 'tallest.', 'is', 'She'], ['She', 'is', 'the', 'tallest.'], 'The comes before tallest.'),
    ],
}

# ---------------------------------------------------------------- slowly, quickly, well
LESSONS['adverb'] = {
    'film': [
        S([L('He walks slowly.', hl=['slowly']), L('She walks quickly.', hl=['quickly'])],
          cast=[C('m', 'man', 40, to=110, toAt=0, dur=6000), C('w', 'woman', 40, in_=1, to=280, toAt=1, dur=1000, accent=True)]),
        S([L('“Slowly” says how he walks.'), L('Many adverbs are an adjective and “ly”.', hl=['ly'])],
          board=[B(0, ['slow', 'slowly'], r={0: 'a'}, tag={1: '+ ly'}),
                 B(1, ['slow', 'slowly', 'quick', 'quickly'], r={0: 'a', 2: 'a'}, tag={1: '+ ly', 3: '+ ly'})]),
        S([L('He drives very slowly.', hl=['slowly']), L('An adverb says more about a verb: how, when or where.', hl=['adverb'])],
          cast=[C('c', 'car', 40, to=120, toAt=0, dur=7000)],
          board=[B(1, ['He', 'drives', 'very', 'slowly.'], r={1: 'v'}, tag={1: 'verb', 3: 'how'})]),
        S([L('She is a good cook.'), L('She cooks well.', hl=['well']), L('“Good” is an adjective. Its adverb is “well”.')],
          cast=[C('w', 'woman', 120, accent=True), C('t', 'table', 220), C('a', 'apple', 210, y=TOP), C('e', 'egg', 232, y=TOP)],
          board=[B(0, ['a', 'good', 'cook'], r={1: 'a'}, tag={1: 'adjective'}),
                 B(1, ['She', 'cooks', 'well.'], r={1: 'v'}, tag={2: 'adverb'})]),
        S([L('The children ran quickly to the door.', hl=['quickly'])],
          cast=[C('d', 'door', 280), C('c', 'boy', 30, n=2, gap=30, to=200, toAt=0, dur=1100), C('g', 'girl', 0, to=180, toAt=0, dur=1100)], min=2600),
    ],
    'rule': {
        'table': [['slow', 'slowly'], ['quick', 'quickly'], ['bad', 'badly'], ['good', 'well']],
        'examples': [{'t': 'He drives very slowly.'}, {'t': 'The children ran quickly to the door.'}, {'t': 'She cooks well.'},
                     {'t': 'Please speak slowly.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['slow', 'slowly'], 'slowly', 'It says how he drives: slowly.', before='He drives very', after='.'),
        pick('Put the right word in the space.', ['quick', 'quickly'], 'quickly', 'It says how they ran: quickly.',
             before='The children ran', after='to the door.'),
        pick('Put the right word in the space.', ['good', 'well'], 'well', 'It says how she cooks: well.', before='She cooks', after='.'),
        pick('Put the right word in the space.', ['good', 'well'], 'good', 'Before a noun, use the adjective: good.', before='She is a', after='cook.'),
        fix(['Please', 'speak', 'slow.'], 2, ['slow', 'slowly'], 'slowly', 'It says how to speak: slowly.'),
        tap('Touch the adverb.', ['He', 'walks', 'slowly', 'to', 'school.'], [2], '“Slowly” says how he walks.'),
    ],
}

# ---------------------------------------------------------------- how much? how many?
LESSONS['much-many'] = {
    'film': [
        S([L('How many apples are there?', by='g', v='woman'), L('There are three.', by='m')],
          cast=[C('g', 'girl', 70, accent=True), C('t', 'table', 160), C('a', 'apple', 140, y=TOP, n=3, gap=20, s=1.1), C('m', 'man', 250, face=-1)]),
        S([L('How much milk is there?', by='g', v='woman'), L('There is not much.', by='m')],
          cast=[C('g', 'girl', 70, accent=True), C('t', 'table', 160), C('b', 'bottle', 160, y=TOP), C('m', 'man', 250, face=-1, pose='shrug', poseAt=1)]),
        S([L('“How many” is for countable nouns.', hl=['many']), L('“How much” is for uncountable nouns.', hl=['much'])],
          board=[B(0, ['How', 'many', 'eggs?'], r={0: 'q', 1: 'q'}, tag={2: 'countable'}),
                 B(1, ['How', 'much', 'milk?'], r={0: 'q', 1: 'q'}, tag={2: 'uncountable'})]),
        S([L('How much is this bag?', by='w', v='woman'), L('We also use “how much” to ask the price.')],
          cast=[C('w', 'woman', 110, accent=True, pose='hold', holds='bag'), C('m', 'man', 220, face=-1)]),
        S([L('How many people are in the room?')],
          cast=[C('m', 'man', 70), C('w', 'woman', 130), C('b', 'boy', 190), C('g', 'girl', 240)], min=2400),
    ],
    'rule': {
        'table': [['countable nouns', 'how many'], ['uncountable nouns, price', 'how much']],
        'examples': [{'t': 'How many people are in the room?'}, {'t': 'How much milk is there?'},
                     {'t': 'How many brothers do you have?'}, {'t': 'How much is this bag?', 'v': 'woman'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['many', 'much'], 'many', 'Brothers are countable: many.', before='How', after='brothers do you have?'),
        pick('Put the right word in the space.', ['many', 'much'], 'much', 'Water is uncountable: much.', before='How', after='water do you drink?'),
        pick('Put the right word in the space.', ['many', 'much'], 'many', 'People are countable: many.', before='How', after='people are in the room?'),
        pick('Put the right word in the space.', ['many', 'much'], 'much', 'To ask the price: how much.', before='How', after='is this bag?'),
        fix(['How', 'much', 'eggs', 'do', 'we', 'have?'], 1, ['many', 'much'], 'many', 'Eggs are countable: how many.'),
        build('Make a question.', ['milk', 'How', 'is', 'there?', 'much'], ['How', 'much', 'milk', 'is', 'there?'], 'How much, then milk.'),
    ],
}

# ---------------------------------------------------------------- must and have to
LESSONS['must-have-to'] = {
    'film': [
        S([L('We have to wear a uniform at school.', by='b'), L('“Must” and “have to” say that something is necessary.')],
          cast=[C('b', 'boy', 90, accent=True), C('g', 'girl', 135), C('h', 'house', 250, s=0.8, label='school', labelAt=0)]),
        S([L('I must go now.', hl=['must']), L('I have to go now.', hl=['have', 'to'])],
          cast=[C('k', 'clock', 250, y=44, h=8), C('m', 'man', 90, accent=True, to=180, toAt=1)],
          board=[B(0, ['I', 'must', 'go', 'now.'], r={1: 'b', 2: 'v'}), B(1, ['I', 'have', 'to', 'go', 'now.'], r={1: 'b', 2: 'b', 3: 'v'})]),
        S([L('You must not touch the fire.', by='m'), L('“Must not” means it is not allowed.', hl=['must', 'not'])],
          cast=[C('m', 'man', 90, accent=True, pose='point'), C('f', 'fire', 180), C('b', 'boy', 250, face=-1, pose='reach', poseEnd=0)]),
        S([L('You do not have to come.', by='w', v='woman'), L('“Do not have to” means it is not necessary. You can choose.')],
          cast=[C('w', 'woman', 110, accent=True), C('m', 'man', 210, face=-1, pose='shrug', poseAt=1)]),
        S([L('“Must not”: not allowed.'), L('“Do not have to”: not necessary.')],
          board=[B(0, ['must', 'not'], r={0: 'b', 1: 'neg'}, tag={0: 'not allowed'}),
                 B(1, ['must', 'not', 'do', 'not', 'have', 'to'], r={0: 'b', 1: 'neg', 3: 'neg'}, tag={0: 'not allowed', 4: 'not necessary'})]),
    ],
    'rule': {
        'table': [['necessary', 'must, have to'], ['not allowed', 'must not'], ['not necessary', 'do not have to']],
        'examples': [{'t': 'We have to wear a uniform at school.'}, {'t': 'You must not touch the fire.'},
                     {'t': 'You do not have to come.', 'v': 'woman'}, {'t': 'I must go now.'}],
    },
    'tasks': [
        pick('Put the right words in the space.', ['must not', 'do not have to'], 'must not', 'It is not allowed: must not.',
             before='You', after='smoke here. It is not allowed.'),
        pick('Put the right words in the space.', ['must not', 'do not have to'], 'do not have to', 'It is not necessary: do not have to.',
             before='You', after='come. It is your choice.'),
        pick('Put the right words in the space.', ['has to', 'have to'], 'has to', 'With she: has to.', before='She', after='go now.'),
        pick('Put the right words in the space.', ['go', 'to go'], 'go', 'There is no to after must.', before='I must', after='now.'),
        fix(['He', 'have', 'to', 'work', 'today.'], 1, ['have', 'has'], 'has', 'With he: has to.'),
        build('Put the words in the right order.', ['to', 'wear', 'We', 'a', 'uniform.', 'have'], ['We', 'have', 'to', 'wear', 'a', 'uniform.'],
              'Have to, then the verb.'),
    ],
}

# ---------------------------------------------------------------- should
LESSONS['should'] = {
    'film': [
        S([L('I am so tired.', by='m'), L('You should drink more water.', by='w', v='woman'), L('“Should” says what is a good idea.', hl=['should'])],
          cast=[C('m', 'man', 110, pose='sad'), C('w', 'woman', 210, face=-1, accent=True, pose='give', holds='glass', poseAt=1)]),
        S([L('Should I take an umbrella?', by='g', v='woman'), L('Yes, you should.', by='w', v='woman')],
          cast=[C('c', 'cloud', 160, y=36, rain=True), C('g', 'girl', 100, accent=True), C('w', 'woman', 210, face=-1, pose='nod', poseAt=1)]),
        S([L('You should go.'), L('You should not go.', hl=['not']), L('“Should not”: it is not a good idea.')],
          board=[B(0, ['You', 'should', 'go.'], r={1: 'b', 2: 'v'}), B(1, ['You', 'should', 'not', 'go.'], r={1: 'b', 2: 'neg', 3: 'v'})]),
        S([L('It is late. You should go to bed early.', by='w', v='woman')],
          cast=[C('n', 'moon', 260, y=36), C('w', 'woman', 100, accent=True, pose='point'), C('b', 'boy', 190, face=-1, pose='sad')]),
    ],
    'rule': {
        'examples': [{'t': 'You should go to bed early.'}, {'t': 'Should we wait for them?'},
                     {'t': 'You should drink more water.', 'v': 'woman'}, {'t': 'You should not eat so much sugar.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'should', 'rest': 'rest'}, {'s': 'you', 'be': 'should', 'rest': 'go to bed'},
        {'s': 'he', 'be': 'should', 'rest': 'drink water'}, {'s': 'she', 'be': 'should', 'rest': 'wait'},
        {'s': 'it', 'be': 'should', 'rest': 'stop'}, {'s': 'we', 'be': 'should', 'rest': 'go home'},
        {'s': 'they', 'be': 'should', 'rest': 'come'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right words in the space.', ['should', 'should not'], 'should', 'Bed is a good idea for a tired person.',
             before='You are tired. You', after='go to bed.'),
        pick('Put the right words in the space.', ['should', 'should not'], 'should not', 'Going out with no coat is not a good idea.',
             before='It is very cold. You', after='go out with no coat.'),
        pick('Put the right words in the space.', ['take', 'to take'], 'take', 'After should, the simple form: take.',
             before='Should I', after='an umbrella?'),
        build('Make a question.', ['we', 'Should', 'wait?'], ['Should', 'we', 'wait?'], 'Should comes first.'),
        fix(['She', 'shoulds', 'rest.'], 1, ['should', 'shoulds'], 'should', 'Should is the same with every subject.'),
        pick('Put the right word in the space.', ['eat', 'eats'], 'eat', 'After should, the verb has no s.', before='He should', after='more fruit.'),
    ],
}

# ---------------------------------------------------------------- the past continuous
LESSONS['past-continuous'] = {
    'film': [
        S([L('I was walking home', by='m'), L('when it started to rain.', hl=['started'])],
          cast=[C('m', 'man', 40, accent=True, to=200, toAt=0, dur=4000), C('c', 'cloud', 200, y=36, rain=True, in_=1), C('h', 'house', 280, s=0.7)]),
        S([L('I was walking.', hl=['was', 'walking']), L('“Was” or “were”, then the verb with “ing”. This is the past continuous.', hl=['past', 'continuous'])],
          board=[B(0, ['I', 'was', 'walking.'], r={1: 'b', 2: 'v'}, tag={2: '+ ing'})]),
        S([L('We were having a meal at eight.', by='w', v='woman'), L('At eight, the meal was going on.')],
          cast=[C('k', 'clock', 160, y=40, h=8), C('w', 'woman', 90, accent=True), C('t', 'table', 160), C('a', 'apple', 150, y=TOP),
                C('g', 'glass', 172, y=TOP), C('m', 'man', 230, face=-1)]),
        S([L('The long action: I was walking.', hl=['walking']), L('The short action that came in the middle: it started to rain.', hl=['started'])],
          board=[B(0, ['was', 'walking'], r={0: 'b', 1: 'v'}, tag={1: 'long'}),
                 B(1, ['was', 'walking', 'started'], r={0: 'b', 1: 'v', 2: 'v'}, tag={1: 'long', 2: 'short'})]),
        S([L('What were you doing?', by='w', v='woman'), L('I was reading.', by='b')],
          cast=[C('w', 'woman', 100, accent=True), C('b', 'boy', 210, face=-1, pose='hold', holds='book', poseAt=1)]),
    ],
    'rule': {
        'table': [['I, he, she, it', 'was + ing'], ['you, we, they', 'were + ing']],
        'examples': [{'t': 'We were having a meal at eight.', 'v': 'woman'}, {'t': 'What were you doing?', 'v': 'woman'},
                     {'t': 'I was walking home when it started to rain.'}, {'t': 'They were not sleeping.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'was', 'rest': 'walking'}, {'s': 'you', 'be': 'were', 'rest': 'reading'},
        {'s': 'he', 'be': 'was', 'rest': 'sleeping'}, {'s': 'she', 'be': 'was', 'rest': 'cooking'},
        {'s': 'it', 'be': 'was', 'rest': 'raining'}, {'s': 'we', 'be': 'were', 'rest': 'eating'},
        {'s': 'they', 'be': 'were', 'rest': 'playing'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right word in the space.', ['was', 'were'], 'were', 'With we: were.', before='We', after='having a meal at eight.'),
        pick('Put the right word in the space.', ['walking', 'walked'], 'walking', 'After was, use the verb with ing.', before='I was', after='home.'),
        pick('Put the right word in the space.', ['was', 'were'], 'was', 'With she: was.', before='She', after='reading when I came.'),
        build('Make a question.', ['were', 'What', 'doing?', 'you'], ['What', 'were', 'you', 'doing?'], 'What, then were, then you.'),
        fix(['They', 'was', 'sleeping.'], 1, ['was', 'were'], 'were', 'With they: were.'),
        pick('Put the right words in the space.', ['started', 'was starting'], 'started', 'The short action uses the past simple.',
             before='I was walking home when it', after='to rain.'),
    ],
}

# ---------------------------------------------------------------- clauses
LESSONS['clause'] = {
    'film': [
        S([L('She cooks.'), L('He cleans the house.')],
          cast=[C('w', 'woman', 28, accent=True), C('t', 'table', 75, s=0.8), C('m', 'man', 290, face=-1, in_=1)],
          board=[B(0, ['She', 'cooks.'], r={0: 'p', 1: 'v'}, tag={0: 'subject', 1: 'verb'}),
                 B(1, ['He', 'cleans', 'the', 'house.'], r={0: 'p', 1: 'v'}, tag={0: 'subject', 1: 'verb'})]),
        S([L('Each one has a subject and a verb.'), L('A group of words with its own subject and verb is a clause.', hl=['clause'])],
          board=[B(0, ['She', 'cooks.', 'He', 'cleans.'], r={0: 'p', 1: 'v', 2: 'p', 3: 'v'}),
                 B(1, ['She', 'cooks.', 'He', 'cleans.'], r={0: 'p', 1: 'v', 2: 'p', 3: 'v'}, tag={1: 'clause', 3: 'clause'})]),
        S([L('She cooks and he cleans the house.', hl=['and']), L('A conjunction joins the two clauses.', hl=['conjunction'])],
          board=[B(0, ['She', 'cooks', 'and', 'he', 'cleans.'], r={0: 'p', 1: 'v', 3: 'p', 4: 'v'}),
                 B(1, ['She', 'cooks', 'and', 'he', 'cleans.'], r={0: 'p', 1: 'v', 2: 'ok', 3: 'p', 4: 'v'}, tag={2: 'conjunction'})]),
        S([L('I was tired, so I went to bed.', by='m'), L('Two subjects, two verbs: two clauses in one sentence.')],
          cast=[C('n', 'moon', 260, y=36), C('m', 'man', 120, accent=True, pose='sad'), C('h', 'house', 210, s=0.8)]),
        S([L('The dog runs.'), L('One subject, one verb: one clause.')],
          cast=[C('d', 'dog', 40, to=250, toAt=0)],
          board=[B(1, ['The', 'dog', 'runs.'], r={1: 'n', 2: 'v'}, tag={2: 'one clause'})]),
    ],
    'rule': {
        'examples': [{'t': 'She cooks and he cleans the house.'}, {'t': 'I stayed at home because I was ill.'},
                     {'t': 'I was tired, so I went to bed.'}, {'t': 'She plays the piano.'}],
    },
    'tasks': [
        pick('How many clauses are in "I was tired, so I went to bed"?', ['one', 'two'], 'two',
             'I was tired. I went to bed. Two subjects and two verbs.'),
        pick('How many clauses are in "The dog runs"?', ['one', 'two'], 'one', 'One subject and one verb.'),
        tap('Touch the word that joins the two clauses.', ['I', 'stayed', 'home', 'because', 'I', 'was', 'ill.'], [3],
            'Because joins the two clauses.'),
        tap('Touch the verbs.', ['She', 'cooks', 'and', 'he', 'cleans.'], [1, 4], 'Cooks and cleans: two verbs, two clauses.'),
        build('Put the words in the right order.', ['and', 'She', 'he', 'cooks', 'cleans.'], ['She', 'cooks', 'and', 'he', 'cleans.'],
              'Clause, conjunction, clause.'),
        pick('Put the right word in the space.', ['so', 'because'], 'because', 'Being ill is the reason: because.',
             before='I stayed at home', after='I was ill.'),
    ],
}
