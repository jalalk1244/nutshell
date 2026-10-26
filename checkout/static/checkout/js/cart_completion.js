/* Sync the browser cart after the server has verified payment through a webhook.
 * GET pages remain read-only: all session changes use a CSRF-protected POST.
 */
(() => {
    window.addEventListener('pageshow', event => {
        if (event.persisted) window.location.reload();
    });
    const form = document.getElementById('checkout-cart-sync');
    if (!form) return;
    const marker = document.querySelector('[data-payment-status]');
    const confirmation = marker && marker.dataset.checkoutKey === form.dataset.checkoutKey ? marker : null;
    const deadline = Date.now() + 60000;
    let timer;

    const retry = () => {
        if (confirmation && Date.now() < deadline) timer = setTimeout(sync, 1500);
    };
    const sync = async () => {
        try {
            const response = await fetch(form.action, {
                method: 'POST', body: new FormData(form), credentials: 'same-origin'
            });
            if (!response.ok) return;
            const result = await response.json();
            if (result.cleared || (confirmation && result.status !== 'none' &&
                    result.status !== confirmation.dataset.paymentStatus)) {
                window.location.reload();
                return;
            }
            if (result.status === 'pending') retry();
        } catch {
            // A temporary connection error must never discard the customer's bag.
            retry();
        }
    };
    window.addEventListener('pagehide', () => clearTimeout(timer));
    sync();
})();
