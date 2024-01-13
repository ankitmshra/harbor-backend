# views.py
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

from admin_dashboard.forms.UserLoginForm import UserLoginForm

def loginview(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        try:
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                user = authenticate(request, username=email, password=password)

                if user is not None:
                    login(request, user)
                    if user.is_staff:
                        return redirect('dashboardview')
                    else:
                        messages.error(request, 'Invalid login credentials')
                else:
                    messages.error(request, 'Invalid login credentials')
            else:
                messages.error(request, 'Form validation error. Please check your input.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})