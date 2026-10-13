"""Elementary school lessons, part 2: prepositions of place and time, how often, the present
continuous, simple or continuous, question words, joining words, countable nouns, there is,
some and any, was and were, the past simple."""
from lessons_kit import L, C, B, S, pick, build, fix, tap, TOP  # noqa: F401

LESSONS = {}

# ---------------------------------------------------------------- in, on, under, next to
LESSONS['preposition-place'] = {
    'film': [
        S([L('The ball is in the box.', hl=['in'])],
          cast=[C('o', 'ball', 160, y=124), C('x', 'box', 160, s=1.4, label='in', labelRole='n', labelAt=0)], min=2400),
        S([L('The ball is on the box.', hl=['on'])],
          cast=[C('x', 'box', 160, s=1.4, label='on', labelRole='n', labelAt=0), C('o', 'ball', 160, y=118)], min=2400),
        S([L('The cat is under the table.', hl=['under']), L('The book is on the table.', hl=['on'])],
          cast=[C('t', 'table', 160), C('c', 'cat', 160, s=0.9, label='under', labelRole='n', labelAt=0),
                C('b', 'book', 175, y=TOP, in_=1)]),
        S([L('The dog is next to the house.', hl=['next', 'to']), L('The girl is between the boys.', hl=['between'])],
          cast=[C('h', 'house', 60, s=0.8), C('d', 'dog', 115), C('b1', 'boy', 195, in_=1), C('g', 'girl', 235, in_=1, accent=True),
                C('b2', 'boy', 275, in_=1, face=-1)]),
        S([L('The boy is behind the tree.', hl=['behind']), L('The girl is in front of the house.', hl=['in', 'front', 'of'])],
          cast=[C('b', 'boy', 80, accent=True), C('t', 'tree', 85), C('h', 'house', 230, s=0.9, in_=1), C('g', 'girl', 230, in_=1)]),
        S([L('In, on, under and next to are prepositions.', hl=['prepositions']),
           L('A preposition shows where one thing is, next to another.')],
          board=[B(0, ['in', 'on', 'under', 'behind'], r={0: 'ok', 1: 'ok', 2: 'ok', 3: 'ok'})]),
    ],
    'rule': {
        'examples': [{'t': 'The cat is under the table.'}, {'t': 'The book is on the shelf.'}, {'t': 'The ball is in the box.'},
                     {'t': 'The dog is next to the house.'}],
    },
    'tasks': [
        pick('Which word means inside?', ['in', 'on', 'under'], 'in', 'In: inside something.'),
        pick('Which word means on top of?', ['in', 'on', 'under'], 'on', 'On: on top of something.'),
        pick('Which word means lower than?', ['behind', 'on', 'under'], 'under', 'Under: lower than something.'),
        pick('Put the right word in the space.', ['between', 'under', 'in'], 'between', 'Between: with one on each side.',
             before='The girl is', after='the two boys.'),
        build('Put the words in the right order.', ['is', 'the', 'box.', 'in', 'The', 'ball'], ['The', 'ball', 'is', 'in', 'the', 'box.'],
              'The ball is, then where: in the box.'),
        tap('Touch the preposition.', ['The', 'book', 'is', 'on', 'the', 'table.'], [3], 'On shows where the book is.'),
    ],
}

