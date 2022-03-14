// Displaying the user input field function for editProfile.html 
function displayUsernameInput(e) {
    e.preventDefault();
    var usernameInput = document.getElementById("editUsernameInput");
    if (usernameInput.display == "block") {
        usernameInput.style.display = "none";
    }
    else {
        usernameInput.style.display = "block";
        document.getElementById("editUsernameButton").style.display = "none";
        document.getElementById("saveUsernameButton").style.display = "block";
    }
}

// Saving edited username function for editProfile.html 
function saveUsernameInput(e) {
    e.preventDefault();
    // insert into database
}