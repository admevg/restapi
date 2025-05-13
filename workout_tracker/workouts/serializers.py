from rest_framework import serializers
from .models import MuscleGroup, Workout, WorkoutMuscleGroup

class MuscleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ['id', 'name']

class WorkoutMuscleGroupSerializer(serializers.ModelSerializer):
    muscle_group_name = serializers.CharField(source='muscle_group.name', read_only=True)
    
    class Meta:
        model = WorkoutMuscleGroup
        fields = ['muscle_group', 'muscle_group_name', 'intensity']

class WorkoutSerializer(serializers.ModelSerializer):
    muscle_groups = WorkoutMuscleGroupSerializer(source='workoutmusclegroup_set', many=True)
    
    class Meta:
        model = Workout
        fields = ['id', 'date_time', 'duration_minutes', 'notes', 'muscle_groups']
    
    def create(self, validated_data):
        muscle_groups_data = validated_data.pop('workoutmusclegroup_set')
        workout = Workout.objects.create(**validated_data)
        
        for mg_data in muscle_groups_data:
            WorkoutMuscleGroup.objects.create(
                workout=workout,
                muscle_group=mg_data['muscle_group'],
                intensity=mg_data.get('intensity', 3)
            )
        
        return workout

class MuscleGroupStatsSerializer(serializers.Serializer):
    muscle_group = serializers.CharField()
    total_workouts = serializers.IntegerField()
    last_workout = serializers.DateTimeField()
    avg_days_between = serializers.FloatField()
    avg_intensity = serializers.FloatField()