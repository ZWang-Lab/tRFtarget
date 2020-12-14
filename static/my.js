/*
External script will behave as if it was located exactly where the <script> tag is located.
External scripts cannot contain <script> tags
Cached JavaScript files can speed up page loads
Jinja template can not be support in this file, so url_for can not be used, instead use the website address directly
Variables declared within a JavaScript function, become LOCAL to the function
A variable declared outside a function, becomes GLOBAL
With JavaScript, the global scope is the complete JavaScript environment
In HTML, the global scope is the window object. All global variables belong to the window object
You can use window.XXXXXX to access them
*/


// list variable for autocomplete
var gene_list = []
var transcript_list = []


// change tRF selection form source based on organism
function changeTRF() {
    var e = document.getElementById('search_organism')
    var organism = e.options[e.selectedIndex].value
    if (organism == 'human') {
        var lst = '/static/json/human_trfs.json'
    }
    else if (organism == 'mouse') {
        var lst = '/static/json/mouse_trfs.json'
    }
    else if (organism == 'drosophila') {
        var lst = '/static/json/drosophila_trfs.json'
    }
    else if (organism == 'c.elegans') {
        var lst = '/static/json/elegans_trfs.json'
    }
    else if (organism == 's.pombe') {
        var lst = '/static/json/pombe_trfs.json'
    }
    else if (organism == 'r.sphaeroides') {
        var lst = '/static/json/sphaeroides_trfs.json'
    }
    else if (organism == 'Xenopus-tropicalis') {
        var lst = '/static/json/xenopus_trfs.json'
    }
    else if (organism == 'Zebra_fish_Zv9') {
        var lst = '/static/json/zebrafish_trfs.json'
    }
    
    $.ajax( {
        url: lst,
        type: 'GET',
        dataType: 'json',
        success: function (json) {
            // get the current selected option
            var t = document.getElementById('trf')
            var trf = t.options[t.selectedIndex].value
            
            // delete previous options
            $('#trf').empty()
            $.each(json, function(i, value) {
                $('#trf').append($('<option>').text(value).attr('value', value))
            } )
                  
            // set selected option, it will only take effect in the success fucntion
            // because the ajax call is asynchronous, the values are not populated yet
            if ($(`#trf option[value=${trf}]`).length != 0) {
                // Template literals for inserting variable name
                // option exists
                // otherwises the first option will be selected
                document.getElementById('trf').value = trf
            }
        }
    } )
}


// change autocomplete source based on organism
function changeList() {
    var e = document.getElementById('search_organism')
    var organism = e.options[e.selectedIndex].value
    if (organism == 'human') {
        var gene_src = '/static/json/human_genes.json'
        var transcript_src = '/static/json/human_transcripts.json'
    }
    else if (organism == 'mouse') {
        var gene_src = '/static/json/mouse_genes.json'
        var transcript_src = '/static/json/mouse_transcripts.json'
    }
    else if (organism == 'drosophila') {
        var gene_src = '/static/json/drosophila_genes.json'
        var transcript_src = '/static/json/drosophila_transcripts.json'
    }
    else if (organism == 'c.elegans') {
        var gene_src = '/static/json/elegans_genes.json'
        var transcript_src = '/static/json/elegans_transcripts.json'
    }
    else if (organism == 's.pombe') {
        var gene_src = '/static/json/pombe_genes.json'
        var transcript_src = '/static/json/pombe_transcripts.json'
    }
    else if (organism == 'r.sphaeroides') {
        var gene_src = '/static/json/sphaeroides_genes.json'
        var transcript_src = '/static/json/sphaeroides_transcripts.json'
    }
    else if (organism == 'Xenopus-tropicalis') {
        var gene_src = '/static/json/xenopus_genes.json'
        var transcript_src = '/static/json/xenopus_transcripts.json'
    }
    else if (organism == 'Zebra_fish_Zv9') {
        var gene_src = '/static/json/zebrafish_genes.json'
        var transcript_src = '/static/json/zebrafish_transcripts.json'
    }
    // define ajax functions to load json data
    // NOTE: This function must return the value from calling the $.ajax() method
    function ajax1() {
        return $.ajax( {
            url: gene_src,
            type: 'GET',
            dataType: 'json',
            success: function (json) {
                gene_list = json
            }
        } )
    }
    
    function ajax2() {
        return $.ajax( {
            url: transcript_src,
            type: 'GET',
            dataType: 'json',
            success: function (json) {
                transcript_list = json
            }
        } )
    }
    
    // activate autocomplete here when ajax function finished
    $.when(ajax1(), ajax2()).done(function () {
        autocomplete(document.getElementById("gene"), gene_list)
        autocomplete(document.getElementById("transcript"), transcript_list)
    } )
}


