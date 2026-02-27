from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    height = models.FloatField()  # in cm
    current_weight = models.FloatField()  # in kg
    target_goal = models.CharField(max_length=20, choices=[
        ('gain', 'Weight Gain'),
        ('lose', 'Fat Loss'),
        ('maintain', 'Maintain')
    ], default='gain')

    def calculate_bmi(self):
        height_m = self.height / 100
        return round(self.current_weight / (height_m * height_m), 1)

    def get_status(self):
        bmi = self.calculate_bmi()
        if bmi < 18.5: return "Underweight"
        if bmi < 25: return "Healthy"
        if bmi < 30: return "Overweight"
        return "Obese"

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    weight = models.FloatField()
    calories = models.IntegerField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    date_added = models.DateTimeField(default=timezone.now)

class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date_added = models.DateTimeField(default=timezone.now)
