// counting diffs in difflib opCodes
function countDiffs(opCodes, sttWords, transcriptWords){
    let resultDiffCount = {
        equal: 0,
        insert: 0,
        replace: 0,
        delete: 0, 
        baseTextTotalWordCount: transcriptWords.length
    }

    opCodes.forEach((opCode)=>{
        const matchType = opCode[0];
        let sttStartIndex = opCode[1];
        let sttEndIndex = opCode[2];
        let baseTextStartIndex = opCode[3];
        let baseTextEndIndex = opCode[4];
        // TODO: Counting the words
        if(matchType === 'equal' ){
            // let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // add the number of words 
            resultDiffCount.equal += baseTextSegment.length;
        }
        if(matchType === 'insert' ){
            // ~stt~ NA
            // base text
            // let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // relative to base text, words not recognised by STT count as deleted
            resultDiffCount.delete += baseTextSegment.length; 
        }
        if(matchType === 'delete' ){
            // stt
            // ~base text~
            let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            // let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // relative to base text, words deleted from base text by STT count as inserted
            resultDiffCount.insert += sttDataSegment.length;
        }
        if(matchType === 'replace' ){
            let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // in replace need to count base text word count because stt words not always replaced with equal
            // number of words (?)
            resultDiffCount.replace += baseTextSegment.length;
        }
        // console.log(resultDiffCount)
    })

    return resultDiffCount;
}


module.exports = countDiffs;