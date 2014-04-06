
  // React when a browser action's icon is clicked.
// chrome.browserAction.onClicked.addListener(function(tab) {
//   console.log("Hey, this works");
// });


var formSubmitButton = $("#form_submit");

formSubmitButton.on("click", function(event){
    event.preventDefault(); // prevent the browser form submission from happening
    $.ajax({
        url: "http://localhost:5000/ajax/new_code",
        method: "POST",
        data: $("form#add_code_form").serialize() + "&user_id=" + "3"
    }).done(function(data){
        alert(data);
    }).fail(function(){
        alert('Fail');
    });

});



// log in on click---nstore in a cookie.
// hardcode user for plugin demo.


// on document load or event-clickeon.
// method - get
// data; user id('')
// empy div where Avaliblae code--- replace the empy dic with the hmtl  with: INNERHTML 