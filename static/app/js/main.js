const sidebarButton = document.getElementById('sidebarButton');
const sidebarMenu = document.getElementById('sidebarMenu');
const main = document.querySelector('main');

$(document).ready(function () {
    if (authenticatedUser) {
        sidebarButton.addEventListener('click', function() {
            if (sidebarMenu.style.display == 'flex') {
                sidebarMenu.style.display = 'none';
            } else {
                sidebarMenu.style.display = 'flex';
            }
        });
    } else {
        main.className ='ms-auto px-md-4 p-4 w-100';
    }
})

var checkingAuth = false;
function checkAuth() {
    if (checkingAuth) {
        return;
    }
    checkingAuth = true;
    $.ajax({
        url: checkAuthUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            if (!data.authenticated) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Sesión Expirada',
                    text: 'Tu sesión ha expirado. Debes iniciar sesión nuevamente.',
                    showCancelButton: false,
                    confirmButtonText: 'OK',
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = loginUrl;
                    }
                });
            } else {
                checkingAuth = false;
            }
        },
        error: function (response) {
            console.log(response);
        },
        statusCode: {
            404: function () {
                console.error('Recurso no encontrado');
            },
            500: function () {
                console.error('Error interno del servidor');
            },
        }
    });
}

if (authenticatedUser) {
    setInterval(checkAuth, 10000);
}

