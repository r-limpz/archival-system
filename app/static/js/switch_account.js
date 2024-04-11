document.addEventListener("DOMContentLoaded", function () {
    const switchRolesBtn = document.getElementById("switch_roles");
    const formTitle = document.getElementById("form-title");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const errorMessage = document.getElementById("error_message");
    const userRole = document.getElementById("user_role");

    switchRolesBtn.addEventListener("click", function () {

        if (switchRolesBtn.innerText === "Sign in as Admin") {
            switchRolesBtn.innerText = "Sign in as Staff";
            usernameInput.classList.remove("is-invalid");
            passwordInput.classList.remove("is-invalid");
            errorMessage.textContent = "";
            formTitle.innerText = "Sign in as Admin";
            userRole.value = 1;
        } else {
            switchRolesBtn.innerText = "Sign in as Admin";
            usernameInput.classList.remove("is-invalid");
            passwordInput.classList.remove("is-invalid");
            errorMessage.textContent = "";
            formTitle.innerText = "Sign in as Staff";
            userRole.value = 2;
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

});

document.addEventListener("DOMContentLoaded", function() {
    var passwordInput = document.getElementById("password");
    var togglePassword = document.getElementById("toggle-password");

    function toggleDisplayState(){
        if (passwordInput.value !== "") {
            togglePassword.style.display = "inline-block";
        } else {
            togglePassword.style.display = "none";
        }
    }

    passwordInput.addEventListener("input", toggleDisplayState);

    togglePassword.style.display = "none";
    toggleDisplayState();
    
    togglePassword.addEventListener("click", function() {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePassword.innerHTML = '<i class="fa-regular fa-eye-slash"></i>';
        } else {
            passwordInput.type = "password";
            togglePassword.innerHTML = '<i class="fa-regular fa-eye"></i>';
        }
    });
});