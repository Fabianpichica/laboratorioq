from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('/')
    return render(request, 'adminlab/dashboard_admin.html', {})
