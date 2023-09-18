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

function validateName(fieldId) {
    var name = $(fieldId).val();
    var lettersWithSpaces = /^[A-Za-z\s]+$/;
    if (name.trim() === "") {
        $("#fnspan").html("Enter your name").css("color", "red");
    } else if (!lettersWithSpaces.test(name)) {
        $("#fnspan").html("Only alphabets are allowed").css("color", "red");
    } else {
        $("#fnspan").html("");
    }
}
function validateStoreName(fieldId) {
    var storename = $(fieldId).val();
    var lettersWithSpaces = /^[A-Za-z\s]+$/;
    if (storename.trim() === "") {
        $("#stspan").html("Enter your store name").css("color", "red");
    } else if (!lettersWithSpaces.test(storename)) {
        $("#stspan").html("Only alphabets are allowed").css("color", "red");
    } else {
        $("#stspan").html("");
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
    var pwd_expression = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;

    if (password === "") {
        $("#pspan").html("Enter your password").css("color", "red");
    } else if (!pwd_expression.test(password)) {
        $("#pspan").html("Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one digit, and one special character").css("color", "red");
    } else {
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

function validateContact(fieldId) {
    var con = $(fieldId).val();
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
    var con = $(fieldId).val();
    if (con === "") {
        $("#adspan").html("Enter your address").css("color", "red");
    } else {
        $("#adspan").html("");
    }
}
