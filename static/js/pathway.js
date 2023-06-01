// function to sort objects by multiple fields 
function getSortMethod() {
    var _args = Array.prototype.slice.call(arguments);
    return function(a, b){
        for(var x in _args){
            var ax = a[_args[x].substring(1)];
            var bx = b[_args[x].substring(1)];
            var cx;

            ax = typeof ax == "string" ? ax.toLowerCase() : ax / 1;
            bx = typeof bx == "string" ? bx.toLowerCase() : bx / 1;

            if(_args[x].substring(0,1) == "-"){cx = ax; ax = bx; bx = cx;}
            if(ax != bx){return ax < bx ? -1 : 1;}
        }
    }
}


// function to copy text to clipboardData
// no direct commands
// inserted into value of a newly created <textarea>, which is then selected, its value is copied to the clipboard and then it gets removed from the document
function copyToClipboard(texts) {
    var dummy = document.createElement("textarea");
    // to avoid breaking orgain page when copying more words
    // cant copy when adding below this code
    // dummy.style.display = 'none'
    document.body.appendChild(dummy);
    //Be careful if you use texarea. setAttribute('value', value), which works with "input" does not work with "textarea". – Eduard
    dummy.value = texts;
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
}


// onclick function to do pathway analysis
// do not be affected by table filtering, that is, all entries will be included for ranking
$('#DAVID').click(function () {
    // number of genes for pathway analysis
    var num = document.getElementById('mrna_num').value;

    // prediction tool for current result, get from print message
    var cur_tool = document.getElementById('message').textContent.split(' ')[1];
    // change it to integers (0: RNAhybrid; 1:IntaRNA)
    if (cur_tool == 'Consensus') {
        cur_tool = 0;
    } else if (cur_tool == 'IntaRNA') {
        cur_tool = 1;
    } else if (cur_tool == 'RNAhybrid') {
        cur_tool = 0;
    }
    
    // get values from datatable
    var table = $('#result_table').DataTable()
    
    // get column value, index start from 0
    // all column values are raw value before rendering by render function
    // you can get all rows no matter whether filter is activated
    // sorting will change the order of rows you get, but it does not matter
    
    // 4th column: gene ID
    var gene = table.column(3).data()
    // 7th column: free energy
    var mfe = table.column(6).data()
    // 8th column: matching length
    var mcl = table.column(7).data()
    // 9th column: prediction tool
    var tool = table.column(8).data()
    
    // extract ensembl IDs, also not include empty strings (entried without gene ID)
    var len = gene.length
    var obj = []
    for (var i = 0; i < len; i++) {
        // only predictions from needed tool are included
        if (tool[i] == cur_tool && gene[i].length > 0) {
            obj.push({ 'id': gene[i], 'mfe': parseFloat(mfe[i]), 'mcl': parseInt(mcl[i]) })
        }
    }


    // sort gene ids based mfe and mcl
    // +/- to indicate ascending or descending order
    // sort genes with lowest mfe first
    // with ties going to the genes with the highest mcl
    // sorting result checked, it's corrected
    obj.sort(getSortMethod('+mfe', '-mcl'))

    // get needed sorted gene ids
    if (num > obj.length) {
        num = obj.length
    }
    
    var sorted_ids = []
    for (var i = 0; i < num; i++) {
        sorted_ids[i] = obj[i].id
    }
    
    // copy procedure checked, list is completed, and the order is corrected
    copyToClipboard(sorted_ids)
    
    // David can also support both human and mouse 
    alert('A list of top ' + num + ' Gene Ensemble IDs copied to clipboard. Paste them into the input box in David website and start Gene Enrichment Analysis')
    
    // open a new window
    window.open('https://david.ncifcrf.gov/tools.jsp')
} )


