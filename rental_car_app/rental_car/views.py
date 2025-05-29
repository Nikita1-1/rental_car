from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    return render(request, 'home.html')  # Render the home template


def legal_page(request):
    return render(request, 'partials/legal.html')


def faq_page(request):
    return render(request, 'partials/faq.html')


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Message from {name} <{email}>:\n\n{message}"

        try:
            send_mail(
                subject=f'Contact Form Submission: {subject}',
                message=full_message,
                from_email="hello@demomailtrap.co",  # or your configured sender
                recipient_list=["aspencarcare@yahoo.com"],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully.")
            return redirect('contact')  # redirect to the same page or a thank you page
        except Exception as e:
            messages.error(request, "There was an error sending your message. Please try again.")

    return render(request, 'partials/contact.html')