// This function is called as soon as the popup opens and
// it searches for the codes available to the user related 
// to the website she is browsing on
chrome.tabs.query(
    {
        currentWindow: true,    // currently focused window
        active: true            // selected tab
    },
    function (foundTabs) {
        if (foundTabs.length > 0) {
            var site = foundTabs[0].url;
				$.ajax({
					url:"http://localhost:5000/ajax/popup?site="+site,
					method: "GET"
				}).done(function(data){
					$('#popup_content').html(data);
			});
        }
    }
);


// Here we take the info from the form and 
// submit it on click to add a new code:
var formSubmitButton = $("#form_submit");
	
formSubmitButton.on("click", function(event){
	event.preventDefault(); // prevent the browser form submission from happening
	$.ajax({
	url: "http://localhost:5000/ajax/new_code",
	method: "POST",
	data: $("form#add_code_form").serialize()
	}).done(function(data){	
		$(this).window("open");
		window.alert("A code was added to your wallet");
		console.log("A code was added to your wallet");
	}).fail(function(){
		window.alert('Something went wrong; please, try again.');
		console.log("Something went wrong; please, try again.");
	});
});


// This function allows for the href for the code on the popup to 
// open a tab to the Referraly website with the code info. 
var codeLink = $("#code_link");

$(document).ready(function(){
codeLink.on('click', function(){
    chrome.tabs.create({url: $(this).attr("href")});
     return false;
   });
});


//This function makes it so that when cliking on the title,
//it takes the user to the main webpage.

var buttonMain = $("#button_main");

$(document).ready(function(){
buttonMain.on('click', function(){
    chrome.tabs.create({url: $(this).attr("href")});
     return false;
   });
});

//This function closes the popup when the 'Close' button is clicked.

var closeButton = $("#close_popup");

$(document).ready(function(){
closeButton.on('click', function(){
    window.close();
    return false;
   });
});






