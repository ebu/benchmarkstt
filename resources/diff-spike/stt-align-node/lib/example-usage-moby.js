const fs = require('fs');
const alignJSONText = require('./index.js');

// file path relative to root
const transcriptText = fs.readFileSync('./sample/data/mobydick-chapter-1/mobydick.txt').toString();
// file path relative to this file.
const transcriptStt = require('../sample/data/mobydick-chapter-1/mobydick-kaldi.json').retval;
// call function 
const result = alignJSONText( transcriptStt, transcriptText);

console.log('-----result-----')
// do something with result 
// console.log(result);

fs.writeFileSync('./sample/output/modbydick-diffs.json', JSON.stringify(result,null,2));