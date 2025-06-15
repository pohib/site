from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from users.models import Profile
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile, TelegramData
import hashlib
import hmac
import time
from django.conf import settings
import logger

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


def telegram_login(request):
    if request.user.is_authenticated:
        return redirect('users:profile')
        
    if request.method == 'GET' and 'hash' in request.GET:
        try:
            auth_data = {
                'id': request.GET.get('id'),
                'first_name': request.GET.get('first_name', ''),
                'last_name': request.GET.get('last_name', ''),
                'username': request.GET.get('username'),
                'photo_url': request.GET.get('photo_url'),
                'auth_date': request.GET.get('auth_date'),
                'hash': request.GET.get('hash')
            }

            if not validate_telegram_data(auth_data):
                return redirect('login')

            try:
                telegram_data = TelegramData.objects.get(telegram_id=auth_data['id'])
                user = telegram_data.user
            except TelegramData.DoesNotExist:
                username = auth_data.get('username') or f"tg_{auth_data['id']}"
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{auth_data['id']}"
                
                user = User.objects.create_user(
                    username=username,
                    first_name=auth_data['first_name'],
                    last_name=auth_data['last_name'],
                    email=f"{username}@telegram.user",
                    password=None
                )
                
                TelegramData.objects.create(
                    user=user,
                    telegram_id=auth_data['id'],
                    username=auth_data.get('username'),
                    photo_url=auth_data.get('photo_url'),
                    auth_date=time.strftime('%Y-%m-%d %H:%M:%S', 
                                          time.localtime(int(auth_data['auth_date']))))
                
                Profile.objects.get_or_create(user=user)

            login(request, user)
            return redirect('users:profile')
            
        except Exception as e:
            logger.error(f"Telegram login error: {str(e)}")
            return redirect('login')
        
    return redirect('login')


def validate_telegram_data(auth_data):
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        data_check_string = '\n'.join(f"{key}={auth_data[key]}" for key in sorted(auth_data) if key != 'hash')
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return auth_data['hash'] == computed_hash
    except:
        return False