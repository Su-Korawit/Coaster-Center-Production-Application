from django.contrib import admin
from .models import (
    UserProfile, Day, Goal, Achievement, WhyLadderSession,
    MysteryBoxReward, UserReward, TemptationBundle, FocusSession
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'total_goals_completed', 'current_streak', 'created_at']
    search_fields = ['user__username']


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ['user', 'day_number', 'date', 'is_active', 'is_completed']
    list_filter = ['is_active', 'is_completed', 'date']
    search_fields = ['user__username']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['original_goal', 'user', 'goal_level', 'selected_target', 'completed', 'created_at']
    list_filter = ['goal_level', 'completed', 'created_at']
    search_fields = ['original_goal', 'transformed_goal', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'achievement_type', 'icon', 'unlocked_at']
    list_filter = ['achievement_type', 'unlocked_at']
    search_fields = ['user__username', 'title']


@admin.register(WhyLadderSession)
class WhyLadderSessionAdmin(admin.ModelAdmin):
    list_display = ['goal', 'current_step', 'is_complete', 'created_at']
    list_filter = ['is_complete', 'current_step']


# ============== Day 2 Features ==============

@admin.register(MysteryBoxReward)
class MysteryBoxRewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'reward_type', 'rarity', 'points_value', 'is_active']
    list_filter = ['rarity', 'reward_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'goal', 'earned_at', 'is_new']
    list_filter = ['is_new', 'earned_at']
    search_fields = ['user__username', 'reward__name']


@admin.register(TemptationBundle)
class TemptationBundleAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_name', 'activity_type', 'icon', 'is_active']
    list_filter = ['activity_type', 'is_active']
    search_fields = ['user__username', 'activity_name']


@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal', 'target_duration', 'elapsed_seconds', 'status', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['user__username']