// onclick function to do GO analysis by ShinyGO
// do not be affected by table filtering, that is, all entries will be included for ranking
// only change the re-directing website
$('#ShinyGO').click(function () {
    // number of genes for pathway analysis
    var num = document.getElementById('mrna_num').value;

    // prediction tool for current result, get from print message
    var cur_tool = document.getElementById('message').textContent.split(' ')[1];
    // change it to integers (0: RNAhybrid; 1:IntaRNA)
    if (cur_tool == 'Consensus') {
        cur_tool = 0;
    } else if (cur_tool == 'IntaRNA') {
        cur_tool = 1;
    } else if (cur_tool == 'RNAhybrid') {
        cur_tool = 0;
    }
    
    // get values from datatable
    var table = $('#result_table').DataTable()
    
    // get column value, index start from 0
    // all column values are raw value before rendering by render function
    // you can get all rows no matter whether filter is activated
    // sorting will change the order of rows you get, but it does not matter
    
    // 4th column: gene ID
    var gene = table.column(3).data()
    // 7th column: free energy
    var mfe = table.column(6).data()
    // 8th column: matching length
    var mcl = table.column(7).data()
    // 9th column: prediction tool
    var tool = table.column(8).data()
    
    // extract ensembl IDs, also not include empty strings (entried without gene ID)
    var len = gene.length
    var obj = []
    for (var i = 0; i < len; i++) {
        // only predictions from needed tool are included
        if (tool[i] == cur_tool && gene[i].length > 0) {
            obj.push({ 'id': gene[i], 'mfe': parseFloat(mfe[i]), 'mcl': parseInt(mcl[i]) })
        }
    }


    // sort gene ids based mfe and mcl
    // +/- to indicate ascending or descending order
    // sort genes with lowest mfe first
    // with ties going to the genes with the highest mcl
    // sorting result checked, it's corrected
    obj.sort(getSortMethod('+mfe', '-mcl'))

    // get needed sorted gene ids
    if (num > obj.length) {
        num = obj.length
    }
    
    var sorted_ids = []
    for (var i = 0; i < num; i++) {
        sorted_ids[i] = obj[i].id
    }
    
    // copy procedure checked, list is completed, and the order is corrected
    copyToClipboard(sorted_ids)
    
    alert('A list of top ' + num + ' Gene Ensemble IDs copied to clipboard. Paste them into the input box in David website and start Gene Enrichment Analysis')
    
    // open a new window
    window.open('http://bioinformatics.sdstate.edu/go/')
} )


// onclick function to do GO analysis by GENE ONTOLOGY
// do not be affected by table filtering, that is, all entries will be included for ranking
// change the re-directing website; use gene symbols instead of IDs; use /n instead of , to separate genes
$('#GENEONTOLOGY').click(function () {
    // number of genes for pathway analysis
    var num = document.getElementById('mrna_num').value

    // prediction tool for current result, get from print message
    var cur_tool = document.getElementById('message').textContent.split(' ')[1];
    // change it to integers (0: RNAhybrid; 1:IntaRNA)
    if (cur_tool == 'Consensus') {
        cur_tool = 0;
    } else if (cur_tool == 'IntaRNA') {
        cur_tool = 1;
    } else if (cur_tool == 'RNAhybrid') {
        cur_tool = 0;
    }
    
    // get values from datatable
    var table = $('#result_table').DataTable()
    
    // get column value, index start from 0
    // all column values are raw value before rendering by render function
    // you can get all rows no matter whether filter is activated
    // sorting will change the order of rows you get, but it does not matter
    
    // 5th column: gene name
    var gene = table.column(4).data()
    // 7th column: free energy
    var mfe = table.column(6).data()
    // 8th column: matching length
    var mcl = table.column(7).data()
    // 9th column: prediction tool
    var tool = table.column(8).data()
    
    // extract gene names, also not include empty strings (entried without gene name)
    var len = gene.length
    var obj = []
    for (var i = 0; i < len; i++) {
        // only predictions from needed tool are included
        if (tool[i] == cur_tool && gene[i].length > 0) {
            obj.push({ 'id': gene[i], 'mfe': parseFloat(mfe[i]), 'mcl': parseInt(mcl[i]) })
        }
    }


    // sort gene ids based mfe and mcl
    // +/- to indicate ascending or descending order
    // sort genes with lowest mfe first
    // with ties going to the genes with the highest mcl
    // sorting result checked, it's corrected
    obj.sort(getSortMethod('+mfe', '-mcl'))

    // get needed sorted gene ids
    if (num > obj.length) {
        num = obj.length
    }
    
    var sorted_ids = []
    for (var i = 0; i < num; i++) {
        sorted_ids[i] = obj[i].id
    }
    
    // copy procedure checked, list is completed, and the order is corrected
    copyToClipboard(sorted_ids.join("\r\n"))
    
    // David can also support both human and mouse 
    alert('A list of top ' + num + ' Gene Names copied to clipboard. Paste them into the input box in GENE ONTOLOGY website and start GO Enrichment Analysis')
    
    // open a new window
    window.open('http://geneontology.org/')    
} )