
const loginButton = document.getElementById("login_btn"); 

loginButton.addEventListener('click', login);


function login(){
    firebase.auth().createUserWithEmailAndPassword("snehkoul@gmail.com", "pancakes").then(() =>
    console.log("Awesome")).catch(function(error) {
        // Handle Errors here.
        var errorCode = error.code;
        var errorMessage = error.message;
        // ...
      });
}