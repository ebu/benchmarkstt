ASSUMPTIONS:
1. Only European languages are in scope. A list of supported languages may be required. 
1. The defined schema and algorithms can be applied equally to all languages in scope. If they can't, language-specific components will be required.     

<table>
	<tr>
		<th>Version</th>
		<th>Provider integration</th>
		<th>Transcript processing</th>
		<th>Reference preparation</th>
		<th>Analysis</th>
		<th>Results</th>
	</tr>
	<tr>
		<td>1</td>
		<td>Manual. Send audio for transcription and retrieve transcript using a UI.</td>
		<td>Define native schema (words only) and use it to convert to native JSON. 
			<pre>
[
 {text: "hello"},
 {text: "world"}
]
			</pre>
		</td>
		<td>String, words only</td>
		<td>WER algorithm and documentation<hr>Diff algorithm: insertions, deletions, insertions and matches</td>
		<td>WER % per vendor<hr>Diff metrics and structured report</td>		
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
