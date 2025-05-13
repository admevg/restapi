from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from workouts import views

router = DefaultRouter()
router.register(r'muscle-groups', views.MuscleGroupViewSet)
router.register(r'workouts', views.WorkoutViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/workouts/regularity/', views.WorkoutViewSet.as_view({'get': 'regularity'}), name='workout-regularity'),
]