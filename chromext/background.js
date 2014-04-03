
// log in on click---nstore in a cookie.
// hardcode user for plugin demo.
// this must be tested as a plugin- browseraction. must connect it. 
// This means that the url will be shortened
chrome.browserAction.onClicked.addListener(function(event){
    console.log("HOLA");
    event.preventDefault();
    $.ajax({
        data: window.location.href,
        url:"http://localhost:5000/ajax/popup?site="+data,
        method: "GET"
    }).done(function(data){
        alert(data);
        // data is template string
        // put the template string insite your empty div
        $('popup_content').innerHTML(data);
    }).fail(function(){
        alert('Fail');
    });
});





// on document load or event-clickeon.
// method - get
// data; user id('')
// empy div where Avaliblae code--- replace the empy dic with the hmtl  with: INNERHTML 













