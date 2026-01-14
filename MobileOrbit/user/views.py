from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def register_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(next_url if next_url else 'home_page')
    else:
        form = UserRegistrationForm()

    return render(request, 'singup.html', {'form': form})

# def register_view(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserRegistrationForm()

#     return render(request, 'singup.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = UserLoginForm(request.POST)

#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']

#             user = authenticate(request, username=email, password=password)

#             if user:
#                 login(request, user)
#                 return redirect('home_page')

#             form.add_error(None, 'Invalid email or password')

#     else:
#         form = UserLoginForm()

#     return render(request, 'login.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user:
                login(request, user)
                return redirect(next_url if next_url else 'home_page')

            form.add_error(None, 'Invalid email or password')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {
        'form': form,
        'next': next_url
    })

@login_required
def profile_view(request):
    user = request.user

    return render(request, 'profile.html', {
        'user_obj': user
    })

def logout_view(request):
    logout(request) 
    return redirect('home_page')



