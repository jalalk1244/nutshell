from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order


@login_required
def profile(request):
    '''View for rendering the profile page'''
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure \
                                    the form is valid.')
    else:
        form = UserProfileForm(instance=profile)

    orders = profile.orders.all()
    context = {
        'form': form,
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user_profile__user=request.user)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'Payment status is shown below.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True
    }

    return render(request, template, context)
