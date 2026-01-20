from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile for Maslow app"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=1)
    avatar = models.CharField(max_length=100, default='default')
    total_goals_completed = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level}"


class Day(models.Model):
    """Represents a day in the user's goal journey"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='days')
    day_number = models.IntegerField()
    date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'day_number']
        ordering = ['-day_number']
    
    def __str__(self):
        return f"Day {self.day_number} - {self.user.username}"
    
    @property
    def completion_percentage(self):
        """Calculate goal completion percentage for this day"""
        goals = self.goals.all()
        if not goals:
            return 0
        completed = goals.filter(completed=True).count()
        return int((completed / goals.count()) * 100)


class Goal(models.Model):
    """Main goal model with AI-enhanced features"""
    GOAL_LEVEL_CHOICES = [
        ('safe', 'Safe Goal'),
        ('growth', 'Growth Goal'),
        ('stretch', 'Stretch Goal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='goals')
    
    # Original input
    original_goal = models.TextField(help_text="User's original goal input")
    
    # The Why Ladder responses
    why_response_1 = models.TextField(blank=True, null=True)
    why_response_2 = models.TextField(blank=True, null=True)
    why_response_3 = models.TextField(blank=True, null=True)
    
    # AI-transformed goal
    transformed_goal = models.TextField(blank=True, null=True, help_text="AI-enhanced powerful goal")
    deep_motivation = models.TextField(blank=True, null=True, help_text="Discovered deep motivation")
    
    # Smart Challenger - target numbers
    baseline_value = models.IntegerField(default=0, help_text="User's current baseline")
    baseline_unit = models.CharField(max_length=50, default='ครั้ง')
    
    safe_target = models.IntegerField(default=0)
    growth_target = models.IntegerField(default=0)
    stretch_target = models.IntegerField(default=0)
    
    selected_target = models.IntegerField(default=0)
    goal_level = models.CharField(max_length=20, choices=GOAL_LEVEL_CHOICES, default='growth')
    
    # Status
    completed = models.BooleanField(default=False)
    progress = models.IntegerField(default=0, help_text="Current progress towards target")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transformed_goal or self.original_goal} ({self.goal_level})"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.selected_target == 0:
            return 0
        return min(int((self.progress / self.selected_target) * 100), 100)


class Achievement(models.Model):
    """User achievements and badges"""
    ACHIEVEMENT_TYPES = [
        ('first_goal', 'First Goal Set'),
        ('streak_3', '3 Day Streak'),
        ('streak_7', '7 Day Streak'),
        ('streak_30', '30 Day Streak'),
        ('goals_10', '10 Goals Completed'),
        ('stretch_complete', 'Stretch Goal Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, default='🏆')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement_type']
    
    def __str__(self):
        return f"{self.icon} {self.title}"


class WhyLadderSession(models.Model):
    """Tracks the Why Ladder conversation flow"""
    goal = models.OneToOneField(Goal, on_delete=models.CASCADE, related_name='why_session')
    current_step = models.IntegerField(default=1)
    ai_question_1 = models.TextField(blank=True, null=True)
    ai_question_2 = models.TextField(blank=True, null=True)
    ai_question_3 = models.TextField(blank=True, null=True)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Why Ladder for: {self.goal.original_goal}"


# ============== Day 2 Features ==============

class MysteryBoxReward(models.Model):
    """Rewards that can be won from mystery box"""
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    REWARD_TYPE_CHOICES = [
        ('points', 'Bonus Points'),
        ('quote', 'Inspirational Quote'),
        ('badge', 'Special Badge'),
        ('theme', 'Theme Unlock'),
        ('avatar', 'Avatar Item'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, default='🎁')
    reward_type = models.CharField(max_length=50, choices=REWARD_TYPE_CHOICES)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    points_value = models.IntegerField(default=0, help_text="Points awarded if reward type is points")
    quote_text = models.TextField(blank=True, null=True, help_text="Quote if reward type is quote")
    drop_rate = models.FloatField(default=0.5, help_text="Probability 0.0-1.0")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['rarity', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name} ({self.get_rarity_display()})"


class UserReward(models.Model):
    """Rewards collected by user from mystery boxes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    reward = models.ForeignKey(MysteryBoxReward, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True, 
                            help_text="Goal that triggered this reward")
    earned_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True, help_text="Not yet viewed by user")
    
    class Meta:
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"


class TemptationBundle(models.Model):
    """User's preferred activities for temptation bundling"""
    ACTIVITY_TYPE_CHOICES = [
        ('podcast', 'ฟัง Podcast'),
        ('music', 'ฟังเพลง'),
        ('series', 'ดูซีรีส์'),
        ('youtube', 'ดู YouTube'),
        ('audiobook', 'ฟัง Audiobook'),
        ('other', 'อื่นๆ'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temptation_bundles')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
    activity_name = models.CharField(max_length=200, help_text="เช่น Podcast ชื่ออะไร")
    activity_url = models.URLField(blank=True, null=True, help_text="Link to content (optional)")
    icon = models.CharField(max_length=100, default='🎧')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.icon} {self.activity_name}"


class FocusSession(models.Model):
    """Timer session for goal with temptation bundling"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='focus_sessions')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='focus_sessions')
    temptation_bundle = models.ForeignKey(TemptationBundle, on_delete=models.SET_NULL, 
                                          null=True, blank=True)
    
    # Timer data
    target_duration = models.IntegerField(help_text="Target duration in minutes")
    elapsed_seconds = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    content_unlocked = models.BooleanField(default=False, help_text="Whether temptation content is accessible")
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Focus: {self.goal.original_goal} ({self.status})"
    
    @property
    def progress_percentage(self):
        """Calculate timer progress"""
        if self.target_duration == 0:
            return 0
        target_seconds = self.target_duration * 60
        return min(int((self.elapsed_seconds / target_seconds) * 100), 100)
    
    @property
    def remaining_seconds(self):
        """Calculate remaining time"""
        target_seconds = self.target_duration * 60
        return max(target_seconds - self.elapsed_seconds, 0)


# ============== Articles/Knowledge ==============

class Article(models.Model):
    """Knowledge articles explaining features"""
    CATEGORY_CHOICES = [
        ('day1', 'Day 1 - Foundation'),
        ('day2', 'Day 2 - Motivation'),
        ('day3', 'Day 3 - Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='day1')
    feature_name = models.CharField(max_length=100, help_text="เช่น Goals Aren't Chores")
    
    # Content
    content_html = models.TextField(help_text="HTML content of article")
    pdf_file = models.FileField(upload_to='articles/', blank=True, null=True)
    
    # Metadata
    icon = models.CharField(max_length=100, default='📖')
    reading_time_minutes = models.IntegerField(default=5)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order']
    
    def __str__(self):
        return f"{self.icon} {self.title}"


class ArticleProgress(models.Model):
    """Track user's reading progress on articles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_progress')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    
    # Progress tracking
    scroll_percentage = models.IntegerField(default=0, help_text="0-100%")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'article']
    
    def __str__(self):
        status = "✅" if self.is_completed else f"{self.scroll_percentage}%"
        return f"{self.user.username} - {self.article.title} ({status})"

