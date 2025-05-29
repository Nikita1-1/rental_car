from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from user_auths.models import User, Profile
from user_auths.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from user_auths.decorator import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
import mimetypes
from django.contrib.auth.decorators import user_passes_test
from django.utils.encoding import filepath_to_uri
from django.core.mail import send_mail


def RegisterUser(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey {request.user.username}, you are already logged in")
        return redirect('car_main:home')   

    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True  # Ensure the user is active
            user.save()

            full_name = form.cleaned_data.get('full_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            drivers_license = form.cleaned_data.get('drivers_license')
            try:
                profile = user.profile
                profile.full_name = full_name
                profile.drivers_license = drivers_license
                profile.save()
            except Profile.DoesNotExist:
                Profile.objects.create(
                    user=user,
                    full_name=full_name,
                    drivers_license=drivers_license
                )

            print(f"Trying to authenticate with username: {username}, password: {password}")
            user = authenticate(request, email=email, password=password)
            print(f"Authenticated user: {user}")

            if user:
                login(request, user)
                messages.success(request, f"Hi {profile.full_name}, your account has been created successfully.")
                email_send = send_mail(
                    subject = "New User Created",
                    message = f"Hi, admin! New user {profile.full_name} has been created successfully. Please confirm confirm their profile in admin dashboard.", 
                    from_email = "hello@demomailtrap.co",
                    recipient_list = ["aspencarcare@yahoo.com"]
                )
                if email_send:
                    print("Email to admin sent successfully.")
                return redirect('car_main:home')
            else:
                messages.error(request, "There was a problem logging you in.")
        else:
            print("Form errors:", form.errors)
    else:
        form = UserRegisterForm()

    return render(request, 'user_auths/sign-up.html', {'form': form})

def LoginUser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user_auths = authenticate(request, email=email, password=password)

            if user_auths is not None:
                login(request, user_auths)
                messages.success(request, "You are Logged In")
                # After successful login, redirect to the next URL or homepage
                next_url = request.GET.get('next', 'car_main:home')  # Default to 'car_main:index' if 'next' isn't in GET
                return redirect(next_url)
            else:
                messages.error(request, 'Username or password is incorrect.')

        except User.DoesNotExist:
            messages.error(request, 'User does not exist')

    return render(request, "user_auths/sign-in.html")  # 

def LogoutUser(request):
    logout(request)
    return redirect('user_auths:sign-in')  



@user_passes_test(lambda u: u.is_superuser)  # or other permission check
def secure_file(request, path):
    secure_path = os.path.join(settings.SECURE_FILE_PATH, path)
    
    if not os.path.isfile(secure_path):
        raise Http404("File not found.")

    response = FileResponse(open(secure_path, 'rb'))
    return response