# Course pipeline

The source of truth for the 1,000 words. Edit `src/b01.txt` .. `src/b10.txt`
(one line per word: `word|pos|mode|definition|example1|example2`), then:

```
python3 lint.py                 # every word in every sentence must be one of the 1,000
python3 build_course.py         # orders the words into 200 steps -> out/course.json
(cd out && cp ../vocab.py . && python3 check_course.py)
cp out/course.json ../../content/ && python3 ../build_data.py   # rebuild data-1..4.txt
```

The order is deterministic: the same source always gives the same steps.
