$(document).ready(function () {
    $("#fn").keyup(function () {
        validateName("#fn");
    });

    $("#mail").keyup(function () {
        validateEmail("#mail");
    });

    $("#pass").keyup(function () {
        validatePassword("#pass");
    });

    $("#cpass").keyup(function () {
        validateConfirmPassword("#cpass");
    });
});
   
   function validateName(fieldId) {
   var name = $(fieldId).val();
   lettersWithSpaces = /^[A-Za-z\s]+$/;
   if (name.trim() === "") {
   $("#fnspan").html("Enter your name").css("color", "red");
   } else if (!lettersWithSpaces.test(name)) {
   $("#fnspan").html("only alphabets are allowed").css("color", "red");
   } else {
   $("#fnspan").html("");
   }
   }
   
   function validateEmail(fieldId) {
   var email = $(fieldId).val();
   var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
   if (email === "") {
   $("#emspan").html("Enter your Email Id").css("color", "red");
   } else if (!filter.test(email)) {
   $("#emspan").html("Incorrect Email Id").css("color", "red");
   } else {
   $("#emspan").html("");
   }
   }
   
   function validatePassword(fieldId) {
   var password = $(fieldId).val();
   var pwd_expression = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])/;
    if (password === "") {
   $("#pspan").html("Enter your password").css("color", "red");
   }
   else if(!pwd_expression.test(password))
    {
        $("#pspan").html("Use correct Password Format").css("color", "red");

    }
    else {
   $("#pspan").html("");
   }
   }
   
   function validateConfirmPassword(fieldId) {
    var password = $("#pass").val();
   var confirmPassword = $(fieldId).val();
    if (confirmPassword === "") {
   $("#cpspan").html("Enter the password").css("color", "red");
   } else if (confirmPassword !== password) {
   $("#cpspan").html("Passwords do not match").css("color", "red");
   } else {
   $("#cpspan").html("");
   }
   }