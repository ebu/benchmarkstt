function getDiffsList(opCodes, sttWords, transcriptWords){
    let resultDiffs = [];
    
    opCodes.forEach((opCode)=>{
        const matchType = opCode[0];
        let sttStartIndex = opCode[1];
        let sttEndIndex = opCode[2];
        let baseTextStartIndex = opCode[3];
        let baseTextEndIndex = opCode[4];
        // TODO: do I need to coun the words?
        if(matchType === 'equal' ){
            let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // add the number of words 
            resultDiffs.push({
                stt: sttDataSegment,
                baseText: baseTextSegment,
                matchType: matchType
            });
        }
        if(matchType === 'insert' ){
            // ~stt~ NA
            // base text
            // let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // relative to base text, words not recognised by STT count as deleted
            resultDiffs.push({
                stt: 'NA',
                baseText: baseTextSegment,
                matchType: 'delete'
            });
        }
        if(matchType === 'delete' ){
            // stt
            // ~base text~
            let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            // let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // relative to base text, words deleted from base text by STT count as inserted
            resultDiffs.push({
                stt: sttDataSegment,
                baseText: 'NA',
                matchType: 'insert'
            });
        }
        if(matchType === 'replace' ){
            let sttDataSegment = sttWords.slice(sttStartIndex, sttEndIndex);
            let baseTextSegment = transcriptWords.slice(baseTextStartIndex, baseTextEndIndex);
            // in replace need to count base text word count because stt words not always replaced with equal
            // number of words (?)
            resultDiffs.push({
                stt: sttDataSegment,
                baseText: baseTextSegment,
                matchType: matchType
            });
        };
    })

    return resultDiffs;
}

module.exports = getDiffsList;
