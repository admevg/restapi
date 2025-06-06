# Generated by Django 5.2.1 on 2025-05-13 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workout',
            name='muscle_group',
        ),
        migrations.CreateModel(
            name='WorkoutMuscleGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intensity', models.PositiveIntegerField(default=3, help_text='1-5 scale')),
                ('muscle_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workouts.musclegroup')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workouts.workout')),
            ],
            options={
                'unique_together': {('workout', 'muscle_group')},
            },
        ),
        migrations.AddField(
            model_name='workout',
            name='muscle_groups',
            field=models.ManyToManyField(through='workouts.WorkoutMuscleGroup', to='workouts.musclegroup'),
        ),
    ]
