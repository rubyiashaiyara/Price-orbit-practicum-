from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from blog.models import Payment
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

@login_required
def download_invoice(request, tran_id):
    payment = get_object_or_404( #------if transaction not found
        Payment,
        transaction_id=tran_id,
        user=request.user,
        status="Success"
    )

    response = HttpResponse(content_type="application/pdf") #
    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{payment.transaction_id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4) # -----------for pdf generate from canva
    width, height = A4

    p.setFont("Helvetica-Bold", 18) #-----------front fixing
    p.drawString(50, height - 50, "PriceFinder nvoice")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Transaction ID: {payment.transaction_id}")
    p.drawString(50, height - 130, f"Customer: {payment.user.username}")
    p.drawString(50, height - 160, f"Product: {payment.product.name}")
    p.drawString(50, height - 190, f"Amount Paid: ৳{payment.amount}")
    p.drawString(50, height - 220, f"Status: {payment.status}")
    p.drawString(
        50,
        height - 250,
        f"Date: {payment.created_at.strftime('%d %B %Y')}"
    )

    p.showPage()
    p.save()

    return response

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
    payments = Payment.objects.filter(user=request.user).order_by("-created_at")
    
    return render(request, "profile.html", {
        "user_obj": request.user,
        "payments": payments,
    })

def logout_view(request):
    logout(request) 
    return redirect('home_page')



