// Native controls keep the storefront usable without a framework runtime.
document.querySelectorAll('.dismiss-message').forEach(button => {
    button.addEventListener('click', () => button.closest('.alert').remove());
});
document.querySelectorAll('.header-actions details').forEach(menu => {
    menu.addEventListener('toggle', () => {
        if (menu.open) document.querySelectorAll('.header-actions details').forEach(other => {
            if (other !== menu) other.open = false;
        });
    });
});
document.addEventListener('keydown', event => {
    if (event.key === 'Escape') document.querySelectorAll('.header-actions details[open]').forEach(menu => {
        menu.open = false;
        menu.querySelector('summary').focus();
    });
});

// Dismiss header disclosures when clicking elsewhere or returning to desktop.
document.addEventListener('click', event => {
    document.querySelectorAll('.header-actions details[open]').forEach(menu => {
        if (!menu.contains(event.target)) menu.open = false;
    });
});
const desktopNavigation = window.matchMedia('(min-width: 801px)');
desktopNavigation.addEventListener('change', event => {
    if (event.matches) document.querySelectorAll('.mobile-menu[open]').forEach(menu => {
        menu.open = false;
    });
});