// change disable status based on search way
function changeDisable() {
    if ($('input[name=search_type]:checked').val() == 'trf') {
        $('#trf').prop('disabled', false)
        $('#gene').prop('disabled', true)
        $('#transcript').prop('disabled', true)
    }
    else if ($('input[name=search_type]:checked').val() == 'gene') {
        $('#trf').prop('disabled', true)
        $('#gene').prop('disabled', false)
        $('#transcript').prop('disabled', true)
    }
    else if ($('input[name=search_type]:checked').val() == 'transcript') {
        $('#trf').prop('disabled', true)
        $('#gene').prop('disabled', true)
        $('#transcript').prop('disabled', false)
    }
}


// run these functions during window loading
if (window.addEventListener) { // Mozilla, Netscape, Firefox
    window.addEventListener('load', changeTRF, false)
    window.addEventListener('load', changeDisable, false)
    window.addEventListener('load', changeList, false)
} else if (window.attachEvent) { // IE
    window.attachEvent('onload', changeTRF)
    window.attachEvent('onload', changeDisable)
    window.attachEvent('onload', changeList)
}


// This custom autocomplete function is fast than the intergrated JQuery autocomplete
// https://www.w3schools.com/howto/howto_js_autocomplete.asp
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var y = document.getElementById(this.id + "autocomplete-list");
      if (y) var x = y.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
        /*y.scrollTop=0;
        y.scrollTop=$('.autocomplete-active').offset().top-y.height);*/
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        // e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }
  }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}


// Many js functions defined here
$(document).ready(function() {
    // Change default setting of filters according to the selected prediction tools
    $('input[name=search_table]').change(function() {
        if (this.value == 'RNAhybrid') {
            $('#mfe_threshold').val('-25')
            $('#len_threshold').val('8')
        }
        else if (this.value == 'IntaRNA') {
            $('#mfe_threshold').val('-10')
            $('#len_threshold').val('8')
        }
        else if (this.value == 'Consensus') {
            $('#mfe_threshold').val('-10')
            $('#len_threshold').val('8')
        }
    } );
    
    
    // when the selected searching ways changes
    $('input[name=search_type]').change(function() {
        changeDisable()
    } );
    
    // when the selected organism changes
    $('#search_organism').change(function() {
          changeTRF()
          changeList()
    } )
    
} );


// For data table in search page
$(document).ready(function() {
    $('#table_id').DataTable( {
        columnDefs: [
          {
              className: "dt-body-center",
              targets: [0,1,2,3,4,5,6,8,9]  // except for the demo column
          },
          {
              className: "dt-head-center",
              targets: [0,1,2,3,4,5,6,7,8,9]
          },
          // hidden columns for downloading
          {
              targets: [10,11,12,13],
              visible: false,
              searchable: false
          },
        ],
        dom:  "<'row'<'col-md-3'i><'col-md-5'p><'col-md-3'f><'col-md-1'B>>" +
          "<'row'<'col-md-12'tr>>",
        buttons: [
          {
              extend: 'csv',
              text: 'Export',
              exportOptions: { // keep newline
                  stripNewlines: false,
                  trim: false,
                  columns: [0,10,11,12,13,3,4,5,6,7,8,9]
              }   
          }
        ],
        processing: true
    } );
} );

// For data table in evidence page
$(document).ready(function() {
    $('#table_id2').DataTable( {
        columnDefs: [
          {
              className: "dt-body-center",
              targets: [0,1,2,3,4,5,6]
          },
          {
              className: "dt-head-center",
              targets: [0,1,2,3,4,5,6]
          },
          // hidden columns for downloading
          {
              targets: [7,8,9,10],
              visible: false,
              searchable: false
          },
        ],
        dom:  "<'row'<'col-md-3'i><'col-md-5'p><'col-md-3'f><'col-md-1'B>>" +
          "<'row'<'col-md-12'tr>>",
        buttons: [
          {
              extend: 'csv',
              text: 'Export',
              exportOptions: { // keep newline
                  stripNewlines: false,
                  trim: false,
                  columns: [0,1,7,8,9,10,4,5,6]
              }   
          }
        ]
    } );
} );

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
    var dummy = document.createElement("textarea")
    // to avoid breaking orgain page when copying more words
    // cant copy when adding below this code
    // dummy.style.display = 'none'
    document.body.appendChild(dummy)
    //Be careful if you use texarea. setAttribute('value', value), which works with "input" does not work with "textarea". – Eduard
    dummy.value = texts
    dummy.select()
    document.execCommand("copy")
    document.body.removeChild(dummy)
}