# ---------------------------------------------------------------- at, on, in for time
LESSONS['preposition-time'] = {
    'film': [
        S([L('The shop closes at six.', hl=['at']), L('At is for a time on the clock.', hl=['at'])],
          cast=[C('k', 'clock', 150, y=46, h=6), C('h', 'house', 240, s=0.8, label='shop', labelAt=0), C('m', 'man', 80, accent=True)]),
        S([L('We play games on Monday.', hl=['on']), L('On is for a day: on Monday, on my birthday.', hl=['on'])],
          board=[B(0, ['on', 'Monday'], r={0: 'ok'}, tag={1: 'day'}), B(1, ['on', 'my', 'birthday'], r={0: 'ok'}, tag={2: 'day'})]),
        S([L('My birthday is in May.', hl=['in']), L('In is for a month or a year: in May, in this year.', hl=['in'])],
          board=[B(0, ['in', 'May'], r={0: 'ok'}, tag={1: 'month'}), B(1, ['in', 'this', 'year'], r={0: 'ok'}, tag={2: 'year'})]),
        S([L('We say in the morning, in the afternoon and in the evening.', hl=['in']), L('But we say at night.', hl=['at'])],
          cast=[C('s', 'sun', 60, y=80, to=260, toAt=0, out=1), C('n', 'moon', 230, y=40, in_=1), C('h', 'house', 150, s=0.9)]),
        S([L('At six.', hl=['at']), L('On Monday.', hl=['on']), L('In May.', hl=['in'])],
          board=[B(0, ['at', 'six'], r={0: 'ok'}, tag={1: 'clock'}), B(1, ['at', 'six', 'on', 'Monday'], r={0: 'ok', 2: 'ok'}, tag={1: 'clock', 3: 'day'}),
                 B(2, ['at', 'six', 'on', 'Monday', 'in', 'May'], r={0: 'ok', 2: 'ok', 4: 'ok'}, tag={1: 'clock', 3: 'day', 5: 'month'})]),
    ],
    'rule': {
        'table': [['a time on the clock', 'at'], ['a day', 'on'], ['a month, a year, part of a day', 'in']],
        'examples': [{'t': 'The shop closes at six.'}, {'t': 'We play games in the afternoon.'}, {'t': 'I see her on Monday.'},
                     {'t': 'My birthday is in May.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['at', 'on', 'in'], 'at', 'At for a time on the clock.', before='The shop closes', after='six.'),
        pick('Put the right word in the space.', ['at', 'on', 'in'], 'on', 'On for a day.', before='I see her', after='Monday.'),
        pick('Put the right word in the space.', ['at', 'on', 'in'], 'in', 'In for a month.', before='My birthday is', after='May.'),
        pick('Put the right word in the space.', ['at', 'on', 'in'], 'in', 'In for a part of the day.', before='We play games', after='the afternoon.'),
        fix(['I', 'sleep', 'in', 'night.'], 2, ['at', 'in', 'on'], 'at', 'We say at night.'),
        pick('Put the right word in the space.', ['at', 'on', 'in'], 'on', 'A birthday is a day: on.', before='We have a party', after='my birthday.'),
    ],
}

# ---------------------------------------------------------------- always, often, never
LESSONS['how-often'] = {
    'film': [
        S([L('Always, usually, often, sometimes, never.', hl=['always', 'usually', 'often', 'sometimes', 'never']),
           L('These words say how often something happens.')],
          board=[B(0, ['always', 'usually', 'often', 'sometimes', 'never'],
                   tag={0: 'every time', 1: 'most times', 2: 'many times', 3: 'some times', 4: 'no time'})]),
        S([L('I always drink milk in the morning.', by='m'), L('Every morning, with no change.', hl=['always'])],
          cast=[C('s', 'sun', 50, y=80), C('m', 'man', 160, accent=True, pose='eat', holds='glass')]),
        S([L('I walk to school.'), L('I often walk to school.', hl=['often']), L('These words come before most verbs.')],
          board=[B(0, ['I', 'walk', 'to', 'school.'], r={1: 'v'}),
                 B(1, ['I', 'often', 'walk', 'to', 'school.'], r={1: 'ok', 2: 'v'}, tag={1: 'before the verb'})]),
        S([L('She is happy.'), L('She is always happy.', hl=['always']), L('They come after am, is and are.')],
          cast=[C('w', 'woman', 160, accent=True, pose='wave', poseAt=1)],
          board=[B(0, ['She', 'is', 'happy.'], r={1: 'b'}),
                 B(1, ['She', 'is', 'always', 'happy.'], r={1: 'b', 2: 'ok'}, tag={2: 'after is'})]),
        S([L('He is never late.', hl=['never']), L('He comes at eight every day.')],
          cast=[C('k', 'clock', 240, y=46, h=8), C('m', 'man', 50, accent=True, to=180, toAt=0)]),
    ],
    'rule': {
        'examples': [{'t': 'I always drink milk in the morning.'}, {'t': 'He is never late.'}, {'t': 'We often walk to school.'},
                     {'t': 'She sometimes reads at night.'}],
    },
    'tasks': [
        build('Put the words in the right order.', ['always', 'I', 'milk.', 'drink'], ['I', 'always', 'drink', 'milk.'],
              'Always comes before the verb.'),
        build('Put the words in the right order.', ['is', 'late.', 'never', 'He'], ['He', 'is', 'never', 'late.'],
              'Never comes after is.'),
        pick('Put the right word in the space.', ['always', 'never'], 'never', 'He comes on time every day, so he is never late.',
             before='He comes on time every day. He is', after='late.'),
        pick('Which word means "not one time"?', ['never', 'often', 'always'], 'never', 'Never: not one time.'),
        pick('Which word means "every time"?', ['always', 'sometimes', 'never'], 'always', 'Always: every time.'),
        tap('Touch the word that says how often.', ['We', 'sometimes', 'play', 'in', 'the', 'garden.'], [1], 'Sometimes says how often.'),
    ],
}

# ---------------------------------------------------------------- the present continuous
LESSONS['present-continuous'] = {
    'film': [
        S([L('Look! It is raining.', by='w', v='woman'), L('It is happening now, at this moment.')],
          cast=[C('c', 'cloud', 200, y=40, rain=True), C('w', 'woman', 90, accent=True, pose='point')]),
        S([L('I walk.'), L('I am walking.', hl=['walking']), L('Am, is or are, then the verb with ing.')],
          cast=[C('m', 'man', 60, accent=True, to=260, toAt=1)],
          board=[B(0, ['I', 'walk.'], r={1: 'v'}), B(1, ['I', 'am', 'walking.'], r={1: 'b', 2: 'v'}, tag={2: '+ ing'})]),
        S([L('The children are playing in the garden.', hl=['playing']),
           L('This is the present continuous.', hl=['present', 'continuous'])],
          cast=[C('c', 'boy', 90, n=2, gap=60, pose='wave'), C('g', 'girl', 120, pose='run'), C('o', 'ball', 230, to=170, toAt=0),
                C('t', 'tree', 280, s=0.8)]),
        S([L('She is sleeping.'), L('She is not sleeping.', hl=['not']), L('Is she sleeping?', hl=['is'])],
          board=[B(0, ['She', 'is', 'sleeping.'], r={1: 'b', 2: 'v'}), B(1, ['She', 'is', 'not', 'sleeping.'], r={1: 'b', 2: 'neg', 3: 'v'}),
                 B(2, ['Is', 'she', 'sleeping?'], r={0: 'b', 2: 'v'})]),
        S([L('What are you doing?', by='w', v='woman'), L('I am reading.', by='b')],
          cast=[C('w', 'woman', 100, accent=True), C('b', 'boy', 210, face=-1, pose='hold', holds='book', poseAt=1)]),
    ],
    'rule': {
        'examples': [{'t': 'The children are playing in the garden.'}, {'t': 'What are you doing?', 'v': 'woman'},
                     {'t': 'Look! It is raining.', 'v': 'woman'}, {'t': 'She is not sleeping.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'am', 'rest': 'walking'}, {'s': 'you', 'be': 'are', 'rest': 'reading'},
        {'s': 'he', 'be': 'is', 'rest': 'eating'}, {'s': 'she', 'be': 'is', 'rest': 'sleeping'},
        {'s': 'it', 'be': 'is', 'rest': 'raining'}, {'s': 'we', 'be': 'are', 'rest': 'playing'},
        {'s': 'they', 'be': 'are', 'rest': 'swimming'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right word in the space.', ['is', 'are'], 'are', 'The children are more than one: are.', before='The children', after='playing.'),
        pick('Put the right word in the space.', ['eating', 'eat'], 'eating', 'After am, use the verb with ing.', before='I am', after='an apple.'),
        build('Make a question.', ['you', 'Are', 'listening?'], ['Are', 'you', 'listening?'], 'Are comes first.'),
        fix(['She', 'is', 'sleep', 'now.'], 2, ['sleep', 'sleeping'], 'sleeping', 'After is, use the verb with ing.'),
        pick('Put the right word in the space.', ['raining', 'rain'], 'raining', 'It is, then the verb with ing.', before='Look! It is', after='.'),
        build('Put the words in the right order.', ['not', 'He', 'is', 'working.'], ['He', 'is', 'not', 'working.'], 'Not comes after is.'),
    ],
}

# ---------------------------------------------------------------- every day, or right now?
LESSONS['simple-or-continuous'] = {
    'film': [
        S([L('I usually walk to school.', by='b'), L('But today I am going by car.', by='b')],
          cast=[C('b', 'boy', 50, accent=True, to=150, toAt=0, out=1), C('c', 'car', 40, in_=1, to=205, toAt=1), C('h', 'house', 285, s=0.6)]),
        S([L('Again and again: the present simple.'), L('Now, or for a short time: the present continuous.')],
          board=[B(0, ['I', 'walk', 'every', 'day.'], r={1: 'v'}, tag={1: 'again and again'}),
                 B(1, ['I', 'am', 'walking', 'now.'], r={1: 'b', 2: 'v'}, tag={2: 'now'})]),
        S([L('He works in a shop.'), L('Look, he is working now.', hl=['working'])],
          cast=[C('h', 'house', 230, s=0.9, label='shop', labelAt=0), C('m', 'man', 120, accent=True, pose='give', poseAt=1),
                C('w', 'woman', 175, face=-1, in_=1)]),
        S([L('She knows the answer.', hl=['knows']), L('Know, like, want and need are about what we think or feel.'),
           L('We do not use them with ing.')],
          cast=[C('g', 'girl', 160, accent=True, pose='reach')],
          board=[B(0, ['She', 'knows', 'the', 'answer.'], r={1: 'v'}),
                 B(2, ['She', 'is', 'knowing.'], r={2: 'v'}, x=[2])]),
    ],
    'rule': {
        'table': [['again and again, always true', 'I walk'], ['now, for a short time', 'I am walking']],
        'examples': [{'t': 'I usually walk to school, but today I am going by car.'}, {'t': 'She knows the answer.'},
                     {'t': 'He works in a shop.'}, {'t': 'Look, he is working now.'}],
    },
    'tasks': [
        pick('Put the right words in the space.', ['walk', 'am walking'], 'walk', 'Every day: the present simple.',
             before='I', after='to school every day.'),
        pick('Put the right words in the space.', ['rains', 'is raining'], 'is raining', 'Look! It is happening now.',
             before='Look! It', after='.'),
        pick('Put the right words in the space.', ['know', 'am knowing'], 'know', 'Know is not used with ing.', before='I', after='the answer.'),
        pick('Put the right words in the space.', ['sleeps', 'is sleeping'], 'is sleeping', 'Be quiet: it is happening now.',
             before='Be quiet! The baby', after='.'),
        fix(['He', 'go', 'to', 'school', 'every', 'day.'], 1, ['go', 'goes', 'going'], 'goes',
            'Every day: the present simple, with s after he.'),
        build('Make a question.', ['are', 'you', 'What', 'doing?'], ['What', 'are', 'you', 'doing?'], 'What, then are, then you.'),
    ],
}

# ---------------------------------------------------------------- who, what, where ...
LESSONS['question-words'] = {
    'film': [
        S([L('Where is my bag?', by='w', v='woman'), L('Where asks about a place.', hl=['where'])],
          cast=[C('w', 'woman', 90, accent=True, pose='shrug'), C('t', 'table', 220), C('b', 'bag', 220, in_=1)]),
        S([L('Who is for people. What is for things.', hl=['who', 'what']),
           L('Where is for places. When is for time.', hl=['where', 'when']),
           L('Why asks for a reason. How asks for the way.', hl=['why', 'how'])],
          board=[B(0, ['who', 'what'], r={0: 'q', 1: 'q'}, tag={0: 'people', 1: 'things'}),
                 B(1, ['who', 'what', 'where', 'when'], r={0: 'q', 1: 'q', 2: 'q', 3: 'q'}, tag={0: 'people', 1: 'things', 2: 'place', 3: 'time'}),
                 B(2, ['who', 'what', 'where', 'when', 'why', 'how'], r={0: 'q', 1: 'q', 2: 'q', 3: 'q', 4: 'q', 5: 'q'},
                   tag={0: 'people', 1: 'things', 2: 'place', 3: 'time', 4: 'reason', 5: 'way'})]),
        S([L('Where do you live?', hl=['where']), L('The question word comes first. Then comes the rest of the question.')],
          board=[B(0, ['Do', 'you', 'live', 'here?'], r={0: 'q'}), B(1, ['Where', 'do', 'you', 'live?'], r={0: 'q', 1: 'q'})]),
        S([L('Why is she sad?', by='b'), L('Her cat is ill.', by='m')],
          cast=[C('b', 'boy', 70, accent=True), C('m', 'man', 150, face=-1), C('g', 'girl', 230, face=-1, pose='sad'), C('c', 'cat', 280, face=-1)]),
        S([L('How do you go to school?', by='w', v='woman'), L('I walk.', by='b')],
          cast=[C('w', 'woman', 90, accent=True), C('b', 'boy', 190, face=-1, to=290, toAt=1)]),
    ],
    'rule': {
        'table': [['people', 'who'], ['things', 'what'], ['places', 'where'], ['time', 'when'], ['a reason', 'why'], ['the way', 'how']],
        'examples': [{'t': 'Where is my bag?', 'v': 'woman'}, {'t': 'How do you go to school?'}, {'t': 'Who is that man?'},
                     {'t': 'Why is she sad?'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['Where', 'When', 'Who'], 'Where', 'The answer is a place: where.',
             after='do you live? In London.'),
        pick('Put the right word in the space.', ['Who', 'What', 'When'], 'Who', 'The answer is a person: who.',
             after='is that man? He is my father.'),
        pick('Put the right word in the space.', ['When', 'Where', 'What'], 'When', 'The answer is a time: when.',
             after='do you get up? At seven.'),
        pick('Put the right word in the space.', ['Why', 'How', 'Who'], 'Why', 'The answer is a reason: why.',
             after='are you sad? Because my dog is ill.'),
        build('Make a question.', ['is', 'Where', 'bag?', 'my'], ['Where', 'is', 'my', 'bag?'], 'Where comes first.'),
        build('Make a question.', ['do', 'How', 'you', 'school?', 'go', 'to'], ['How', 'do', 'you', 'go', 'to', 'school?'],
              'How, then do, then you.'),
    ],
}

# ---------------------------------------------------------------- and, but, or, because, so
LESSONS['joining-words'] = {
    'film': [
        S([L('I have a dog and a cat.', by='m'), L('And adds an idea.', hl=['and'])],
          cast=[C('m', 'man', 90, accent=True), C('d', 'dog', 180), C('c', 'cat', 250)]),
        S([L('I like apples, but I do not like eggs.', by='g', v='woman'), L('But shows a different idea.', hl=['but'])],
          cast=[C('g', 'girl', 90, accent=True, pose='eat', holds='apple'), C('t', 'table', 220), C('e', 'egg', 220, y=TOP)]),
        S([L('Do you want milk or water?', by='w', v='woman'), L('Or gives a choice.', hl=['or'])],
          cast=[C('w', 'woman', 80, accent=True), C('t', 'table', 160), C('b', 'bottle', 150, y=TOP), C('g', 'glass', 172, y=TOP),
                C('b2', 'boy', 245, face=-1)]),
        S([L('We stayed at home because it was raining.', hl=['because']), L('Because gives the reason.', hl=['because'])],
          cast=[C('c', 'cloud', 180, y=40, rain=True), C('h', 'house', 180), C('m', 'man', 80, accent=True)]),
        S([L('It was raining, so we stayed at home.', hl=['so']), L('So gives the result.', hl=['so'])],
          cast=[C('c', 'cloud', 180, y=40, rain=True), C('h', 'house', 180), C('m', 'man', 60, accent=True, to=170, toAt=0, out=1)]),
        S([L('And, but, or, because and so are conjunctions.', hl=['conjunctions']),
           L('A conjunction joins words or parts of a sentence.')],
          board=[B(0, ['and', 'but', 'or', 'because', 'so'], tag={0: 'adds', 1: 'different', 2: 'choice', 3: 'reason', 4: 'result'})]),
    ],
    'rule': {
        'table': [['adds an idea', 'and'], ['a different idea', 'but'], ['a choice', 'or'], ['the reason', 'because'], ['the result', 'so']],
        'examples': [{'t': 'I like apples, but I do not like eggs.', 'v': 'woman'}, {'t': 'We stayed at home because it was raining.'},
                     {'t': 'I have a dog and a cat.'}, {'t': 'Do you want milk or water?', 'v': 'woman'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['and', 'but', 'or'], 'but', 'A different idea: but.',
             before='I like apples,', after='I do not like eggs.'),
        pick('Put the right word in the space.', ['because', 'so'], 'because', 'It is cold is the reason: because.',
             before='I am wearing a coat', after='it is cold.'),
        pick('Put the right word in the space.', ['because', 'so'], 'so', 'Wearing a coat is the result: so.',
             before='It is cold,', after='I am wearing a coat.'),
        pick('Put the right word in the space.', ['and', 'or'], 'or', 'A choice: or.', before='Do you want milk', after='water?'),
        pick('Put the right word in the space.', ['and', 'but'], 'and', 'It adds an idea: and.', before='I have a dog', after='a cat.'),
        tap('Touch the conjunction.', ['She', 'is', 'tired', 'but', 'happy.'], [3], 'But joins tired and happy.'),
    ],
}

# ---------------------------------------------------------------- countable or uncountable
LESSONS['countable'] = {
    'film': [
        S([L('One apple. Two apples. Three apples.', hl=['apple', 'apples']),
           L('We can put a number before apple, and it has a plural.')],
          cast=[C('a', 'apple', 100, s=1.4, label='one', labelAt=0), C('b', 'apple', 160, s=1.4, n=2, gap=22, in_=0),
                C('c', 'apple', 245, s=1.4, n=3, gap=22, in_=0)]),
        S([L('This is water.', hl=['water']), L('We do not say two waters. Water has no plural.')],
          cast=[C('g', 'glass', 160, s=1.6)],
          board=[B(1, ['two', 'waters'], x=[0, 1])]),
        S([L('Apple is countable. Water is uncountable.', hl=['countable', 'uncountable']),
           L('Milk, music and money are uncountable too.')],
          board=[B(0, ['an', 'apple', 'water'], tag={1: 'countable', 2: 'uncountable'}),
                 B(1, ['milk', 'music', 'money'], tag={0: 'no plural', 1: 'no plural', 2: 'no plural'})]),
        S([L('Many apples.', hl=['many']), L('Much water.', hl=['much']),
           L('Use many with countable nouns and much with uncountable nouns.')],
          board=[B(0, ['many', 'apples'], r={1: 'n'}, tag={1: 'countable'}),
                 B(1, ['many', 'apples', 'much', 'water'], r={1: 'n', 3: 'n'}, tag={1: 'countable', 3: 'uncountable'})]),
        S([L('How many eggs do we have?', by='w', v='woman'), L('We do not have much milk.', by='m')],
          cast=[C('w', 'woman', 70, accent=True), C('t', 'table', 160), C('e', 'egg', 140, y=TOP, n=3, gap=12), C('b', 'bottle', 182, y=TOP),
                C('m', 'man', 250, face=-1, pose='shrug', poseAt=1)]),
    ],
    'rule': {
        'table': [['countable: a, an, two, many', 'an apple, two apples'], ['uncountable: no a, no plural, much', 'water, much water']],
        'examples': [{'t': 'How many eggs do we have?', 'v': 'woman'}, {'t': 'We do not have much milk.'}, {'t': 'I have two apples.'},
                     {'t': 'Water is good for you.'}],
    },
    'tasks': [
        pick('Which noun is countable?', ['apple', 'water', 'milk'], 'apple', 'We can say two apples.'),
        pick('Which noun is uncountable?', ['egg', 'book', 'money'], 'money', 'We do not say two moneys.'),
        pick('Put the right word in the space.', ['many', 'much'], 'many', 'Eggs are countable: many.', before='How', after='eggs do we have?'),
        pick('Put the right word in the space.', ['many', 'much'], 'much', 'Milk is uncountable: much.', before='We do not have', after='milk.'),
        fix(['I', 'have', 'three', 'book.'], 3, ['book', 'books'], 'books', 'Book is countable: three books.'),
        build('Put the words in the right order.', ['much', 'have', 'We', 'not', 'do', 'milk.'], ['We', 'do', 'not', 'have', 'much', 'milk.'],
              'Much comes before milk.'),
    ],
}

# ---------------------------------------------------------------- there is, there are
LESSONS['there-is'] = {
    'film': [
        S([L('There is a cat in the garden.', hl=['there', 'is'])],
          cast=[C('t', 'tree', 220), C('c', 'cat', 140, accent=True), C('f', 'flower', 70)], min=2400),
        S([L('There are two cats in the garden.', hl=['there', 'are']), L('There is for one. There are for more than one.')],
          cast=[C('t', 'tree', 240), C('c', 'cat', 110, n=2, gap=50, accent=True), C('f', 'flower', 50)]),
        S([L('There is water in the glass.'), L('With an uncountable noun, use there is too.')],
          cast=[C('g', 'glass', 160, s=1.6)]),
        S([L('There is a book on the table.'), L('Is there a book on the table?', hl=['is', 'there']), L('To ask, put is or are first.')],
          cast=[C('t', 'table', 160), C('b', 'book', 160, y=TOP)],
          board=[B(0, ['There', 'is', 'a', 'book.'], r={1: 'b'}), B(1, ['Is', 'there', 'a', 'book?'], r={0: 'b'})]),
        S([L('Are there any eggs?', by='w', v='woman'), L('Yes, there are.', by='m')],
          cast=[C('w', 'woman', 70, accent=True), C('t', 'table', 160), C('e', 'egg', 145, y=TOP, n=3, gap=14), C('m', 'man', 250, face=-1, pose='nod', poseAt=1)]),
    ],
    'rule': {
        'table': [['one, or uncountable', 'there is'], ['more than one', 'there are']],
        'examples': [{'t': 'There is a book on the table.'}, {'t': 'Are there any eggs?', 'v': 'woman'},
                     {'t': 'There are two cats in the garden.'}, {'t': 'There is water in the glass.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['is', 'are'], 'is', 'One cat: there is.', before='There', after='a cat in the garden.'),
        pick('Put the right word in the space.', ['is', 'are'], 'are', 'Three eggs: there are.', before='There', after='three eggs.'),
        pick('Put the right word in the space.', ['is', 'are'], 'is', 'Water is uncountable: there is.', before='There', after='water in the glass.'),
        build('Make a question.', ['there', 'Is', 'a', 'book?'], ['Is', 'there', 'a', 'book?'], 'Is comes first.'),
        fix(['There', 'is', 'two', 'dogs.'], 1, ['is', 'are'], 'are', 'Two dogs: there are.'),
        pick('Put the right word in the space.', ['Is', 'Are'], 'Are', 'Eggs are more than one: are.', after='there any eggs?'),
    ],
}

# ---------------------------------------------------------------- some and any
LESSONS['some-any'] = {
    'film': [
        S([L('There are some birds in the tree.', hl=['some']), L('We say some when we do not say the number.')],
          cast=[C('t', 'tree', 160, s=1.3), C('b', 'bird', 135, y=58, n=3, gap=24)]),
        S([L('We do not have any bread.', by='m'), L('After not, we use any.', hl=['any'])],
          cast=[C('m', 'man', 100, accent=True, pose='shrug'), C('t', 'table', 210)]),
        S([L('Do you have any milk?', by='w', v='woman'), L('Yes, I have some.', by='m'), L('In questions, we use any.', hl=['any'])],
          cast=[C('w', 'woman', 90, accent=True), C('m', 'man', 200, face=-1, pose='give', holds='bottle', poseAt=1)]),
        S([L('Would you like some milk?', by='m'), L('Yes, please.', by='w', v='woman'),
           L('When we offer something, we use some, even in a question.', hl=['some'])],
          cast=[C('m', 'man', 100, accent=True, pose='give', holds='glass'), C('w', 'woman', 200, face=-1, pose='nod', poseAt=1)]),
        S([L('I have some apples.', hl=['some']), L('I do not have any.', hl=['any']), L('Do you have any?', hl=['any'])],
          board=[B(0, ['I', 'have', 'some', 'apples.'], r={2: 'ok'}), B(1, ['I', 'do', 'not', 'have', 'any.'], r={2: 'neg', 4: 'ok'}),
                 B(2, ['Do', 'you', 'have', 'any?'], r={0: 'q', 3: 'ok'})]),
    ],
    'rule': {
        'table': [['saying yes', 'some'], ['after not', 'any'], ['questions', 'any'], ['offering', 'some']],
        'examples': [{'t': 'There are some birds in the tree.'}, {'t': 'We do not have any bread.'},
                     {'t': 'Do you have any milk?', 'v': 'woman'}, {'t': 'Would you like some milk?'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['some', 'any'], 'some', 'A sentence that says yes: some.', before='I have', after='apples.'),
        pick('Put the right word in the space.', ['some', 'any'], 'any', 'After not: any.', before='I do not have', after='money.'),
        pick('Put the right word in the space.', ['some', 'any'], 'any', 'In a question: any.', before='Do you have', after='brothers?'),
        pick('Put the right word in the space.', ['some', 'any'], 'some', 'You offer something: some.', before='Would you like', after='water?'),
        fix(['There', 'are', 'any', 'birds', 'in', 'the', 'tree.'], 2, ['some', 'any'], 'some', 'This sentence says yes: some.'),
        build('Put the words in the right order.', ['any', 'We', 'have', 'do', 'not', 'bread.'], ['We', 'do', 'not', 'have', 'any', 'bread.'],
              'Do not have, then any.'),
    ],
}

# ---------------------------------------------------------------- was and were
LESSONS['past-be'] = {
    'film': [
        S([L('Today I am at school.', by='b'), L('Yesterday I was at home.', by='b'), L('Was is the past of am and is.', hl=['was'])],
          cast=[C('b', 'boy', 120, accent=True), C('h', 'house', 240, s=0.8, label='school', labelAt=0, out=1),
                C('h2', 'house', 240, s=0.8, in_=1, label='home', labelAt=1)]),
        S([L('I am at home.'), L('Yesterday I was at home.', hl=['was']), L('Yesterday they were at home.', hl=['were'])],
          board=[B(0, ['I', 'am', 'at', 'home.'], r={1: 'b'}), B(1, ['I', 'was', 'at', 'home.'], r={1: 'b'}, tag={1: 'past'}),
                 B(2, ['They', 'were', 'at', 'home.'], r={1: 'b'}, tag={1: 'past'})]),
        S([L('I, he, she and it: was.', hl=['was']), L('You, we and they: were.', hl=['were'])],
          board=[B(0, ['I', 'he', 'she', 'it', 'was'], r={0: 'p', 1: 'p', 2: 'p', 3: 'p', 4: 'b'}),
                 B(1, ['you', 'we', 'they', 'were'], r={0: 'p', 1: 'p', 2: 'p', 3: 'b'})]),
        S([L('The shops were closed.', hl=['were']), L('We were not happy.', hl=['were', 'not'])],
          cast=[C('h', 'house', 90, s=0.8), C('h2', 'house', 170, s=0.8), C('m', 'man', 245, face=-1, pose='shrug', poseAt=1, accent=True)]),
        S([L('Was it cold?', by='g', v='woman'), L('Yes, it was.', by='m')],
          cast=[C('c', 'cloud', 160, y=36, rain=True), C('g', 'girl', 100, accent=True), C('m', 'man', 210, face=-1, pose='nod', poseAt=1)]),
    ],
    'rule': {
        'table': [['I, he, she, it', 'was'], ['you, we, they', 'were']],
        'examples': [{'t': 'I was at home yesterday.'}, {'t': 'The shops were closed.'}, {'t': 'Was it cold? Yes, it was.'},
                     {'t': 'We were not late.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'was', 'rest': 'at home'}, {'s': 'you', 'be': 'were', 'rest': 'late'},
        {'s': 'he', 'be': 'was', 'rest': 'tired'}, {'s': 'she', 'be': 'was', 'rest': 'at school'},
        {'s': 'it', 'be': 'was', 'rest': 'cold'}, {'s': 'we', 'be': 'were', 'rest': 'happy'},
        {'s': 'they', 'be': 'were', 'rest': 'ill'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right word in the space.', ['was', 'were'], 'was', 'With I: was.', before='I', after='at home yesterday.'),
        pick('Put the right word in the space.', ['was', 'were'], 'were', 'The shops are more than one: were.', before='The shops', after='closed.'),
        pick('Put the right word in the space.', ['Was', 'Were'], 'Were', 'With you: were.', after='you there?'),
        fix(['They', 'was', 'late.'], 1, ['was', 'were'], 'were', 'With they: were.'),
        build('Put the words in the right order.', ['not', 'was', 'It', 'cold.'], ['It', 'was', 'not', 'cold.'], 'Not comes after was.'),
        pick('Put the right word in the space.', ['was', 'were'], 'was', 'The answer uses was again.',
             before='Was it cold? Yes, it', after='.', answer='Was it cold? Yes, it was.'),
    ],
}

# ---------------------------------------------------------------- the past simple
LESSONS['past-simple'] = {
    'film': [
        S([L('Today I play.'), L('Yesterday I played.', hl=['played'])],
          cast=[C('b', 'boy', 110, accent=True, pose='kick', poseAt=1), C('o', 'ball', 128, to=260, toAt=1)],
          board=[B(0, ['I', 'play.'], r={1: 'v'}, tag={1: 'now'}), B(1, ['I', 'played.'], r={1: 'v'}, tag={1: '+ ed'})]),
        S([L('The past simple is for things that happened and ended before now.', hl=['past', 'simple']),
           L('For most verbs, we add ed.', hl=['ed'])],
          board=[B(0, ['walk', 'walked'], r={1: 'v'}, tag={1: 'past'}),
                 B(1, ['walk', 'walked', 'open', 'opened'], r={1: 'v', 3: 'v'}, tag={1: '+ ed', 3: '+ ed'})]),
        S([L('She opened the window.', hl=['opened'])],
          cast=[C('w', 'woman', 150, accent=True, pose='reach', poseAt=0), C('x', 'window', 210, out=0), C('x2', 'window', 210, open=True, in_=0)],
          min=2400),
        S([L('I walked. She walked. They walked.', hl=['walked']), L('The past simple is the same with every subject.')],
          board=[B(0, ['I', 'walked'], r={1: 'v'}), B(1, ['I', 'walked', 'she', 'walked', 'they', 'walked'], r={1: 'v', 3: 'v', 5: 'v'})]),
        S([L('We played a game yesterday.', by='g', v='woman')],
          cast=[C('g', 'girl', 80, accent=True), C('b', 'boy', 150, pose='wave'), C('o', 'ball', 220), C('t', 'tree', 280, s=0.8)]),
    ],
    'rule': {
        'examples': [{'t': 'We played a game yesterday.', 'v': 'woman'}, {'t': 'She opened the window.'}, {'t': 'I walked to school.'},
                     {'t': 'They watched the birds.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['play', 'played'], 'played', 'Yesterday is past: played.', before='We', after='a game yesterday.'),
        pick('Put the right word in the space.', ['open', 'opened'], 'opened', 'An hour ago is past: opened.', before='She', after='the window an hour ago.'),
        pick('Put the right word in the space.', ['walks', 'walked'], 'walked', 'Last night is past: walked.', before='He', after='home last night.'),
        fix(['They', 'watch', 'the', 'birds', 'yesterday.'], 1, ['watch', 'watched'], 'watched', 'Yesterday is past: add ed.'),
        build('Put the words in the right order.', ['the', 'door.', 'I', 'closed'], ['I', 'closed', 'the', 'door.'], 'Subject, verb, object.'),
        pick('Which sentence is about the past?', ['I played a game.', 'I play a game.'], 'I played a game.',
             'Played ends in ed: it is the past.'),
    ],
}
