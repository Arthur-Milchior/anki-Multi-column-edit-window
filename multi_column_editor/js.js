var columnCount = 1;
singleColspan = columnCount;
singleLine = [];
function setColumnCount(n) {
    columnCount = n;
}
function setSingleLine(field) {
    singleLine.push(field);
}
var ffFix = false; // Frozen Fields fix
function setFFFix(use) {
  ffFix = use;
}
// Event triggered when #fields is modified.
function makeColumns(event) {
    // If the inserted object is not at the top level of the "fields" object,
    // ignore it. We're assuming that anything added to the "fields" table is
    // the entirety of the content of the table itself.
    if ($(event.target).parent()[0].id !== "fields") {
        return;
    }
    // In the original, there is a row for each field's name followed by a row
    // with that field's edit box. I.e.:
    // <tr><td>...Field name...</td></tr>
    // <tr><td>...Edit box...</td></tr>
    // We copy each row into its own group's array and then
    // write out the table again using our own ordering.
    singleLine = []
    pycmd("mceTrigger"); // Inject global variables for us to use from python.
}
// Because of the asynchronous nature of the bridge calls, we split this method
// into two parts, the latter of which is called from python once the variable
// injection has completed.
function makeColumns2() {
    singleColspan = columnCount;
    // Hack to make Frozen Fields look right.
    if (ffFix) {
        // Apply fixed width to first <td>, which is a Frozen Fields cell,
        // or it will take up too much space.
        $("#fields td:first-child").each(function (){
            $(this).attr("width", "28px");
        });
        singleColspan = (columnCount*2)-1;
    }
    
    s = '<style>';
    s += '.mceTable { table-layout: fixed; height: 1%%; width: 100%%;}';
    s += '.mceTable td .field { height: 100%%; }';
    s += '</style>';
    $('html > head').append(s);
    
    var fNames = [];
    var fEdit = [];
    
    // Create our two lists and tag those that need their own row.
    var rows = $('#fields tr');
    for(var i=0; i<rows.length;){
        fldName = $('.fname', rows[i])[0].innerHTML;
        if (singleLine.indexOf(fldName) >= 0) {
            $(rows[i]).addClass("mceSingle");
            $(rows[i+1]).addClass("mceSingle");
        }
        fNames.push(rows[i]);
        fEdit.push(rows[i+1]);
        i += 2;
    }
    txt = "";
    txt += "<tr>";
    // Pre-populate empty cells to influence column size
    for (var i = 0; i < columnCount; i++) {
        if (ffFix) {
            txt += "<td width=28px></td>";
        }
        txt += "<td></td>";
    }
    txt += "</tr>";
    for (var i = 0; i < fNames.length;) {
        // Lookahead for single-line fields
        target = columnCount;
        for (var j = 0; j < target && i+j < fNames.length; j++) {
            nTd = fNames[i+j];
            eTd = fEdit[i+j];
    
            if ($(nTd).hasClass("mceSingle")) {
                $('.fname', nTd).attr("colspan", singleColspan);
                $('td[width^=100]', eTd).attr("colspan", singleColspan); // hacky selector. need a class
                txt += "<tr class='mceRow mceNameRow'>" + nTd.innerHTML + "</tr>";
                txt += "<tr class='mceRow mceEditRow'>" + eTd.innerHTML + "</tr>";
                fNames[i+j] = "skipme";
                fEdit[i+j] = "skipme";
                target++;
            }
        }
        
        nTxt = "<tr class='mceRow mceNameRow'>";
        eTxt = "<tr class='mceRow mceEditRow'>";
        target = columnCount;
        for (var j = 0; j < target && i+j < fNames.length; j++) {
            var nTd = fNames[i+j];
            var eTd = fEdit[i+j];
            if (nTd === "skipme") {
                target++;
                continue;
            }
            nTxt += nTd.innerHTML;
            eTxt += eTd.innerHTML;
        }
        nTxt += "</tr>";
        eTxt += "</tr>";
        i += target;
        txt += nTxt + eTxt;
    }
    
    // Unbind then rebind to avoid infinite loop
    $('#fields').unbind('DOMNodeInserted')
    $("#fields").html("<table class='mceTable'>" + txt + "</table>");
    $('#fields').bind('DOMNodeInserted', makeColumns);
}
// Attach event to restructure the table after it is populated
$('#fields').bind('DOMNodeInserted', makeColumns);