// onclick function to do pathway analysis
// do not be affected by table filtering, that is, all entries will be included for ranking
$('#pathway').click(function () {
    // number of genes for pathway analysis
    var num = document.getElementById('mrna_num').value

    // prediction tool
    var cur_tool = $('input[name=search_table]:checked').val()
    if (cur_tool == 'Consensus') {cur_tool='IntaRNA'}
    
    // get values from datatable
    var table = $('#table_id').DataTable()
    
    // get column value, index start from 0
    // you can get all rows no matter whether filter is activated
    // sorting will change the order of rows you get, but it does not matter
    
    // 3rd column: gene with href link, need parse
    // update: hidden column 12 gene ID; 13 gene symbol
    var gene = table.column(12).data()
    // 5th column: free energy
    var mfe = table.column(4).data()
    // 7th column: matching length
    var mcl = table.column(6).data()
    // 4th column: prediction tool
    var tool = table.column(3).data()
    
    // extract ensembl ID from links
    var len = gene.length
    // var pattern = />([a-zA-Z0-9_.]*?)<br/
    var obj = []
    for (var i = 0; i < len; i++) {
        // the first element will include the '>' and '<br'
        // ensemble ID is the 2nd element
        // only predictions from needed tool are included
        if (tool[i] == cur_tool) {
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
    var num = document.getElementById('mrna_num').value

    // prediction tool
    var cur_tool = $('input[name=search_table]:checked').val()
    if (cur_tool == 'Consensus') {cur_tool='IntaRNA'}
    
    // get values from datatable
    var table = $('#table_id').DataTable()
    
    // get column value, index start from 0
    // you can get all rows no matter whether filter is activated
    // sorting will change the order of rows you get, but it does not matter
    
    // 3rd column: gene with href link, need parse
    // update: hidden column 12 gene ID; 13 gene symbol
    var gene = table.column(12).data()
    // 5th column: free energy
    var mfe = table.column(4).data()
    // 7th column: matching length
    var mcl = table.column(6).data()
    // 4th column: prediction tool
    var tool = table.column(3).data()
    
    // extract ensembl ID from links
    var len = gene.length
    // var pattern = />([a-zA-Z0-9_.]*?)<br/
    var obj = []
    for (var i = 0; i < len; i++) {
        // the first element will include the '>' and '<br'
        // ensemble ID is the 2nd element
        // only predictions from needed tool are included
        if (tool[i] == cur_tool) {
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
    alert('A list of top ' + num + ' Gene Ensemble IDs copied to clipboard. Paste them into the input box in ShinyGO website and start GO Enrichment Analysis')
    
    // open a new window
    window.open('http://bioinformatics.sdstate.edu/go/')    
} )


// onclick function to do GO analysis by GENE ONTOLOGY
// do not be affected by table filtering, that is, all entries will be included for ranking
// change the re-directing website; use gene symbols instead of IDs; use /n instead of , to separate genes
$('#GENEONTOLOGY').click(function () {
    // number of genes for pathway analysis
    var num = document.getElementById('mrna_num').value

    // prediction tool
    var cur_tool = $('input[name=search_table]:checked').val()
    if (cur_tool == 'Consensus') {cur_tool='IntaRNA'}
    
    // get values from datatable
    var table = $('#table_id').DataTable()
    
    // get column value, index start from 0
    // you can get all rows no matter whether filter is activated
    // sorting will change the order of rows you get, but it does not matter
    
    // 3rd column: gene with href link, need parse
    // update: hidden column 12 gene ID; 13 gene symbol
    var gene = table.column(13).data()
    // 5th column: free energy
    var mfe = table.column(4).data()
    // 7th column: matching length
    var mcl = table.column(6).data()
    // 4th column: prediction tool
    var tool = table.column(3).data()
    
    // extract ensembl ID from links
    var len = gene.length
    // var pattern = />([a-zA-Z0-9_.]*?)<br/
    var obj = []
    for (var i = 0; i < len; i++) {
        // the first element will include the '>' and '<br'
        // ensemble ID is the 2nd element
        // only predictions from needed tool are included
        if (tool[i] == cur_tool) {
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
    alert('A list of top ' + num + ' Gene Symbols copied to clipboard. Paste them into the input box in GENE ONTOLOGY website and start GO Enrichment Analysis')
    
    // open a new window
    window.open('http://geneontology.org/')    
} )
