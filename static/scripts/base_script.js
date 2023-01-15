
// Auto hide the message alerts
window.setTimeout(() => {
$('.alert').fadeTo(500, 0).slideUp(() => {
    $(this).remove();
})
}, 5000);
