# The Alignment problem
The main Alignment problem this module is trying to solve is:
Give some accurate base text, and some speech to text results that are not 100% accurate, how do you transpose the timings from the STT results to the words of the base text?
Considering that there might be inserted, deleted, replaced and matched words in the comparison.

## Example

If I have a sentence - let’s assume it’s accurate base text

```
"But we'll back with more from our correspondents' next Saturday morning as usual."
```

and a json - let’s assume is from STT so timecodes are ok, but text might not be accurate (and might also have insertion, deletions, and substitutions differences from base text)

```json
[
    {
        "start": 1672.9,
        "end": 1673.14,
        "text": "But",
    },
    {
      "start": 1673.14,
      "end": 1673.24,
      "text": "we'll"
    },
    {
      "start": 1673.24,
      "end": 1673.52,
      "text": "back"
    },
    {
      "start": 1673.52,
      "end": 1673.64,
      "text": "with"
    },
    {
      "start": 1673.64,
      "end": 1673.81,
      "text": "more"
    },
    {
      "start": 1673.81,
      "end": 1674,
      "text": "from"
    },
    {
      "start": 1674,
      "end": 1674.07,
      "text": "our"
    },
    {
      "start": 1674.07,
      "end": 1674.95,
      "text": "correspondents'"
    },
    {
      "start": 1674.95,
      "end": 1675.24,
      "text": "next"
    },
    {
      "start": 1675.24,
      "end": 1675.66,
      "text": "Saturday"
    },
    {
      "start": 1675.66,
      "end": 1676.08,
      "text": "morning"
    },
    {
      "start": 1676.08,
      "end": 1676.22,
      "text": "as"
    },
    {
      "start": 1676.22,
      "end": 1676.73,
      "text": "usual."
    },
    {
      "start": 1676.97,
      "end": 1677.16,
      "text": "Do"
    }
  ];
```

How would you go about re-aligning these? Meaning - generating a json that has words with timecodes from STT and accurate text from base text?