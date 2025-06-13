from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from users.models import Profile

@login_required
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    return render(request, 'users/profile/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            if 'avatar-clear' in request.POST:
                request.user.profile.avatar.delete(save=False)
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'users/profile/profile_edit.html', {'form': form})