from django.urls import path
from . import views

urlpatterns = [
    # Home and Day views
    path('', views.home, name='home'),
    path('day/<int:day_id>/', views.day_view, name='day_view'),
    
    # Goal creation flow
    path('goal/create/', views.goal_create, name='goal_create'),
    path('goal/why/<int:step>/', views.goal_why, name='goal_why'),
    path('goal/transform/', views.goal_transform, name='goal_transform'),
    path('goal/baseline/', views.goal_baseline, name='goal_baseline'),
    path('goal/select-level/', views.goal_select_level, name='goal_select_level'),
    path('goal/save/', views.goal_save, name='goal_save'),
    path('goal/<int:goal_id>/summary/', views.goal_summary, name='goal_summary'),
    
    # Goal actions
    path('goal/<int:goal_id>/complete/', views.goal_complete, name='goal_complete'),
    path('goal/<int:goal_id>/progress/', views.update_progress, name='update_progress'),
    
    # User
    path('register/', views.register, name='register'),
    path('achievements/', views.achievements, name='achievements'),
    
    # ============== Day 2 Features ==============
    
    # Mystery Box
    path('goal/<int:goal_id>/mystery-box/', views.open_mystery_box, name='open_mystery_box'),
    path('rewards/', views.my_rewards, name='my_rewards'),
    
    # Temptation Bundler
    path('temptation/add/', views.add_temptation, name='add_temptation'),
    path('temptation/', views.manage_temptations, name='manage_temptations'),
    path('temptation/<int:bundle_id>/delete/', views.delete_temptation, name='delete_temptation'),
    
    # Focus Session
    path('goal/<int:goal_id>/focus/', views.start_focus, name='start_focus'),
    path('focus/<int:session_id>/', views.focus_timer, name='focus_timer'),
    path('focus/<int:session_id>/update/', views.update_timer, name='update_timer'),
    path('focus/<int:session_id>/end/', views.end_focus, name='end_focus'),
    path('focus/<int:session_id>/pause/', views.pause_focus, name='pause_focus'),
]
