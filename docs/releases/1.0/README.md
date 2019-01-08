DRAFT Release 1.0 (MVP) scope 
=============================
This document describes the minimal set of components and functionality for the first release of the STT benchmarking toolkit.

In order to focus the initial development on the important part of the system, this version will not include integrations with the providers. Subsequent versions can create adapters that given the credentials for the STT service and the audio or video to transcribe can automate the request.  

This version will focus on defining the diff and WER algorithms and return WER scores for transcripts manually submitted to a small number of cloud providers. 

For an overview of the system and component names see https://github.com/ebu/ai-benchmarking-stt/wiki

Assumptions
-----------
1. Only European languages are in scope. A list of supported languages may be required. 
1. The defined schema and algorithms can be applied equally to all languages in scope. If they can't, language-specific components will be required.   

Parts of the system
--------------------
This release will include:

### Test data
The reference will be a simple string containing words only (i.e. no timings, punctuation marks or non-word sounds such as 'erm'). The audio must also contain words only (this could be as simple as a recording of someone reading out some text). 

### Transcript schema
The basis for a future comprehensive schema for the reference and the hypothesis. In this release it will include words only, for example:
```javascript
[
	{"text": "hello"},
	{"text": "world"}
]
``` 

### Hypothesis normalisers
This component will convert from the different formats of the hypotheses to a single JSON format using the transcript schema. A documentation guide helps provide guidance to create new converters to add more providers to the system.

### Analysis 
- Diff component: Define the diff algorithm and use it to identify deletions, insertions, matches and substitutions between the reference and the hypothesis strings. This component could use a diffing library under hood and/or something more appropriate. 
- WER analyser: Define the WER algorithm and provide documentation with pseudo-code so that users are clear about the approach taken, pros and cons and any limitations. It is important to be transparent about the diff and WER definitions because the algorithms are likely to affect the results.   

### Results
- WER score for each provider, in percent. 
- Number of deletions, insertions, substitutions and matches for each provider
- Detailed results in a structured format (e.g. JSON) that can be used for further visualisation or processing (out of scope).





