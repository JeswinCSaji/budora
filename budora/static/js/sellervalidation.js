$(document).ready(function () {
    $("#st").keyup(function () {
        validateStoreName("#st");
    });

    $("#fn").keyup(function () {
        validateName("#fn");
    });

    $("#mail").keyup(function () {
        validateEmail("#mail");
    });

    $("#contact").keyup(function () {
        validateContact("#contact");
    });

    $("#address").keyup(function () {
        validateAddress("#address");
    });

    $("#pass").keyup(function () {
        validatePassword("#pass");
    });

    $("#cpass").keyup(function () {
        validateConfirmPassword("#cpass");
    });

});
    function validateStoreName(fieldId) {
    var stname = $(fieldId).val();
    lettersWithSpaces = /^[A-Za-z\s]+$/;
    if (stname.trim() === "") {
    $("#stspan").html("Enter your storename").css("color", "red");
    } else if (!lettersWithSpaces.test(stname)) {
    $("#stspan").html("only alphabets are allowed").css("color", "red");
    } else {
    $("#stspan").html("");
    }
    }

   function validateName(fieldId) {
   var name = $(fieldId).val();
   lettersWithSpacesstore = /^[A-Za-z\s]+$/;
   if (name.trim() === "") {
   $("#fnspan").html("Enter your name").css("color", "red");
   } else if (!lettersWithSpacesstore.test(name)) {
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
        $("#pspan").html("Uppercase letter, Symbol and number needed").css("color", "red");

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

   validateContact
   function validateContact(fieldId) {
    var con= $(fieldId).val();
    var filtercon = /^(\d{3})[- ]?(\d{3})[- ]?(\d{4})$/;
    if (con === "") {
    $("#cnspan").html("Enter your Mobile Number").css("color", "red");
    } else if (!filtercon.test(con)) {
    $("#cnspan").html("Incorrect Mobile Number").css("color", "red");
    } else {
    $("#cnspan").html("");
    }
    }

    function validateAddress(fieldId) {
     var con= $(fieldId).val();
     if (con === "") {
     $("#adspan").html("Enter your address").css("color", "red");
     } 
     }