//show toast message of the status
function showToast(title, message, className, bordercol) {
    let toastContainer = document.getElementById('toastContainer');

    let toastHTML = `<div class="toast align-items-center opacity-75 border border-bottom-2 ${bordercol}" role="alert" aria-live="assertive" aria-atomic="true" id="add_userToast" >
                                    <div class="d-flex">
                                        <div class="toast-body d-flex">
                                            <span class="fs-large ${className} me-3"> </span> <span class="fw-bold me-2">${title}</span> ${message}
                                        </div>
                                    </div>
                                </div> `;

    toastContainer.innerHTML = toastHTML;
}