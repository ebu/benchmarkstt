// TODO: 
// -  [ ] add possibility to hide inserted, deleted, and base text for replaced, to see stt?

function diffsListToHtml(diffsList){
    let htmlResult = [];
    const style = `<style>
    .equal{
        cursor: pointer;
    }

    .delete {
        display: inline-block;
        position: relative;
        // background-color: #ffe5e5;
        // background-color: #ff0000;
        // color: white;
        cursor: no-drop;
    }

    .delete:before {
        content: "~~~~~~~~~~~~";
        font-size: 0.6em;
        font-weight: 700;
        font-family: Times New Roman, Serif;
        color: red;
        width: 100%;
        position: absolute;
        top: 12px;
        left: -1px;
        overflow: hidden;
    }

    .insert{
        text-decoration-line: line-through;
        background-color: #e5e5ff;
        cursor: pointer;
    }

    .insert {
        display: inline-block;
        position: relative;
        cursor: pointer;
    }

    .insert:before {
        content: "~~~~~~~~~~~~";
        font-size: 0.6em;
        font-weight: 700;
        font-family: Times New Roman, Serif;
        color: blue;
        width: 100%;
        position: absolute;
        top: 12px;
        left: -1px;
        overflow: hidden;
    }

    .replaceStt{
        display: inline-block;
        position: relative;
        cursor: pointer;
    }

    .replaceStt:before {
        content: "~~~~~~~~~~~~";
        font-size: 0.6em;
        font-weight: 700;
        font-family: Times New Roman, Serif;
        color:  red;
        width: 100%;
        position: absolute;
        top: 12px;
        left: -1px;
        overflow: hidden;
    }


    .replaceBaseText{
        display: inline-block;
        position: relative;
        // background-color: #99cc99;
        cursor: no-drop;
    }

    .replaceBaseText:before {
        content: "~~~~~~~~~~~~";
        font-size: 0.6em;
        font-weight: 700;
        font-family: Times New Roman, Serif;
        color:  #99cc99;
        width: 100%;
        position: absolute;
        top: 12px;
        left: -1px;
        overflow: hidden;
    }

    span.replaceBaseTextLine.line{
        background-color: #e5f2e5;
    }

    span.replaceBaseTextLine.line:after{
        content: "]";
        color: #99cc99;
    }

    span.replaceBaseTextLine.line:before{
        content: "[";
        color: #99cc99;
    }

    span.replaceSttLine.line{
        background-color: #ffe5e5;
    }

    span.replaceSttLine.line:after{
        content: "]";
        color: red;
    }
    span.replaceSttLine.line:before{
        content: "[";
        color: red;
    }

    .unplayedWord{
        color:grey!important;
    }

    video.videoPreview {
        margin-left: auto;
        margin-right: auto;
        display: block;
    }
    </style>`


    htmlResult.push(style);

    let styleLegend =`
    Equal: Some equal text
    <br>
    Inserted: <span class='insert'>an</span> <span class='insert'>inserted</span> <span class='insert'>word</span>
    <br>
    Deleted:<span class='delete'>a</span>  <span class='delete'>deleted</span> <span class='delete'>word</span>
    <br>
    Replaced:<span class='replaceBaseTextLine line'>
    <span class='replaceBaseText '>Some</span>
    <span class='replaceBaseText '>base</span>
    <span class='replaceBaseText '>text</span>
    <span class='replaceBaseText '>line</span>
    </span>
    <span class='replaceSttLine line'>
    <span class="replaceStt ">replaced</span>
    <span class="replaceStt ">by</span>
    <span class="replaceStt ">stt</span>
    <span class="replaceStt ">hypothesis</span>
    </span>
    <br>
    <hr>
    <br>
    `;

    htmlResult.push(styleLegend)


    htmlResult.push(`
    Video <input class='videoInput' type="file" name="video" accept="video/*, audio/*">
    <br>
    <video class='videoPreview' style="width: 40vw;" controls></video>

    <script>
    const videoEl =  document.querySelector('.videoPreview');
    const videoInputEl = document.querySelector('.videoInput');


    videoInputEl.addEventListener('change', function(e) {
        console.log(e.target.value, this.files)
        var url = URL.createObjectURL(this.files[0]);
        document.querySelector('.videoPreview').src =url; 
    });


    document.querySelector('.text').addEventListener('click', function(e) {
        console.log(e.target.dataset.start);
        videoEl.currentTime = e.target.dataset.start;
        videoEl.play();
    })

    document.querySelector('video').addEventListener("timeupdate", function(){
        console.log('time updated', this.currentTime)
        let currentTime = this.currentTime;
        let wordsEl = document.querySelectorAll('.word');
        wordsEl.forEach((word)=>{
            if(word.dataset.start >= currentTime){
                word.classList.add("unplayedWord");
            }
            else{
                word.classList.remove("unplayedWord");
            }
        })
    });

    </script>
    <hr>`)

    function createSpanWord(text, className, startTime){
        return `<span class='${className} word' data-start='${startTime}'>${text}</span>`
    }

    function createLine(elements, className){
        return `<span class='${className} line'>${elements}</span>`
    }

    diffsList.forEach(element => {
        const matchType = element.matchType;

        if(matchType === 'equal' ){
            // TODO: do word level - use STT times and text
            let words = element.stt.map((w)=>{
                return createSpanWord(w.word,'equal',w.start)
            })
            htmlResult.push(words.join(' '))
        }
        if(matchType === 'insert' ){
            let words = element.stt.map((w)=>{
                return createSpanWord(w.word,'insert',w.start)
            })
            htmlResult.push(words.join(' '))
        }
        if(matchType === 'delete' ){
            let words = element.baseText.map((w)=>{
                return createSpanWord(w,'delete')
            })
            htmlResult.push(words.join(' '))
        }
        if(matchType === 'replace' ){
            const wordsStt = element.stt.map((w)=>{
                return createSpanWord(w.word,'replaceStt',w.start)
            })
            const wordsBaseText = element.baseText.map((w)=>{
                return createSpanWord(w,'replaceBaseText')
            })

            const wordsSttLine =  createLine(wordsStt.join(' '),'replaceSttLine')
            const baseTextLine =  createLine(wordsBaseText.join(' '),'replaceBaseTextLine')
            const replacedLine = baseTextLine+wordsSttLine ;
            htmlResult.push(replacedLine)
        } 

    
        
    });
    htmlResult = `<div class='text'>${htmlResult.join(' ')}</div>`

    return htmlResult;
}

module.exports.diffsListToHtml = diffsListToHtml;
