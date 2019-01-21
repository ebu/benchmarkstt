import re, json, difflib, numpy

def interpolate(data):

    # create a numpy array of times with NaN for missing data
    start = [datum.get('start', None) for datum in data]
    times = numpy.array(start, dtype=numpy.float)

    # linearly interpolate the missing times
    indicies = numpy.arange(len(times))
    notNan = numpy.logical_not(numpy.isnan(times))
    timesInterp = numpy.interp(indicies, indicies[notNan], times[notNan])
 
    for i in range(len(data)):
        data[i]['start'] = timesInterp[i]
    return data

def alignWords(sttData, transcriptWords):

    # extract list of words
    sttWords=[words.get('word') for words in sttData]

    # convert words to lowercase and remove numbers and special characters
    sttWordsStripped = [re.sub('[^a-z]', '', word.lower()) for word in sttWords]
    transcriptWordsStripped = [re.sub('[^a-z]', '', word.lower()) for word in transcriptWords]

    # create empty list to receive data
    transcriptData = [{} for _ in range(len(transcriptWords))]

    # populate transcriptData with matching words
    matcher = difflib.SequenceMatcher(None, sttWordsStripped, transcriptWordsStripped)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            transcriptData[j1:j2] = sttData[i1:i2]
    
    # replace words with originals
    for i in range(len(transcriptData)):
        transcriptData[i]['word'] = transcriptWords[i];

    # fill in missing timestamps
    return interpolate(transcriptData)

# def alignJSON(sttFilename, transcriptFilename):

#     # load JSON data
#     with open(sttFilename) as sttFile:
#         sttData=json.load(sttFile)['words']
#     with open(transcriptFilename) as transcriptFile:
#         transcriptText=json.load(transcriptFile)['text']

#     # align words
#     aligned = alignWords(sttData, transcriptText.split())

#     return {'text': transcriptText, 'words': aligned}

def alignJSONText(sttFilename, transcriptText):

    # load JSON data
    with open(sttFilename) as sttFile:
        sttData=json.load(sttFile)['words']

    # align words
    aligned = alignWords(sttData, transcriptText.split())

    return {'text': transcriptText, 'words': aligned}


alignJSONText('./sample/data/short/transcript.txt','this is the transcript')