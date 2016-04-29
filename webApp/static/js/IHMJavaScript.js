$(window).load(function() {
    $(".loader").fadeOut("slow");
})
$(document).ready(function () {
    toggleFields(); //call this first so we start out with the correct visibility depending on the selected form values
    //this will call our toggleFields function every time the selection value of our underAge field changes
    $("#id_activateLocation").change(function () {
        toggleFields();
    });
//Handling the legende display
    $( "#legende" ).hide();
    $( ".fieldKeywords" ).focusin(function() {
       $( "#legende" ).toggle( "drop" );

    });
    $( ".fieldKeywords" ).focusout(function() {
      $( "#legende" ).toggle( "drop" );
    });
});
//this toggles the visibility of our parent permission fields depending on the current selected value of the underAge field
function toggleFields() {
    if ($("#id_activateLocation").is(':checked')){
    	        $("#location").show('slow');
    			$("#rowofraduis").show('slow');
    }

    else{
    	$("#location").hide('slow');
    	$("#rowofraduis").hide('slow');
    }       
}
function deleteSearch(url, crsfToken){
    var buttonId=event.target.id;
    PK=buttonId.substr(13)
    searchId='#search_'.concat(PK);
    $(searchId).fadeOut(500, function(){ $(this).remove();});
    $.ajax({
        url: url,
        method: "POST",
        headers: {'X-CSRFToken': crsfToken},
        data: {searchPK:PK},
        dataType: "json"
    });
}
function deleteTweet(url, crsfToken){
    var buttonId=event.target.id;
    tweetID=buttonId.substr(11)
    tweetId='#tweet_'.concat(tweetID); 
    $(tweetId).fadeOut(500, function(){ $(this).remove();});
    $.ajax({
        url: url,
        method: "POST",
        headers: {'X-CSRFToken': crsfToken},
        data: {tweet:tweetID},
        dataType: "json"
    });
}
