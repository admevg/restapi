from django.db.models import Count, Max, Min, Avg, Prefetch
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters

from .models import MuscleGroup, Workout, WorkoutMuscleGroup
from .serializers import (
    MuscleGroupSerializer,
    WorkoutSerializer,
    MuscleGroupStatsSerializer
)

class MuscleGroupViewSet(viewsets.ModelViewSet):
    queryset = MuscleGroup.objects.all()
    serializer_class = MuscleGroupSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name']

class WorkoutFilter(filters.FilterSet):
    muscle_group = filters.NumberFilter(field_name='workoutmusclegroup__muscle_group')
    date_from = filters.DateFilter(field_name='date_time', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date_time', lookup_expr='lte')

    class Meta:
        model = Workout
        fields = ['muscle_group', 'date_from', 'date_to']

class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all().order_by('-date_time')
    serializer_class = WorkoutSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = WorkoutFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        muscle_group_id = self.request.query_params.get('muscle_group')
        
        if muscle_group_id:
            queryset = queryset.filter(
                workoutmusclegroup__muscle_group=muscle_group_id
            ).prefetch_related(
                Prefetch('workoutmusclegroup_set',
                       queryset=WorkoutMuscleGroup.objects.filter(
                           muscle_group=muscle_group_id
                       ))
            ).distinct()
        else:
            queryset = queryset.prefetch_related('workoutmusclegroup_set')
            
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = []
        
        muscle_groups = MuscleGroup.objects.annotate(
            total_workouts=Count('workoutmusclegroup'),
            last_workout=Max('workoutmusclegroup__workout__date_time'),
            avg_intensity=Avg('workoutmusclegroup__intensity')
        ).filter(total_workouts__gt=0)
        
        for mg in muscle_groups:
            workouts = Workout.objects.filter(
                workoutmusclegroup__muscle_group=mg
            ).order_by('date_time')
            
            total_days = 0
            prev_date = None
            
            for workout in workouts:
                if prev_date:
                    total_days += (workout.date_time - prev_date).days
                prev_date = workout.date_time
            
            avg_days = total_days / (workouts.count() - 1) if workouts.count() > 1 else 0
            
            stats.append({
                'muscle_group': mg.name,
                'total_workouts': mg.total_workouts,
                'last_workout': mg.last_workout,
                'avg_days_between': avg_days,
                'avg_intensity': mg.avg_intensity
            })
        
        serializer = MuscleGroupStatsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-muscle-group/(?P<muscle_group_id>\d+)')
    def by_muscle_group(self, request, muscle_group_id=None):
        try:
            muscle_group = MuscleGroup.objects.get(id=muscle_group_id)
        except MuscleGroup.DoesNotExist:
            return Response(
                {"error": "Muscle group not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        workouts = self.get_queryset().filter(
            workoutmusclegroup__muscle_group=muscle_group
        ).prefetch_related(
            Prefetch('workoutmusclegroup_set',
                   queryset=WorkoutMuscleGroup.objects.filter(
                       muscle_group=muscle_group
                   ))
        ).distinct()
        
        page = self.paginate_queryset(workouts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(workouts, many=True)
        return Response(serializer.data)