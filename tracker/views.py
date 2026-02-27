from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Meal, WeightLog, UserProfile
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
import uuid

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/landing.html')

def setup_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        # Generate a truly unique username
        username = f"{name.replace(' ', '').lower()}_{uuid.uuid4().hex[:8]}"
        
        # Create a new system user with a unique username
        user = User.objects.create_user(username=username, password='defaultpassword')
        
        # Create the profile
        UserProfile.objects.create(
            user=user,
            name=name,
            age=int(request.POST.get('age')),
            height=float(request.POST.get('height')),
            current_weight=float(request.POST.get('weight')),
            target_goal=request.POST.get('goal')
        )
        
        login(request, user)
        return redirect('dashboard')
    return render(request, 'tracker/setup.html')

@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('setup')

    today = timezone.now().date()
    meals_today = Meal.objects.filter(user=request.user, date_added__date=today).order_by('-date_added')
    
    bmi = profile.calculate_bmi()
    status = profile.get_status()
    
    recommendation = ""
    if bmi < 18.5:
        recommendation = "Underweight: High-Calorie Surplus required. Focus on healthy fats and protein."
    elif bmi < 25:
        recommendation = "Healthy: Maintain with strength training to build lean muscle."
    else:
        recommendation = "Overweight: Slight Calorie Deficit recommended. Focus on high-volume Indian foods like greens."

    totals = meals_today.aggregate(cal=Sum('calories'), prot=Sum('protein'))
    
    context = {
        'profile': profile,
        'bmi': bmi,
        'status': status,
        'recommendation': recommendation,
        'meals': meals_today,
        'totals': {'calories': totals['cal'] or 0, 'protein': totals['prot'] or 0},
        'goals': {'calories': 3000 if bmi < 18.5 else 2200, 'protein': 180},
        'progress': {
            'calories': min(round(((totals['cal'] or 0) / (3000 if bmi < 18.5 else 2200)) * 100), 100),
            'protein': min(round(((totals['prot'] or 0) / 180) * 100), 100),
        }
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def log_meal(request):
    if request.method == 'POST':
        Meal.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            weight=float(request.POST.get('weight')),
            calories=int(request.POST.get('calories')),
            protein=float(request.POST.get('protein', 0)),
            carbs=float(request.POST.get('carbs', 0)),
            fat=float(request.POST.get('fat', 0))
        )
    return redirect('dashboard')

@login_required
def delete_meal(request, meal_id):
    Meal.objects.filter(user=request.user, id=meal_id).delete()
    return redirect('dashboard')

def logout_user(request):
    logout(request)
    return redirect('landing')
