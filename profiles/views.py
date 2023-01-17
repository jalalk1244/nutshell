from django.shortcuts import render, get_object_or_404

from .models import UserProfile
from .forms import UserProfileForm


def profile(request):
    '''View for rendering the profile page'''
    profile = get_object_or_404(UserProfile, user=request.user)

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    context = {
        'form': form,
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'profiles/profile.html', context)