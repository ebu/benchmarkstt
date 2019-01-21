const difflib = require('difflib');
const normaliseWord = require('./normalise-word/index.js');
const countDiffs = require('./count-diffs/index.js');
const getDiffsList = require('./diffs-list/index.js');
const alignRefTextWithSTT = require('./align/index.js');
const calculateWordDuration = require('./calculate-word-duration/index.js');
const diffsListToHtml = require('./diffs-list-to-html/index.js').diffsListToHtml;

/**
 * 
 * @param {array} sttData - array of STT words
 * @param {array} transcriptWords - array of base text accurate words
 * @return {array} opCodes - diffs opcodes
 */
function diffGetOpcodes(sttWords, transcriptWords){   
    // # convert words to lowercase and remove numbers and special characters
    // sttWordsStripped = [re.sub('[^a-z]', '', word.lower()) for word in sttWords]
    const sttWordsStripped = sttWords.map((word)=>{
        return normaliseWord(word.word);
    })
  
    // transcriptWordsStripped = [re.sub('[^a-z]', '', word.lower()) for word in transcriptWords]
    const transcriptWordsStripped = transcriptWords.map((word)=>{
        return normaliseWord(word);
    })
    
    const matcher = new difflib.SequenceMatcher(null,   sttWordsStripped, transcriptWordsStripped);
    const opCodes  = matcher.getOpcodes();
    return opCodes;
}


function removeNewLinesFromRefText(refText){
    return refText.trim().replace(/\n\n/g,'').replace(/\n/g,' ')
}

function convertRefTextToList(refText){
    const transcriptTextWithoutLineBreaks = removeNewLinesFromRefText(refText);
    const transcriptTextArray = transcriptTextWithoutLineBreaks.split(' ');
    return transcriptTextArray;
}

/**
 * 
 * @param {json} sttWords - stt transcript json
 * @param {array} sttWords.words
 * @param {float} sttWords.words[0].start
 * @param {float} sttWords.words[0].end
 * @param {float} sttWords.words[0].word
 * @param {string} transcriptText - plain text corrected transcript, base text
 */
function diff(sttWords, transcriptText){
    const transcriptTextArray = convertRefTextToList(transcriptText);
    const diffResults = diffGetOpcodes(sttWords, transcriptTextArray);
    return diffResults;
}


function diffsListAsHtml(sttWords, transcriptText){
    const sttWordsList = sttWords.words;
    const opCodes =  diff(sttWordsList, transcriptText);
    const transcriptWords = convertRefTextToList(transcriptText);
    const alignedResults = getDiffsList(opCodes,sttWordsList,transcriptWords);
    return diffsListToHtml(alignedResults);;
}



function diffsList(sttWords, transcriptText){
    const sttWordsList = sttWords.words;
    const opCodes =  diff(sttWordsList, transcriptText);
    const transcriptWords = convertRefTextToList(transcriptText);
    const alignedResults = getDiffsList(opCodes,sttWordsList,transcriptWords);
    return alignedResults;
}

function diffsCount(sttWords, transcriptText){
    const sttWordsList = sttWords.words;
    const opCodes =  diff(sttWordsList, transcriptText);
    const transcriptWords = convertRefTextToList(transcriptText);
    const alignedResults = countDiffs(opCodes,sttWordsList,transcriptWords);
    return alignedResults;
}

function alignSTT(sttWords, transcriptText){
    const sttWordsList = sttWords.words;
    const opCodes =  diff(sttWordsList, transcriptText);
    const transcriptWords = convertRefTextToList(transcriptText);
    const alignedResults = alignRefTextWithSTT(opCodes,sttWordsList,transcriptWords);
    return alignedResults;
}

module.exports.diffsList = diffsList;

module.exports.diffsCount = diffsCount;

module.exports.alignSTT = alignSTT; 

module.exports.calculateWordDuration = calculateWordDuration;

module.exports.diffsListToHtml = diffsListToHtml;

module.exports.diffsListAsHtml = diffsListAsHtml;