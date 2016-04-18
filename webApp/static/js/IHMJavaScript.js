
$(document).ready(function () {
    toggleFields(); //call this first so we start out with the correct visibility depending on the selected form values
    //this will call our toggleFields function every time the selection value of our underAge field changes
    $("#id_activateLocation").change(function () {
        toggleFields();
    });

});
//this toggles the visibility of our parent permission fields depending on the current selected value of the underAge field
function toggleFields() {
    if ($("#id_activateLocation").is(':checked')){
    	        $("#location").show();
    			$("#rowofraduis").show();
    }

    else{
    	$("#location").hide();
    	$("#rowofraduis").hide();
    }
        
}
function deleteSearch(){
    var buttonId=event.target.id;
    searchId='#search'.concat(buttonId.substr(12));
    console.log(searchId)
    $(searchId).remove();
}
function deleteTweet(){
    var buttonId=event.target.id;
    tweetId='#tweet'.concat(buttonId.substr(10));
    console.log(tweetId)
    $(tweetId).remove();
}