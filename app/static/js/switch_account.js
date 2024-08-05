document.addEventListener("DOMContentLoaded", function () {
    const switchRolesBtn = document.getElementById("switch_roles");
    const formTitle = document.getElementById("form-title");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const captchaImage = document.getElementById("captcha-image");
    const captchaInput = document.getElementById("captcha");
    const errorMessage = document.getElementById("error_message");
    const userRole = document.getElementById("role");

    function clearErrorMessageIfValid() {
        if (!usernameInput.classList.contains("is-invalid") &&
            !passwordInput.classList.contains("is-invalid") &&
            !captchaInput.classList.contains("is-invalid") &&
            captchaInput.value.length === 6) {
            errorMessage.innerText = "";
        }
    }

    switchRolesBtn.addEventListener("click", function () {

        if (switchRolesBtn.innerText === "Sign in as Admin") {
            switchRolesBtn.innerText = "Sign in as Staff";
            usernameInput.classList.remove("is-invalid");
            passwordInput.classList.remove("is-invalid");
            errorMessage.innerText = "";
            formTitle.innerText = "Sign in as Admin";
            userRole.value = '1';
        } else {
            switchRolesBtn.innerText = "Sign in as Admin";
            usernameInput.classList.remove("is-invalid");
            passwordInput.classList.remove("is-invalid");
            errorMessage.innerText = "";
            formTitle.innerText = "Sign in as Staff";
            userRole.value = '2';
        }
    });

    usernameInput.addEventListener("focus", function () {
        usernameInput.classList.remove("is-invalid");
        clearErrorMessageIfValid();
    });

    passwordInput.addEventListener("focus", function () {
        passwordInput.classList.remove("is-invalid");
        clearErrorMessageIfValid();
    });

    captchaInput.addEventListener("keyup", function () {
        if (captchaInput.value.length === 6) {
            captchaInput.classList.remove("is-invalid");
            captchaImage.classList.remove("is-invalid");
            clearErrorMessageIfValid();
        }
    });

});
