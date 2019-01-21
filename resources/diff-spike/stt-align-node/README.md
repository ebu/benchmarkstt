# Stt-align-node

node version of [stt-align](https://github.com/bbc/stt-align) by Chris Baume - R&D.
<!-- 
_One liner + link to confluence page_

_Screenshot of UI - optional_ -->

_Work in progress_
 
## Setup

_stack - optional_

_How to build and run the code/app_

 

## Usage

```js
const alignJSONText = require('./index.js');

const transcriptText = 'There was a day, about 10 years ago, when I asked a friend to hold a baby dinosaur robot upside down. ';

const transcriptStt = { 
    words: [
    { start: 13.05, end: 13.21, word: 'there' },
    // { start: 13.21, end: 13.38, word: 'is' },
    { start: 13.38, end: 13.44, word: 'a' },
    // { start: 13.44, end: 13.86, word: 'day' },
    // { start: 13.86, end: 14.13, word: 'about' },
    { start: 14.13, end: 14.37, word: 'ten' },
    // { start: 14.37, end: 14.61, word: 'years' },
    { start: 14.61, end: 15.15, word: 'ago' },
    { start: 15.44, end: 15.67, word: 'when' },
    // { start: 15.67, end: 15.82, word: 'i' },
    // { start: 15.82, end: 16.19, word: 'asked' },
    // { start: 16.19, end: 16.27, word: 'a' },
    // { start: 16.27, end: 16.65, word: 'friend' },
    { start: 16.65, end: 16.74, word: 'to' },
    // { start: 16.74, end: 17.2, word: 'hold' },
    // { start: 17.23, end: 17.32, word: 'a' },
    // { start: 17.32, end: 17.63, word: 'baby' },
    // { start: 17.63, end: 18.13, word: 'dinosaur' },
    // { start: 18.17, end: 18.61, word: 'robot' },
    // { start: 18.72, end: 19.17, word: 'upside' },
    { start: 19.17, end: 19.56, word: 'down' } 
    ]
}

// call function 
const result = alignJSONText( transcriptStt, transcriptText);
// do something with the result
console.log(result);
```

See [`/lib/example-usage`](./lib/example-usage.js) for an example that you can run with `npm run example`.

### Example output
 ```js
 { text: 'There was a day, about 10 years ago, when I asked a friend to hold a baby dinosaur robot upside down. ',
  words:
   [ { start: 13.05, end: 13.21, word: 'There' },
     { word: 'was', start: 13.215, end: 13.325 },
     { start: 13.38, end: 13.44, word: 'a' },
     { word: 'day,', start: 13.626000000000001, end: 13.84 },
     { word: 'about', start: 13.872, end: 14.239999999999998 },
     { word: '10', start: 14.118, end: 14.639999999999999 },
     { word: 'years', start: 14.364, end: 15.04 },
     { end: 15.44, start: 14.61, word: 'ago,' },
     { start: 15.15, end: 15.67, word: 'when' },
     { word: 'I', start: 15.450000000000001, end: 15.883999999999999 },
     { word: 'asked', start: 15.75, end: 16.098 },
     { word: 'a', start: 16.05, end: 16.311999999999998 },
     { word: 'friend', start: 16.35, end: 16.525999999999996 },
     { start: 16.65, end: 16.74, word: 'to' },
     { word: 'hold',
       start: 17.009999999999998,
       end: 17.142857142857142 },
     { word: 'a', start: 17.369999999999997, end: 17.545714285714286 },
     { word: 'baby',
       start: 17.729999999999997,
       end: 17.948571428571427 },
     { word: 'dinosaur', start: 18.09, end: 18.35142857142857 },
     { word: 'robot', start: 18.45, end: 18.754285714285714 },
     { word: 'upside', start: 18.81, end: 19.15714285714286 },
     { start: 19.17, end: 19.56, word: 'down.' } ] }
```

## System Architecture

<!-- _High level overview of system architecture_ -->

Node version of [stt-align](https://github.com/bbc/stt-align) by Chris Baume - R&D.

In _pseudo code_

- input, output as described in the example usage. 
    - Accurate base text transcription, string.
    - Array of word objects transcription from STT service.

- Align words
    - normalize words, my removing capitalization and punctuation and converting numbers to letters
    - generate array list of words from base text, and array list of words from stt transcript. 
        - get [opcodes](https://docs.python.org/2/library/difflib.html#difflib.SequenceMatcher.get_opcodes)  using `difflib` comparing two arrays
        - for equal matches, add matched STT word objects segment to results array base text index position.
        - Then iterate to result array to replace STT word objects text with words from base text  

    - interpolate missing words
        - calculates missing timecodes
        - first optimization 
            -  using neighboring words to do a first pass at setting missing start and end time when present 
            - 
        - Then Missing word timings are interpolated using interpolation library [`'everpolate`](http://borischumichev.github.io/everpolate/#linear).



## Development env

 <!-- _How to run the development environment_

_Coding style convention ref optional, eg which linter to use_

_Linting, github pre-push hook - optional_ -->

- node `10`
- npm `6.1.0`
 

## Build

_How to run build_

NA
<!-- only needed if adding ES6 and babel, with dist folder for npm ? -->
  

## Tests
_How to carry out tests_


```
npm run test
```

- [ ] add more tests 

## Deployment

_How to deploy the code/app into test/staging/production_

TBC 

- [ ] deploy to npm 

<!-- TODOs:

- [ ] Clean up repository
- [ ] change baseText and sttText mentions to be `referenceText` and `hypothesisText`
- [ ] add linting 
- [ ] add babel(?)
- [ ] change if else to be switch statments
 -->