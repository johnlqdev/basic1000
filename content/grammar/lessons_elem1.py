"""Elementary school lessons, part 1: this/that, the, subject and object, the present simple,
have, not and questions in the present, object pronouns, my/your, 's, can, orders."""
from lessons_kit import L, C, B, S, pick, build, fix, tap, TOP  # noqa: F401

LESSONS = {}

# ---------------------------------------------------------------- this, that, these, those
LESSONS['this-that'] = {
    'film': [
        S([L('This is my book.', by='m'), L('The book is near him, so he says this.', hl=['this'])],
          cast=[C('m', 'man', 110, pose='hold', holds='book', accent=True), C('t', 'tree', 260, s=0.9)]),
        S([L('That is my house.', by='m'), L('The house is far from him, so he says that.', hl=['that'])],
          cast=[C('m', 'man', 60, pose='point', accent=True), C('h', 'house', 255, s=0.7)]),
        S([L('These are my apples.', by='w', v='woman'), L('These is for more than one thing near you.', hl=['these'])],
          cast=[C('w', 'woman', 80, accent=True, pose='point'), C('t', 'table', 150), C('a', 'apple', 132, y=TOP, n=3, gap=18, s=1.2)]),
        S([L('Those birds are very high.', by='w', v='woman'), L('Those is for more than one thing far from you.', hl=['those'])],
          cast=[C('w', 'woman', 70, accent=True, pose='reach'), C('b', 'bird', 210, y=40, n=3, gap=28)]),
        S([L('Near you: this for one, these for more than one.', hl=['this', 'these']),
           L('Far from you: that for one, those for more than one.', hl=['that', 'those'])],
          board=[B(0, ['this', 'these'], tag={0: 'near, one', 1: 'near, more'}),
                 B(1, ['this', 'these', 'that', 'those'], tag={0: 'near, one', 1: 'near, more', 2: 'far, one', 3: 'far, more'})]),
    ],
    'rule': {
        'table': [['near, one', 'this'], ['near, more', 'these'], ['far, one', 'that'], ['far, more', 'those']],
        'examples': [{'t': 'This is my book.'}, {'t': 'These apples are red.'}, {'t': 'That is my house.'},
                     {'t': 'Those birds are very high.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['This', 'These'], 'These', 'Apples are more than one, and they are near: these.',
             after='apples are mine.'),
        pick('Put the right word in the space.', ['that', 'those'], 'that', 'One house, far away: that.',
             before='Look at', after='house over there.'),
        pick('Put the right word in the space.', ['this', 'these'], 'this', 'One book, here in my hand: this.',
             before='I like', after='book.'),
        pick('Put the right word in the space.', ['That', 'Those'], 'Those', 'More than one bird, far away: those.',
             after='birds are very high.'),
        fix(['These', 'book', 'is', 'new.'], 0, ['This', 'These'], 'This', 'One book: this, not these.'),
        build('Put the words in the right order.', ['are', 'Those', 'dogs.', 'my'], ['Those', 'are', 'my', 'dogs.'],
              'Those, then are, then my dogs.'),
    ],
}

# ---------------------------------------------------------------- a or the
LESSONS['the'] = {
    'film': [
        S([L('I saw a dog.', by='w', v='woman'), L('The dog is new to the man, so she says a dog.', hl=['a'])],
          cast=[C('w', 'woman', 90, accent=True), C('m', 'man', 190, face=-1), C('d', 'dog', 280, face=-1, in_=1)]),
        S([L('The dog was very big.', by='w', v='woman'), L('Now he knows about the dog. So she says the dog.', hl=['the'])],
          cast=[C('w', 'woman', 90, accent=True, pose='shrug', poseAt=0), C('m', 'man', 190, face=-1), C('d', 'dog', 270, face=-1, s=1.6)]),
        S([L('The sun is hot.'), L('There is only one sun, so we say the sun.', hl=['the'])],
          cast=[C('s', 'sun', 160, y=40), C('b', 'boy', 110), C('g', 'girl', 210, face=-1)]),
        S([L('A dog: any dog, a dog that is new to you.', hl=['a']),
           L('The dog: the one we both know about.', hl=['the'])],
          cast=[C('d', 'dog', 160, s=1.3)],
          board=[B(0, ['a', 'dog'], r={0: 'art'}, tag={0: 'new'}), B(1, ['the', 'dog'], r={0: 'art'}, tag={0: 'we know it'})]),
        S([L('A, an and the are called articles.', hl=['articles'])],
          board=[B(0, ['a', 'an', 'the'], r={0: 'art', 1: 'art', 2: 'art'}, tag={0: 'article', 1: 'article', 2: 'article'})]),
    ],
    'rule': {
        'examples': [{'t': 'I saw a dog. The dog was very big.', 'v': 'woman'}, {'t': 'The sun is hot.'},
                     {'t': 'Please open the door.'}, {'t': 'She has an apple and a book.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['a', 'the'], 'a', 'The cat is new to the person you talk to: a.',
             before='I have', after='cat.'),
        pick('Put the right word in the space.', ['A', 'The'], 'The', 'Now we both know the cat: the.',
             before='I have a cat.', after='cat is black.'),
        pick('Put the right word in the space.', ['a', 'the'], 'the', 'There is only one sun: the.',
             before='Look at', after='sun!'),
        pick('Put the right word in the space.', ['a', 'an', 'the'], 'an', 'Any egg, and egg begins with the sound of e: an.',
             before='She eats', after='egg every day.'),
        fix(['The', 'bird', 'is', 'in', 'a', 'sky.'], 4, ['a', 'the'], 'the', 'There is only one sky: the sky.'),
        pick('Which word is an article?', ['the', 'dog', 'big'], 'the', 'A, an and the are articles.'),
    ],
}

# ---------------------------------------------------------------- subject and object
LESSONS['subject-object'] = {
    'film': [
        S([L('The boy kicks the ball.', hl=['kicks'])],
          cast=[C('b', 'boy', 110, accent=True, pose='kick', poseAt=0), C('o', 'ball', 128, to=280, toAt=0)], min=2600),
        S([L('Kicks is the verb.', hl=['kicks']),
           L('The boy does the action. The boy is the subject.', hl=['subject']),
           L('The ball is what he kicks. The ball is the object.', hl=['object'])],
          cast=[C('b', 'boy', 110, accent=True), C('o', 'ball', 220)],
          board=[B(0, ['The', 'boy', 'kicks', 'the', 'ball.'], r={2: 'v'}, tag={2: 'verb'}),
                 B(1, ['The', 'boy', 'kicks', 'the', 'ball.'], r={1: 'n', 2: 'v'}, tag={1: 'subject', 2: 'verb'}),
                 B(2, ['The', 'boy', 'kicks', 'the', 'ball.'], r={1: 'n', 2: 'v', 4: 'n'}, tag={1: 'subject', 2: 'verb', 4: 'object'})]),
        S([L('The cat eats the fish.'), L('The cat is the subject. The fish is the object.', hl=['subject', 'object'])],
          cast=[C('c', 'cat', 120, accent=True), C('f', 'fish', 170, s=0.8, face=-1)],
          board=[B(0, ['The', 'cat', 'eats', 'the', 'fish.'], r={2: 'v'}),
                 B(1, ['The', 'cat', 'eats', 'the', 'fish.'], r={1: 'n', 2: 'v', 4: 'n'}, tag={1: 'subject', 4: 'object'})]),
        S([L('The dog sees the boy.'), L('The boy sees the dog.'),
           L('Change the order, and the meaning changes.')],
          cast=[C('d', 'dog', 110), C('b', 'boy', 220, face=-1)],
          board=[B(0, ['The', 'dog', 'sees', 'the', 'boy.'], r={1: 'n', 2: 'v', 4: 'n'}, tag={1: 'subject', 4: 'object'}),
                 B(1, ['The', 'boy', 'sees', 'the', 'dog.'], r={1: 'n', 2: 'v', 4: 'n'}, tag={1: 'subject', 4: 'object'})]),
        S([L('The subject usually comes before the verb.', hl=['subject']),
           L('The object usually comes after it.', hl=['object'])],
          board=[B(0, ['My', 'mother', 'drives', 'the', 'car.'], r={1: 'n', 2: 'v'}, tag={1: 'subject', 2: 'verb'}),
                 B(1, ['My', 'mother', 'drives', 'the', 'car.'], r={1: 'n', 2: 'v', 4: 'n'}, tag={1: 'subject', 2: 'verb', 4: 'object'})],
          cast=[C('w', 'woman', 50, accent=True), C('c', 'car', 255)]),
    ],
    'rule': {
        'examples': [{'t': 'The boy kicks the ball.'}, {'t': 'My mother drives the car.'}, {'t': 'The cat eats the fish.'}],
    },
    'tasks': [
        tap('Touch the subject.', ['The', 'girl', 'opens', 'the', 'door.'], [1], 'The girl does the action.'),
        tap('Touch the object.', ['The', 'boy', 'kicks', 'the', 'ball.'], [4], 'The ball is what the boy kicks.'),
        tap('Touch the subject.', ['My', 'father', 'drives', 'a', 'car.'], [1], 'My father does the driving.'),
        tap('Touch the object.', ['Mary', 'reads', 'a', 'book.'], [3], 'The book is what Mary reads.'),
        pick('In "The dog sees the cat", which is the object?', ['the dog', 'the cat'], 'the cat',
             'The dog does the action. The cat is what the dog sees.'),
        build('Put the words in the right order.', ['the', 'eats', 'The', 'fish.', 'cat'], ['The', 'cat', 'eats', 'the', 'fish.'],
              'Subject, then verb, then object.'),
    ],
}

# ---------------------------------------------------------------- the present simple
LESSONS['present-simple'] = {
    'film': [
        S([L('I walk to school every day.', by='b'),
           L('This happens again and again. We use the present simple.', hl=['present', 'simple'])],
          cast=[C('b', 'boy', 60, accent=True, to=170, toAt=0), C('h', 'house', 270, s=0.8, label='school', labelAt=0)]),
        S([L('She walks to school every day.'), L('With he, she and it, the verb gets s.', hl=['walks'])],
          cast=[C('g', 'girl', 60, accent=True, to=200, toAt=0)],
          board=[B(0, ['She', 'walks', 'to', 'school.'], r={0: 'p', 1: 'v'}),
                 B(1, ['I', 'walk.', 'She', 'walks.'], r={1: 'v', 3: 'v'}, tag={3: '+ s'})]),
        S([L('I play. You play. We play. They play.'), L('He plays. She plays. It plays.', hl=['plays'])],
          board=[B(0, ['I', 'you', 'we', 'they', 'play'], r={0: 'p', 1: 'p', 2: 'p', 3: 'p', 4: 'v'}),
                 B(1, ['he', 'she', 'it', 'plays'], r={0: 'p', 1: 'p', 2: 'p', 3: 'v'}, tag={3: '+ s'})]),
        S([L('After s, sh, ch, x and o, we add es.', hl=['es']), L('Watch, watches. Go, goes.', hl=['watches', 'goes'])],
          board=[B(0, ['watch', 'watches'], r={1: 'v'}, tag={1: '+ es'}),
                 B(1, ['watch', 'watches', 'go', 'goes'], r={1: 'v', 3: 'v'}, tag={1: '+ es', 3: '+ es'})]),
        S([L('The sun rises in the east.'), L('This is always true. We use the present simple for it too.')],
          cast=[C('s', 'sun', 40, y=70, to=150, toAt=0), C('t', 'tree', 250, s=0.9), C('h', 'house', 90, s=0.6)]),
    ],
    'rule': {
        'examples': [{'t': 'I walk to school every day.'}, {'t': 'She walks to school every day.'},
                     {'t': 'The sun rises in the east.'}, {'t': 'He goes home at six.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['walk', 'walks'], 'walks', 'With she, add s.', before='She', after='to school.'),
        pick('Put the right word in the space.', ['play', 'plays'], 'play', 'With they, the verb has no s.', before='They', after='in the garden.'),
        pick('Put the right word in the space.', ['watchs', 'watches'], 'watches', 'After ch, add es.', before='He', after='the birds.'),
        pick('Put the right word in the space.', ['gos', 'goes'], 'goes', 'After o, add es.', before='My father', after='to work at eight.'),
        fix(['The', 'sun', 'rise', 'in', 'the', 'east.'], 2, ['rise', 'rises'], 'rises', 'The sun is like it: add s.'),
        build('Put the words in the right order.', ['every', 'day.', 'I', 'milk', 'drink'], ['I', 'drink', 'milk', 'every', 'day.'],
              'Subject, verb, object, then when.'),
    ],
}

# ---------------------------------------------------------------- have and has
LESSONS['have'] = {
    'film': [
        S([L('I have a red bag.', by='g', v='woman'), L('She has a red bag.', hl=['has'])],
          cast=[C('g', 'girl', 150, accent=True, pose='hold', holds='bag')]),
        S([L('He has a dog.', hl=['has']), L('With he, she and it, we use has.', hl=['has'])],
          cast=[C('b', 'boy', 120, accent=True), C('d', 'dog', 190)]),
        S([L('We have two cats.', by='m'), L('With I, you, we and they, we use have.', hl=['have'])],
          cast=[C('m', 'man', 70, accent=True), C('w', 'woman', 120, accent=True), C('c', 'cat', 200, n=2, gap=40)]),
        S([L('I have, you have, we have, they have.', hl=['have']), L('He has, she has, it has.', hl=['has'])],
          board=[B(0, ['I', 'you', 'we', 'they', 'have'], r={0: 'p', 1: 'p', 2: 'p', 3: 'p', 4: 'v'}),
                 B(1, ['he', 'she', 'it', 'has'], r={0: 'p', 1: 'p', 2: 'p', 3: 'v'})]),
        S([L('We also use have for food and for time.'), L('We have a meal at seven.', by='w', v='woman')],
          cast=[C('w', 'woman', 90, accent=True), C('t', 'table', 165), C('a', 'apple', 150, y=TOP, s=1.1),
                C('g', 'glass', 180, y=TOP), C('m', 'man', 240, face=-1)]),
    ],
    'rule': {
        'table': [['I, you, we, they', 'have'], ['he, she, it', 'has']],
        'examples': [{'t': 'She has a red bag.'}, {'t': 'We have two cats.'}, {'t': 'He has a big house.'},
                     {'t': 'They have a meal at seven.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'have', 'rest': 'a dog'}, {'s': 'you', 'be': 'have', 'rest': 'a car'},
        {'s': 'he', 'be': 'has', 'rest': 'a ball'}, {'s': 'she', 'be': 'has', 'rest': 'a red bag'},
        {'s': 'it', 'be': 'has', 'rest': 'a long tail'}, {'s': 'we', 'be': 'have', 'rest': 'two cats'},
        {'s': 'they', 'be': 'have', 'rest': 'a big house'}], 'forms': ['plain']},
    'tasks': [
        pick('Put the right word in the space.', ['have', 'has'], 'has', 'With she, use has.', before='She', after='a red bag.'),
        pick('Put the right word in the space.', ['have', 'has'], 'have', 'With we, use have.', before='We', after='two cats.'),
        pick('Put the right word in the space.', ['have', 'has'], 'has', 'The dog is like it: has.', before='The dog', after='a long tail.'),
        pick('Put the right word in the space.', ['have', 'has'], 'have', 'With I, use have.', before='I', after='a brother.'),
        fix(['They', 'has', 'a', 'car.'], 1, ['have', 'has'], 'have', 'With they, use have.'),
        build('Put the words in the right order.', ['has', 'My', 'a', 'sister', 'cat.'], ['My', 'sister', 'has', 'a', 'cat.'],
              'My sister is like she: has.'),
    ],
}

# ---------------------------------------------------------------- do not, does not
LESSONS['present-not'] = {
    'film': [
        S([L('I do not like milk.', by='m'), L('He says do not before the verb.', hl=['do', 'not'])],
          cast=[C('m', 'man', 120, accent=True, pose='shrug', poseAt=0), C('t', 'table', 210), C('b', 'bottle', 210, y=TOP)]),
        S([L('I like milk.'), L('I do not like milk.', hl=['do', 'not']), L('Put do not before the verb.')],
          board=[B(0, ['I', 'like', 'milk.'], r={1: 'v'}),
                 B(1, ['I', 'do', 'not', 'like', 'milk.'], r={1: 'neg', 2: 'neg', 3: 'v'})]),
        S([L('She likes milk.'), L('She does not like milk.', hl=['does', 'not']),
           L('With he, she and it, use does not. Then the verb has no s.')],
          cast=[C('w', 'woman', 160, accent=True, pose='shrug', poseAt=1)],
          board=[B(0, ['She', 'likes', 'milk.'], r={1: 'v'}, tag={1: '+ s'}),
                 B(1, ['She', 'does', 'not', 'like', 'milk.'], r={1: 'neg', 2: 'neg', 3: 'v'}, tag={3: 'no s'})]),
        S([L("When we talk, do not becomes don't."), L("And does not becomes doesn't.")],
          board=[B(0, ['do', 'not', "don't"], r={2: 'neg'}), B(1, ['does', 'not', "doesn't"], r={2: 'neg'})]),
        S([L('He does not drive a car. He walks.')],
          cast=[C('m', 'man', 50, accent=True, to=250, toAt=0), C('c', 'car', 150, s=0.8)], min=2600),
    ],
    'rule': {
        'table': [['I, you, we, they', 'do not'], ['he, she, it', 'does not']],
        'examples': [{'t': 'I do not eat meat.'}, {'t': 'He does not drive a car.'}, {'t': 'We do not live here.'},
                     {'t': "She doesn't like milk."}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['do', 'does'], 'does', 'With she, use does not.', before='She', after='not like milk.'),
        pick('Put the right word in the space.', ['do', 'does'], 'do', 'With they, use do not.', before='They', after='not eat meat.'),
        pick('Put the right word in the space.', ['drive', 'drives'], 'drive', 'After does not, the verb has no s.',
             before='He does not', after='a car.'),
        fix(['She', 'does', 'not', 'likes', 'fish.'], 3, ['like', 'likes'], 'like', 'After does not, the verb has no s.'),
        build('Put the words in the right order.', ['not', 'I', 'do', 'here.', 'live'], ['I', 'do', 'not', 'live', 'here.'],
              'Do not comes before the verb.'),
        pick('Put the right words in the space.', ['do not', 'does not'], 'do not', 'With we, use do not.', before='We', after='have a car.'),
    ],
}

# ---------------------------------------------------------------- do you? does she?
LESSONS['present-question'] = {
    'film': [
        S([L('Do you live here?', by='w', v='woman'), L('Yes, I do.', by='m')],
          cast=[C('w', 'woman', 90, accent=True), C('m', 'man', 190, face=-1, pose='nod', poseAt=1), C('h', 'house', 275, s=0.7)]),
        S([L('You live here.'), L('Do you live here?', hl=['do']), L('To ask, put do first.')],
          board=[B(0, ['You', 'live', 'here.'], r={1: 'v'}), B(1, ['Do', 'you', 'live', 'here?'], r={0: 'q', 2: 'v'})]),
        S([L('He works on Sunday.'), L('Does he work on Sunday?', hl=['does']),
           L('With he, she and it, use does. Then the verb has no s.')],
          board=[B(0, ['He', 'works', 'on', 'Sunday.'], r={1: 'v'}, tag={1: '+ s'}),
                 B(1, ['Does', 'he', 'work', 'on', 'Sunday?'], r={0: 'q', 2: 'v'}, tag={2: 'no s'})]),
        S([L('Does she like music?', by='b'), L('Yes, she does.', by='m'), L('A short answer uses do or does again.')],
          cast=[C('b', 'boy', 80, accent=True), C('m', 'man', 170, face=-1, pose='nod', poseAt=1), C('w', 'woman', 260, face=-1)]),
        S([L('Do they eat meat?', by='g', v='woman'), L('No, they do not.', by='w', v='woman')],
          cast=[C('g', 'girl', 80, accent=True), C('w', 'woman', 160, face=-1), C('c', 'cow', 255, face=-1)]),
    ],
    'rule': {
        'table': [['I, you, we, they', 'do'], ['he, she, it', 'does']],
        'examples': [{'t': 'Do you live here? Yes, I do.'}, {'t': 'Does he work on Sunday? No, he does not.'},
                     {'t': 'Do they like music?'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['Do', 'Does'], 'Do', 'With you, use do.', after='you like apples?'),
        pick('Put the right word in the space.', ['Do', 'Does'], 'Does', 'With she, use does.', after='she live here?'),
        pick('Put the right word in the space.', ['work', 'works'], 'work', 'After does, the verb has no s.',
             before='Does he', after='on Sunday?'),
        build('Make a question.', ['you', 'Do', 'fish?', 'like'], ['Do', 'you', 'like', 'fish?'], 'Do comes first.'),
        pick('Put the right word in the space.', ['do', 'does'], 'does', 'The answer uses does again.',
             before='Does she like music? Yes, she', after='.', answer='Does she like music? Yes, she does.'),
        fix(['Does', 'they', 'live', 'here?'], 0, ['Do', 'Does'], 'Do', 'With they, use do.'),
    ],
}

# ---------------------------------------------------------------- me, him, her, us, them
LESSONS['object-pronoun'] = {
    'film': [
        S([L('The woman sees the man.'), L('She sees him.', hl=['him'])],
          cast=[C('w', 'woman', 100, accent=True), C('m', 'man', 210, face=-1)],
          board=[B(0, ['The', 'woman', 'sees', 'the', 'man.'], r={1: 'n', 2: 'v', 4: 'n'}, tag={1: 'subject', 4: 'object'}),
                 B(1, ['She', 'sees', 'him.'], r={0: 'p', 1: 'v', 2: 'p'}, tag={0: 'subject', 2: 'object'})]),
        S([L('After a verb, I becomes me.', hl=['me']), L('He becomes him. She becomes her.', hl=['him', 'her']),
           L('We becomes us. They becomes them.', hl=['us', 'them'])],
          board=[B(0, ['I', 'me'], r={1: 'p'}), B(1, ['he', 'him', 'she', 'her'], r={1: 'p', 3: 'p'}),
                 B(2, ['we', 'us', 'they', 'them'], r={1: 'p', 3: 'p'})]),
        S([L('You does not change: you see me, I see you.', hl=['you']), L('It does not change: it sees me, I see it.', hl=['it'])],
          board=[B(0, ['you', 'you'], r={1: 'p'}, tag={0: 'subject', 1: 'object'}),
                 B(1, ['it', 'it'], r={1: 'p'}, tag={0: 'subject', 1: 'object'})]),
        S([L('Give the book to them.', by='w', v='woman'),
           L('After to, with and for, we use me, him, her, us and them too.')],
          cast=[C('w', 'woman', 90, accent=True, pose='give', holds='book'), C('c', 'boy', 190, face=-1, n=2, gap=34)]),
        S([L('Come with me.', by='g', v='woman'), L('We help her.', by='m')],
          cast=[C('g', 'girl', 110, accent=True, pose='wave', poseEnd=1), C('m', 'man', 200, face=-1), C('w', 'woman', 245, face=-1)]),
    ],
    'rule': {
        'table': [['I', 'me'], ['he', 'him'], ['she', 'her'], ['we', 'us'], ['they', 'them'], ['you, it', 'no change']],
        'examples': [{'t': 'She likes him.'}, {'t': 'Give the book to them.'}, {'t': 'Come with me.', 'v': 'woman'},
                     {'t': 'We help her.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['he', 'him'], 'him', 'After a verb, he becomes him.', before='I know', after='.'),
        pick('Put the right word in the space.', ['she', 'her'], 'her', 'After a verb, she becomes her.', before='We help', after='.'),
        pick('Put the right word in the space.', ['they', 'them'], 'them', 'After to, they becomes them.', before='Give the book to', after='.'),
        pick('Put the right word in the space.', ['I', 'me'], 'me', 'After with, I becomes me.', before='Come with', after='.'),
        fix(['She', 'likes', 'we.'], 2, ['we', 'us'], 'us', 'After a verb, we becomes us.'),
        tap('Touch the pronoun that is an object.', ['He', 'sees', 'her.'], [2], 'Her comes after the verb: it is the object.'),
    ],
}

# ---------------------------------------------------------------- my, your, his, her ...
LESSONS['possessive'] = {
    'film': [
        S([L('This is my bag.', by='m'), L('My says who has the bag.', hl=['my'])],
          cast=[C('m', 'man', 140, accent=True, pose='hold', holds='bag')]),
        S([L('This is his dog.', hl=['his']), L('This is her house.', hl=['her'])],
          cast=[C('m', 'man', 60, label='his dog', labelAt=0), C('d', 'dog', 110), C('w', 'woman', 190, in_=1),
                C('h', 'house', 262, in_=1, s=0.8, label='her house', labelAt=1)]),
        S([L('I: my. You: your.'), L('He: his. She: her.'), L('It: its. We: our. They: their.')],
          board=[B(0, ['I', 'my', 'you', 'your'], r={1: 'p', 3: 'p'}), B(1, ['he', 'his', 'she', 'her'], r={1: 'p', 3: 'p'}),
                 B(2, ['it', 'its', 'we', 'our', 'they', 'their'], r={1: 'p', 3: 'p', 5: 'p'})]),
        S([L('The dog wants its food.', hl=['its']), L('Its has no mark in it.')],
          cast=[C('d', 'dog', 140, accent=True), C('b', 'box', 190, s=0.7)],
          board=[B(1, ['its', 'food'], r={0: 'p'}, tag={0: 'no mark'})]),
        S([L('The bag is mine.', by='w', v='woman'),
           L('Mine, yours, his, hers, ours and theirs stand on their own, with no noun after them.')],
          cast=[C('w', 'woman', 150, accent=True, pose='hold', holds='bag', poseAt=0)]),
    ],
    'rule': {
        'table': [['I', 'my, mine'], ['you', 'your, yours'], ['he', 'his'], ['she', 'her, hers'], ['it', 'its'],
                  ['we', 'our, ours'], ['they', 'their, theirs']],
        'examples': [{'t': 'This is my house.'}, {'t': 'The book is hers.'}, {'t': 'Their dog is big.'},
                     {'t': 'The dog wants its food.'}],
    },
    'tasks': [
        pick('Put the right word in the space.', ['my', 'mine'], 'my', 'Before a noun, use my.', before='This is', after='bag.'),
        pick('Put the right word in the space.', ['her', 'hers'], 'hers', 'With no noun after it, use hers.', before='The book is', after='.'),
        pick('Put the right word in the space.', ['their', 'they'], 'their', 'Their says who has the house.', before='This is', after='house.'),
        pick('Put the right word in the space.', ['his', 'her'], 'her', 'Mary is a woman: her.', before='Mary has a cat. It is', after='cat.'),
        fix(['The', 'dog', 'wants', 'it', 'food.'], 3, ['it', 'its'], 'its', 'Its says who has the food.'),
        build('Put the words in the right order.', ['is', 'book', 'Your', 'new.'], ['Your', 'book', 'is', 'new.'],
              'Your comes before the noun.'),
    ],
}

# ---------------------------------------------------------------- the girl's book
LESSONS['apostrophe-s'] = {
    'film': [
        S([L("This is the girl's book."), L("We add 's to girl to show who has the book.")],
          cast=[C('g', 'girl', 150, accent=True, pose='hold', holds='book')],
          board=[B(0, ['the', "girl's", 'book'], r={1: 'n'}), B(1, ['the', "girl's", 'book'], r={1: 'n'}, tag={1: "+ 's"})]),
        S([L('This small mark is called an apostrophe.', hl=['apostrophe'])],
          board=[B(0, ["girl's"], r={0: 'n'}, tag={0: 'apostrophe'})]),
        S([L('Two boys have one room.'), L("Boys ends in s. So we add only the mark: the boys' room.")],
          cast=[C('b', 'boy', 90, n=2, gap=34, accent=True), C('h', 'house', 240, s=0.8)],
          board=[B(1, ['the', "boys'", 'room'], r={1: 'n'}, tag={1: "+ '"})]),
        S([L('Children does not end in s.'), L("So we add 's: the children's toys.")],
          cast=[C('c', 'girl', 70, n=2, gap=30), C('o', 'ball', 200), C('x', 'box', 240)],
          board=[B(1, ['the', "children's", 'toys'], r={1: 'n'}, tag={1: "+ 's"})]),
        S([L("This is my brother's car.", by='w', v='woman')],
          cast=[C('w', 'woman', 80, accent=True, pose='point'), C('m', 'man', 150), C('c', 'car', 240)]),
    ],
    'rule': {
        'table': [['the girl', "the girl's book"], ['the boys', "the boys' room"], ['the children', "the children's toys"]],
        'examples': [{'t': "This is my brother's car.", 'v': 'woman'}, {'t': "The children's toys are on the floor."},
                     {'t': "The girl's book is red."}, {'t': "The boys' room is big."}],
    },
    'tasks': [
        pick('Put the right word in the space.', ["girl's", 'girls'], "girl's", "The bag of the girl: the girl's bag.",
             before='This is the', after='bag.'),
        pick('Put the right word in the space.', ["boys'", "boy's"], "boys'", 'Two boys: boys ends in s, so add only the mark.',
             before='Two boys live here. This is the', after='room.'),
        pick('Put the right word in the space.', ["children's", "childrens'"], "children's", "Children does not end in s: add 's.",
             before='These are the', after='toys.'),
        fix(['This', 'is', 'my', 'sisters', 'car.'], 3, ['sisters', "sister's"], "sister's", "The car of my sister: add 's."),
        tap('Touch the word with an apostrophe.', ['My', "father's", 'car', 'is', 'red.'], [1], "Father's has the mark '."),
        build('Put the words in the right order.', ['dog', 'is', 'The', 'black.', "man's"], ['The', "man's", 'dog', 'is', 'black.'],
              "The man's dog: the dog of the man."),
    ],
}

# ---------------------------------------------------------------- can
LESSONS['can'] = {
    'film': [
        S([L('Birds can fly.', hl=['can'])],
          cast=[C('b', 'bird', 60, y=60, n=2, gap=30, to=230, toAt=0), C('t', 'tree', 260)], min=2600),
        S([L('I can run very quickly.', by='b'), L('Can and a verb say what someone is able to do.', hl=['can'])],
          cast=[C('b', 'boy', 50, accent=True, pose='run', poseEnd=1, to=200, toAt=0)]),
        S([L('I can swim.'), L('She can swim.'), L('They can swim.'),
           L('Can is the same with every subject. The verb after it has no s.')],
          board=[B(0, ['I', 'can', 'swim.'], r={1: 'b', 2: 'v'}), B(1, ['She', 'can', 'swim.'], r={1: 'b', 2: 'v'}),
                 B(2, ['They', 'can', 'swim.'], r={1: 'b', 2: 'v'}),
                 B(3, ['She', 'can', 'swim.'], r={1: 'b', 2: 'v'}, tag={1: 'no s', 2: 'no s'})]),
        S([L('I can not see the sea from here.'), L("We say can not, cannot or can't.")],
          cast=[C('m', 'man', 140, accent=True, pose='shrug', poseAt=0)],
          board=[B(0, ['I', 'can', 'not', 'see', 'the', 'sea.'], r={1: 'b', 2: 'neg', 3: 'v'}),
                 B(1, ['can', 'not', 'cannot', "can't"], r={1: 'neg', 2: 'neg', 3: 'neg'})]),
        S([L('Can you swim?', by='g', v='woman'), L('Yes, I can.', by='b'), L('To ask, put can first.')],
          cast=[C('g', 'girl', 110, accent=True), C('b', 'boy', 210, face=-1, pose='nod', poseAt=1)]),
    ],
    'rule': {
        'examples': [{'t': 'Birds can fly.'}, {'t': 'I can not see the sea from here.'}, {'t': 'Can you swim? Yes, I can.'},
                     {'t': 'She can read.'}],
    },
    'machine': {'people': [
        {'s': 'I', 'be': 'can', 'rest': 'swim'}, {'s': 'you', 'be': 'can', 'rest': 'read'},
        {'s': 'he', 'be': 'can', 'rest': 'run'}, {'s': 'she', 'be': 'can', 'rest': 'cook'},
        {'s': 'it', 'be': 'can', 'rest': 'fly'}, {'s': 'we', 'be': 'can', 'rest': 'help'},
        {'s': 'they', 'be': 'can', 'rest': 'write'}], 'forms': ['plain', 'not', 'question']},
    'tasks': [
        pick('Put the right words in the space.', ['can swim', 'can swims'], 'can swim', 'The verb after can has no s.',
             before='She', after='.'),
        pick('Put the right words in the space.', ['swim', 'to swim'], 'swim', 'There is no to after can.', before='I can', after='.'),
        build('Make a question.', ['you', 'Can', 'swim?'], ['Can', 'you', 'swim?'], 'Can comes first.'),
        fix(['He', 'cans', 'run.'], 1, ['can', 'cans'], 'can', 'Can is the same with every subject.'),
        pick('Put the right words in the space.', ['can not', 'not can'], 'can not', 'Not comes after can.', before='Fish', after='walk.'),
        pick('Put the right words in the space.', ['can', 'can not'], 'can', 'Birds are able to fly.', before='Birds', after='fly.'),
    ],
}

# ---------------------------------------------------------------- orders
LESSONS['order'] = {
    'film': [
        S([L('Sit down.', by='w', v='woman'), L('To tell someone to do something, begin with the verb.')],
          cast=[C('w', 'woman', 100, accent=True, pose='point'), C('b', 'boy', 210, face=-1, pose='sit', poseAt=1),
                C('c', 'chair', 222, face=-1)]),
        S([L('Open the door.', by='m')],
          cast=[C('m', 'man', 70, accent=True, pose='point'), C('b', 'boy', 150, to=205, toAt=0),
                C('d', 'door', 245, out=0), C('d2', 'door', 245, open=True, in_=0)], min=2600),
        S([L('We do not say you.'), L('The verb comes first.', hl=['open'])],
          board=[B(0, ['You', 'open', 'the', 'door.'], r={1: 'v'}, x=[0]),
                 B(1, ['Open', 'the', 'door.'], r={0: 'v'}, tag={0: 'verb first'})]),
        S([L('Do not touch it.', by='w', v='woman'), L('To tell someone not to do something, use do not.')],
          cast=[C('w', 'woman', 90, accent=True, pose='point'), C('b', 'box', 170), C('g', 'girl', 240, face=-1, pose='reach', poseEnd=0)],
          board=[B(1, ['Do', 'not', 'touch', 'it.'], r={0: 'neg', 1: 'neg', 2: 'v'})]),
        S([L('Close the window, please.', by='g', v='woman'), L('Please makes it kind.', hl=['please'])],
          cast=[C('g', 'girl', 80, accent=True), C('b', 'boy', 160, to=225, toAt=0), C('w', 'window', 260, open=True, out=1),
                C('w2', 'window', 260, in_=1)]),
    ],
    'rule': {
        'examples': [{'t': 'Close the window, please.', 'v': 'woman'}, {'t': 'Do not run in the house.'},
                     {'t': 'Sit down.'}, {'t': 'Please open the door.'}],
    },
    'tasks': [
        pick('Which one tells someone to do something?', ['Open the door.', 'You open the door.'], 'Open the door.',
             'Begin with the verb.'),
        build('Put the words in the right order.', ['door.', 'Close', 'the'], ['Close', 'the', 'door.'], 'The verb comes first.'),
        build('Put the words in the right order.', ['run', 'not', 'Do', 'here.'], ['Do', 'not', 'run', 'here.'], 'Do not, then the verb.'),
        pick('Put the right words in the space.', ['Not', 'Do not'], 'Do not', 'Use do not before the verb.', after='touch it.'),
        fix(['Please', 'sits', 'down.'], 1, ['sit', 'sits'], 'sit', 'The verb has no s.'),
        pick('Put the right word in the space.', ['please', 'do'], 'please', 'Please makes it kind.', before='Help me,', after='.'),
    ],
}
