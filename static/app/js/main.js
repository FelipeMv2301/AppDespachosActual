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
        main.className ='ms-sm-aut px-md-4 p-4';
    }
})
