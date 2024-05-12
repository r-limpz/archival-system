document.addEventListener("DOMContentLoaded", function () {
    const switchRolesBtn = document.getElementById("switch_roles");
    const formTitle = document.getElementById("form-title");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const captchaInput = document.getElementById("captcha");
    const errorMessage = document.getElementById("error_message");
    const userRole = document.getElementById("role");

    switchRolesBtn.addEventListener("click", function () {

        if (switchRolesBtn.innerText === "Sign in as Admin") {
            switchRolesBtn.innerText = "Sign in as Staff";
            usernameInput.classList.remove("is-invalid");
            passwordInput.classList.remove("is-invalid");
            captchaInput.classList.remove("is-invalid");
            errorMessage.textContent = "";
            formTitle.innerText = "Sign in as Admin";
            userRole.value = '1';
        } else {
            switchRolesBtn.innerText = "Sign in as Admin";
            usernameInput.classList.remove("is-invalid");
            passwordInput.classList.remove("is-invalid");
            captchaInput.classList.remove("is-invalid");
            errorMessage.textContent = "";
            formTitle.innerText = "Sign in as Staff";
            userRole.value = '2';
        }
    });

    usernameInput.addEventListener("focus", function () {
        usernameInput.classList.remove("is-invalid");
        errorMessage.textContent = "";
    });

    passwordInput.addEventListener("focus", function () {
        passwordInput.classList.remove("is-invalid");
        errorMessage.textContent = "";
    });

    captchaInput.addEventListener("focus", function () {
        captchaInput.classList.remove("is-invalid");
        errorMessage.textContent = "";
    });

});
