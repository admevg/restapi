from django.db import models
from django.utils import timezone

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Workout(models.Model):
    date_time = models.DateTimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    muscle_groups = models.ManyToManyField(MuscleGroup, through='WorkoutMuscleGroup')
    
    def __str__(self):
        return f"{self.date_time} - {self.muscle_groups.count()} groups"

class WorkoutMuscleGroup(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE)
    intensity = models.PositiveIntegerField(default=3, help_text="1-5 scale")

    class Meta:
        unique_together = ('workout', 'muscle_group')