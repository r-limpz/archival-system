//show toast message of the status
function showToast(title, message, theme) {
    let container_theme = "";
    let font_color = "";
    let icon = "";

    switch (theme) {
        case 'success':
            container_theme = "bg-success-subtle";
            font_color = "text-success";
            icon = "fa-solid fa-circle-check";
            break;
        case 'warning':
            container_theme = "bg-warning-subtle";
            font_color = "text-warning";
            icon = "fa-solid fa-triangle-exclamation";
            break;
        case 'error':
            container_theme = "bg-danger";
            font_color = "text-danger";
            icon = "fa-solid fa-circle-xmark";
            break;
    }

    let toastContainer = document.getElementById('toastContainer');
    let toastHTML = `<div class="toast align-items-center ${container_theme}" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="10000" id="add_userToast" style="min-width:400px"> 
                        <div class="d-flex p-3 gap-2 align-items-center">
                            <div class="toast-body p-0 flex-grow-1 d-flex justify-content-start gap-3">
                                <span class="fs-def pt-1 ${font_color} ${icon}"></span>
                                <div class="">
                                    <div class="fs-def fw-bold ${font_color}"> ${title} </div>
                                    <div class="fs-small"> ${message}</div>
                                </div>
                            </div>
                            <button type="button" class="no-border-button fs-medium fs-small bg-transparent p-0" data-bs-dismiss="toast" aria-label="Close"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                    </div>`;

    toastContainer.innerHTML = toastHTML;
}

