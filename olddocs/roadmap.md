Benchmarking toolkit road map
=============================  
<table>
	<tr>
		<th>V</th>
		<th>Provider integration</th>
		<th>Transcript processing</th>
		<th>Reference preparation</th>
		<th>Analysis</th>
		<th>Results</th>
	</tr>
	<tr>
		<td><a href="https://github.com/ebu/ai-benchmarking-stt/blob/master/docs/releases/1.0/README.md">1</a></td>
		<td>Manual. Send audio for transcription and retrieve transcript using a UI. The audio file contains clean standard speech.</td>
		<td>Define a native schema, initially for words only. Use the native schema to convert to normalized JSON. 
			<pre>
[
 {text: "hello"},
 {text: "world"}
]
			</pre>
		</td>
		<td>String, words only. Without timings, this reference data is easier to produce.</td>
		<td>WER algorithm and pseudo-code with discussion.<hr>Diff algorithm: substitutions, deletions, insertions, correct words.</td>
		<td>WER % per vendor<hr>Detailed diff metrics (s/d/i/c) available in a structured format.</td>		
	</tr>
	<tr>
		<td>2</td>
		<td>Create 1-2 adapters and provide instructions for users to add their own.</td>
		<td>Add timings to native schema
			<pre>
[
 {
  begin: 0.234, 
  end: 0.654, 
  text: "hello"
 },
 ...
]
</pre>
		</td>
		<td>JSON (word and timings) using native schema</td>
		<td>Define timing accuracy algorithm<hr>Timings diff algorithm</td>
		<td>Average time deviation from reference?</td>
	</tr>
	<tr>
		<td>3</td>
		<td></td>
		<td>Add word weighting to native schema (e.g. proper nouns)</td>
		<td>Mark word weighting using native schema</td>
		<td>Define 'Weighted WER' algorithm<hr>Weighted diff</td>
		<td>Visualise results?</td>
	</tr>
