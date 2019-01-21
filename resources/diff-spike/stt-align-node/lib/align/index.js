const linear = require('everpolate').linear;
// using neighboring words to set missing start and end time when present 
function interpolationOptimization(wordsList){
    return wordsList.map((word, index)=>{
        let wordTmp = word;
        // setting the start time of each unmatched word to the previous word’s end time - when present
        // does not first element in list edge case
       
        if(('start' in word) &&( index !== 0)){
            let previousWord = wordsList[index-1];
            if( 'end' in previousWord){
                wordTmp = {
                    start: previousWord.end,
                    end: word.end,
                    word: word.word
                }
            }
        }
        // TODO: handle first item ?
        // setting the end time of each unmatched word to the next word’s start time - when present
        // does handle last element in list edge case
         if(('end' in word) &&( index !== (wordsList.length-1))){
            let nextWord = wordsList[index+1];
            if( 'start' in nextWord){
                wordTmp = {
                    end: nextWord.start,
                    start: word.start,
                    word: word.word
                }
            }
        }
        // TODO: handle last item ?
        return wordTmp;
    });
}

function interpolate(wordsList){
    let words = interpolationOptimization(wordsList)
    const indicies = [...Array(words.length).keys()];
    let indiciesWithStart = [];
    let indiciesWithEnd = [];
    let startTimes = [];
    let endTimes = [];
    // interpolate times for start
    for (let i=0; i<words.length; i++) {
        if('start' in words[i]){
        indiciesWithStart.push(i);
        startTimes.push(words[i].start);
      }
    }
     // interpolate times for end
    for (let i=0; i<words.length; i++) {
        if('end' in words[i]){
        indiciesWithEnd.push(i);
        endTimes.push(words[i].end);
      }
    }
    // http://borischumichev.github.io/everpolate/#linear
    const outStartTimes = linear(indicies, indiciesWithStart, startTimes);
    const outEndTimes = linear(indicies, indiciesWithEnd, endTimes);
    words = words.map((word, index)=>{
        if (!('start' in word)){
            word.start = outStartTimes[index];
        }
        if (!('end' in word) ){
            word.end = outEndTimes[index];
        }
        return word;
    })
    return words;
}

function alignRefTextWithSTT(opCodes, sttWords, transcriptWords){
    // # create empty list to receive data
    // transcriptData = [{} for _ in range(len(transcriptWords))]
    let transcriptData = [];
    // empty objects as place holder 
    transcriptWords.forEach(()=>{
        transcriptData.push({});
    })

    opCodes.forEach((opCode)=>{
        let matchType = opCode[0];
        let sttStartIndex = opCode[1];
        let sttEndIndex = opCode[2];
        let baseTextStartIndex = opCode[3];
        
        if(matchType === 'equal' ){
            // slice does not not include the end - hence +1
            let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            transcriptData.splice(baseTextStartIndex, sttDataSegment.length, ...sttDataSegment);
        }
  
        // # populate transcriptData with matching words
        transcriptData.forEach((wordObject, index)=>{
            wordObject.word = transcriptWords[index];
        })
        // # replace words with originals
        
    })
    // # fill in missing timestamps
    return interpolate(transcriptData);
}

module.exports = alignRefTextWithSTT;