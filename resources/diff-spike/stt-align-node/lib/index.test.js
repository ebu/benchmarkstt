const alignJSONText = require('./index.js');

const baseTextAccurateTranscription = "There was a day, about 10 years ago, when I asked a friend to hold a baby dinosaur robot upside down. "

describe('Re-align accurate transcript', () => {
    test('if STT correct - still expect transposed output', () => {
        const automatedSttTranscription ={ 
            words: [
            { start: 13.05, end: 13.21, word: 'there' },
            { start: 13.21, end: 13.38, word: 'is' },
            { start: 13.38, end: 13.44, word: 'a' },
            { start: 13.44, end: 13.86, word: 'day' },
            { start: 13.86, end: 14.13, word: 'about' },
            { start: 14.13, end: 14.37, word: 'ten' },
            { start: 14.37, end: 14.61, word: 'years' },
            { start: 14.61, end: 15.15, word: 'ago' },
            { start: 15.44, end: 15.67, word: 'when' },
            { start: 15.67, end: 15.82, word: 'i' },
            { start: 15.82, end: 16.19, word: 'asked' },
            { start: 16.19, end: 16.27, word: 'a' },
            { start: 16.27, end: 16.65, word: 'friend' },
            { start: 16.65, end: 16.74, word: 'to' },
            { start: 16.74, end: 17.2, word: 'hold' },
            { start: 17.23, end: 17.32, word: 'a' },
            { start: 17.32, end: 17.63, word: 'baby' },
            { start: 17.63, end: 18.13, word: 'dinosaur' },
            { start: 18.17, end: 18.61, word: 'robot' },
            { start: 18.72, end: 19.17, word: 'upside' },
            { start: 19.17, end: 19.56, word: 'down' } 
        ]
        }

        const expectedResult ={ 
            text: baseTextAccurateTranscription,
            words: [
            { start: 13.05, end: 13.21, word: 'There' },
            { start: 13.21, end: 13.38, word: 'was' },
            { start: 13.38, end: 13.44, word: 'a' },
            { start: 13.44, end: 13.86, word: 'day,' },
            { start: 13.86, end: 14.13, word: 'about' },
            { start: 14.13, end: 14.37, word: '10' },
            { start: 14.37, end: 14.61, word: 'years' },
            { start: 14.61, end: 15.15, word: 'ago,' },
            { start: 15.44, end: 15.67, word: 'when' },
            { start: 15.67, end: 15.82, word: 'I' },
            { start: 15.82, end: 16.19, word: 'asked' },
            { start: 16.19, end: 16.27, word: 'a' },
            { start: 16.27, end: 16.65, word: 'friend' },
            { start: 16.65, end: 16.74, word: 'to' },
            { start: 16.74, end: 17.2, word: 'hold' },
            { start: 17.23, end: 17.32, word: 'a' },
            { start: 17.32, end: 17.63, word: 'baby' },
            { start: 17.63, end: 18.13, word: 'dinosaur' },
            { start: 18.17, end: 18.61, word: 'robot' },
            { start: 18.72, end: 19.17, word: 'upside' },
            { start: 19.17, end: 19.56, word: 'down.' } 
        ]
        }

    const result = alignJSONText( automatedSttTranscription, baseTextAccurateTranscription);
      expect(result).toEqual(expectedResult);
    });
});

describe('Re-align  transcript - deletion', () => {
    test('1 deletion', () => {
        const automatedSttTranscription ={ 
            words: [
            { start: 13.05, end: 13.21, word: 'there' },
            { start: 13.21, end: 13.38, word: 'is' },
            { start: 13.38, end: 13.44, word: 'a' },
            { start: 13.44, end: 13.86, word: 'day' },
            { start: 13.86, end: 14.13, word: 'about' },
            { start: 14.13, end: 14.37, word: 'ten' },
            { start: 14.37, end: 14.61, word: 'years' },
            { start: 14.61, end: 15.15, word: 'ago' },
            { start: 15.44, end: 15.67, word: 'when' },
            { start: 15.67, end: 15.82, word: 'i' },
            { start: 15.82, end: 16.19, word: 'asked' },
            { start: 16.19, end: 16.27, word: 'a' },
            { start: 16.27, end: 16.65, word: 'friend' },
            { start: 16.65, end: 16.74, word: 'to' },
            { start: 16.74, end: 17.2, word: 'hold' },
            { start: 17.23, end: 17.32, word: 'a' },
            { start: 17.32, end: 17.63, word: 'baby' },
            { start: 17.63, end: 18.13, word: 'dinosaur' },
            { start: 18.17, end: 18.61, word: 'robot' },
            { start: 18.72, end: 19.17, word: 'upside' },
            { start: 19.17, end: 19.56, word: 'down' } 
        ]
        }

        const expectedResult ={ 
            text: baseTextAccurateTranscription,
            words: [
            { start: 13.05, end: 13.21, word: 'There' },
            { start: 13.21, end: 13.38, word: 'was' },
            { start: 13.38, end: 13.44, word: 'a' },
            { start: 13.44, end: 13.86, word: 'day,' },
            { start: 13.86, end: 14.13, word: 'about' },
            { start: 14.13, end: 14.37, word: '10' },
            { start: 14.37, end: 14.61, word: 'years' },
            { start: 14.61, end: 15.15, word: 'ago,' },
            { start: 15.44, end: 15.67, word: 'when' },
            { start: 15.67, end: 15.82, word: 'I' },
            { start: 15.82, end: 16.19, word: 'asked' },
            { start: 16.19, end: 16.27, word: 'a' },
            { start: 16.27, end: 16.65, word: 'friend' },
            { start: 16.65, end: 16.74, word: 'to' },
            { start: 16.74, end: 17.2, word: 'hold' },
            { start: 17.23, end: 17.32, word: 'a' },
            { start: 17.32, end: 17.63, word: 'baby' },
            { start: 17.63, end: 18.13, word: 'dinosaur' },
            { start: 18.17, end: 18.61, word: 'robot' },
            { start: 18.72, end: 19.17, word: 'upside' },
            { start: 19.17, end: 19.56, word: 'down.' } 
        ]
        }

    const result = alignJSONText( automatedSttTranscription, baseTextAccurateTranscription);
      expect(result).toEqual(expectedResult);
    });
});