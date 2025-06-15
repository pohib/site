from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from users.models import Profile
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile, TelegramUser
import hashlib
import hmac

from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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
    if not request.GET.get('hash'):
        logger.error("Telegram login: Missing hash in request")
        return redirect('login')
    
    auth_data = request.GET.dict()
    logger.info(f"[TELEGRAM DATA] GET: {auth_data}")

    
    if not validate_telegram_data(auth_data):
        logger.error("Telegram login: Validation failed")
        return redirect('login')

    telegram_id = auth_data['id']
    
    try:
        telegram_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        
        if telegram_user:
            user = telegram_user.user
            logger.info(f"Existing user logged in: {user.username}")
        else:
            username = generate_unique_username(auth_data)
            user = User.objects.create_user(
                username=username,
                first_name=auth_data.get('first_name', ''),
                last_name=auth_data.get('last_name', '')
            )
            logger.info(f"New user created: {username}")

            TelegramUser.objects.create(
                user=user,
                telegram_id=telegram_id,
                username=auth_data.get('username'),
                first_name=auth_data.get('first_name'),
                last_name=auth_data.get('last_name'),
                photo_url=auth_data.get('photo_url')
            )
            
        profile, created = Profile.objects.get_or_create(user=user)
        if created:
            logger.info(f"Profile created for Telegram user {user.username}")
        
        login(request, user)
        return redirect('users:profile')
        
    except Exception as e:
        logger.error(f"Telegram login error: {str(e)}", exc_info=True)
        return redirect('login')

def validate_telegram_data(auth_data):
    try:
        required_fields = ['id', 'first_name', 'auth_date', 'hash']
        for field in required_fields:
            if field not in auth_data:
                logger.error(f"Missing required field: {field}")
                return False

        bot_token = settings.TELEGRAM_BOT_TOKEN
        data_check_string = '\n'.join(
            f"{key}={auth_data[key]}" 
            for key in sorted(auth_data.keys()) 
            if key != 'hash'
        )
        
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        computed_hash = hmac.new(
            secret_key, 
            data_check_string.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return auth_data['hash'] == computed_hash
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return False

def generate_unique_username(auth_data):
    base_username = auth_data.get('username', f"tg_{auth_data['id']}")
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1
    
    return username