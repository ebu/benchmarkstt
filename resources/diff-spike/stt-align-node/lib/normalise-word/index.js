const converterNumbersToWords = require('number-to-words');
/**
 * https://stackoverflow.com/questions/175739/built-in-way-in-javascript-to-check-if-a-string-is-a-valid-number
 * @param {*}  num 
 * @return {boolean} - if it's a number true, if it's not false.
 */
function isANumber(num){
    return !isNaN(num) && num!=='';
}

/**
 * removes capitalization, punctuation and converts numbers to letters
 * @param {string} wordText - word text 
 * @return {string}
 * handles edge case if word is undefined, and returns undefined in that instance
 */
function normaliseWord(wordText){
    if(wordText!== undefined){
        let wordTextResult = wordText.toLowerCase().trim().replace(/[^a-z|0-9]+/g, '');
        if(isANumber(wordTextResult)){
            console.log('console',wordTextResult)
            return converterNumbersToWords.toWords(wordTextResult);
        }
        return wordTextResult;
    }else{
        return wordText
    }
        
}

module.exports = normaliseWord;