/* Save the validated order before confirming its session-bound PaymentIntent. */
const publicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
const errorDiv = document.getElementById('card-errors');
const form = document.getElementById('payment-form');
const button = document.getElementById('submit-button');
if (!publicKey) {
    errorDiv.textContent = 'Payment is unavailable. Please contact the store.';
    button.disabled = true;
} else {
    const stripe = Stripe(publicKey);
    const card = stripe.elements().create('card');
    card.mount('#card-element');
    card.on('change', event => { errorDiv.textContent = event.error ? event.error.message : ''; });
    form.addEventListener('submit', async event => {
        event.preventDefault();
        button.disabled = true;
        errorDiv.textContent = '';
        try {
            const response = await fetch('/checkout/cache_checkout_data/', {
                method: 'POST', body: new FormData(form), credentials: 'same-origin'
            });
            const data = await response.json();
            if (!response.ok) {
                const fields = data.fields ? Object.entries(data.fields).map(([k,v]) => `${k}: ${v.join(' ')}`).join(' ') : '';
                throw new Error(`${data.error} ${fields}`);
            }
            if (data.client_secret) {
                const result = await stripe.confirmCardPayment(data.client_secret, {
                    payment_method: { card, billing_details: {
                        name: form.full_name.value, email: form.email.value
                    }}
                });
                if (result.error) throw new Error(result.error.message);
            }
            window.location.assign(data.redirect);
        } catch (error) {
            errorDiv.textContent = error.message || 'Payment unavailable. Retry safely.';
            button.disabled = false;
        }
    });
}
