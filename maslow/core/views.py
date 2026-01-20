from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
import random

from .models import (
    UserProfile, Day, Goal, Achievement, WhyLadderSession,
    MysteryBoxReward, UserReward, TemptationBundle, FocusSession,
    Article, ArticleProgress
)
from .forms import GoalInitialForm, WhyLadderForm, BaselineForm, GoalLevelForm, ProgressForm
from .ai_services import maslow_ai


def home(request):
    """Home page - Day view with swipeable navigation"""
    if not request.user.is_authenticated:
        return render(request, 'landing.html')
    
    user = request.user
    today = timezone.now().date()
    
    # Get user's day count (determines which day they're on)
    day_count = Day.objects.filter(user=user).count()
    if day_count == 0:
        day_count = 1
    
    # Get or create current day
    current_day, created = Day.objects.get_or_create(
        user=user,
        date=today,
        defaults={'day_number': day_count}
    )
    
    # Get goals
    goals = Goal.objects.filter(user=user)
    
    # Feature completion status
    feature_1_done = goals.filter(transformed_goal__isnull=False).exists()
    feature_2_done = goals.filter(selected_target__gt=0).exists()
    feature_3_done = UserReward.objects.filter(user=user).exists()
    feature_4_done = TemptationBundle.objects.filter(user=user).exists()
    
    # Determine current day number (1 or 2 based on progress)
    current_day_number = request.GET.get('day', None)
    if current_day_number:
        current_day_number = int(current_day_number)
    else:
        # Default to latest unlocked day
        current_day_number = min(day_count, 2)
    
    context = {
        'current_day': current_day,
        'current_day_number': current_day_number,
        'goals': goals,
        'feature_1_done': feature_1_done,
        'feature_2_done': feature_2_done,
        'feature_3_done': feature_3_done,
        'feature_4_done': feature_4_done,
    }
    return render(request, 'home.html', context)


def day_view(request, day_id):
    """View specific day"""
    if not request.user.is_authenticated:
        return redirect('home')
    
    day = get_object_or_404(Day, id=day_id, user=request.user)
    goals = Goal.objects.filter(day=day)
    days = Day.objects.filter(user=request.user).order_by('-day_number')[:7]
    
    context = {
        'current_day': day,
        'days': days,
        'goals': goals,
    }
    return render(request, 'home.html', context)


@login_required
def goal_create(request):
    """Step 1: Enter initial goal"""
    if request.method == 'POST':
        form = GoalInitialForm(request.POST)
        if form.is_valid():
            # Store in session
            request.session['goal_data'] = {
                'original_goal': form.cleaned_data['original_goal'],
                'why_answers': []
            }
            return redirect('goal_why', step=1)
    else:
        form = GoalInitialForm()
    
    return render(request, 'goal/create.html', {'form': form})


@login_required
def goal_why(request, step):
    """The Why Ladder - Steps 1-3"""
    goal_data = request.session.get('goal_data', {})
    
    if not goal_data:
        return redirect('goal_create')
    
    original_goal = goal_data.get('original_goal', '')
    why_answers = goal_data.get('why_answers', [])
    
    # Generate AI question
    if step == 1:
        ai_question = maslow_ai.ask_why(original_goal)
    else:
        ai_question = maslow_ai.ask_why(original_goal, why_answers)
    
    if request.method == 'POST':
        form = WhyLadderForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            why_answers.append(answer)
            goal_data['why_answers'] = why_answers
            request.session['goal_data'] = goal_data
            
            if step >= 2:
                # Enough answers, transform the goal
                return redirect('goal_transform')
            else:
                return redirect('goal_why', step=step + 1)
    else:
        form = WhyLadderForm()
    
    context = {
        'form': form,
        'step': step,
        'total_steps': 2,
        'original_goal': original_goal,
        'ai_question': ai_question,
        'previous_answers': why_answers,
    }
    return render(request, 'goal/why_ladder.html', context)


@login_required
def goal_transform(request):
    """Transform goal and show result"""
    goal_data = request.session.get('goal_data', {})
    
    if not goal_data:
        return redirect('goal_create')
    
    original_goal = goal_data.get('original_goal', '')
    why_answers = goal_data.get('why_answers', [])
    
    # Transform goal using AI
    transformed = maslow_ai.transform_goal(original_goal, why_answers)
    
    goal_data['transformed_goal'] = transformed.get('transformed_goal', original_goal)
    goal_data['deep_motivation'] = transformed.get('deep_motivation', '')
    request.session['goal_data'] = goal_data
    
    context = {
        'original_goal': original_goal,
        'transformed_goal': goal_data['transformed_goal'],
        'deep_motivation': goal_data['deep_motivation'],
        'why_answers': why_answers,
    }
    return render(request, 'goal/transform.html', context)


@login_required
def goal_baseline(request):
    """Smart Challenger - Enter baseline"""
    goal_data = request.session.get('goal_data', {})
    
    if not goal_data:
        return redirect('goal_create')
    
    if request.method == 'POST':
        form = BaselineForm(request.POST)
        if form.is_valid():
            baseline = form.cleaned_data['baseline_value']
            unit = form.cleaned_data['baseline_unit']
            
            # Get AI suggestions
            targets = maslow_ai.suggest_targets(
                goal_data.get('original_goal', ''),
                baseline,
                unit
            )
            
            goal_data['baseline_value'] = baseline
            goal_data['baseline_unit'] = unit
            goal_data['safe_target'] = targets['safe']
            goal_data['growth_target'] = targets['growth']
            goal_data['stretch_target'] = targets['stretch']
            request.session['goal_data'] = goal_data
            
            return redirect('goal_select_level')
    else:
        form = BaselineForm()
    
    context = {
        'form': form,
        'transformed_goal': goal_data.get('transformed_goal', ''),
    }
    return render(request, 'goal/baseline.html', context)


@login_required
def goal_select_level(request):
    """Smart Challenger - Select goal level"""
    goal_data = request.session.get('goal_data', {})
    
    if not goal_data or 'safe_target' not in goal_data:
        return redirect('goal_baseline')
    
    if request.method == 'POST':
        selected_level = request.POST.get('goal_level', 'growth')
        
        # Get the selected target
        if selected_level == 'safe':
            selected_target = goal_data['safe_target']
        elif selected_level == 'stretch':
            selected_target = goal_data['stretch_target']
        else:
            selected_target = goal_data['growth_target']
        
        goal_data['goal_level'] = selected_level
        goal_data['selected_target'] = selected_target
        request.session['goal_data'] = goal_data
        
        return redirect('goal_save')
    
    context = {
        'transformed_goal': goal_data.get('transformed_goal', ''),
        'baseline_value': goal_data.get('baseline_value', 0),
        'baseline_unit': goal_data.get('baseline_unit', ''),
        'safe_target': goal_data.get('safe_target', 0),
        'growth_target': goal_data.get('growth_target', 0),
        'stretch_target': goal_data.get('stretch_target', 0),
    }
    return render(request, 'goal/select_level.html', context)


@login_required
def goal_save(request):
    """Save the goal to database"""
    goal_data = request.session.get('goal_data', {})
    
    if not goal_data:
        return redirect('goal_create')
    
    user = request.user
    today = timezone.now().date()
    
    # Get or create today's day
    day_count = Day.objects.filter(user=user).count()
    current_day, _ = Day.objects.get_or_create(
        user=user,
        date=today,
        defaults={'day_number': day_count + 1}
    )
    
    # Create the goal
    goal = Goal.objects.create(
        user=user,
        day=current_day,
        original_goal=goal_data.get('original_goal', ''),
        transformed_goal=goal_data.get('transformed_goal', ''),
        deep_motivation=goal_data.get('deep_motivation', ''),
        why_response_1=goal_data.get('why_answers', [''])[0] if goal_data.get('why_answers') else '',
        why_response_2=goal_data.get('why_answers', ['', ''])[1] if len(goal_data.get('why_answers', [])) > 1 else '',
        baseline_value=goal_data.get('baseline_value', 0),
        baseline_unit=goal_data.get('baseline_unit', ''),
        safe_target=goal_data.get('safe_target', 0),
        growth_target=goal_data.get('growth_target', 0),
        stretch_target=goal_data.get('stretch_target', 0),
        selected_target=goal_data.get('selected_target', 0),
        goal_level=goal_data.get('goal_level', 'growth'),
    )
    
    # Check for first goal achievement
    if Goal.objects.filter(user=user).count() == 1:
        Achievement.objects.get_or_create(
            user=user,
            achievement_type='first_goal',
            defaults={
                'title': 'ก้าวแรก!',
                'description': 'ตั้งเป้าหมายแรกสำเร็จ',
                'icon': '🎯'
            }
        )
    
    # Clear session
    if 'goal_data' in request.session:
        del request.session['goal_data']
    
    messages.success(request, '🎉 ตั้งเป้าหมายสำเร็จ!')
    return redirect('goal_summary', goal_id=goal.id)


@login_required
def goal_summary(request, goal_id):
    """Show goal summary"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    context = {
        'goal': goal,
    }
    return render(request, 'goal/summary.html', context)


@login_required
@require_POST
def goal_complete(request, goal_id):
    """Mark goal as complete"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.completed = True
    goal.progress = goal.selected_target
    goal.save()
    
    # Update user stats
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.total_goals_completed += 1
    profile.save()
    
    messages.success(request, '🎉 ยอดเยี่ยม! ทำสำเร็จแล้ว!')
    return redirect('home')


@login_required
@require_POST
def update_progress(request, goal_id):
    """Update goal progress via AJAX"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        progress = int(data.get('progress', 0))
        goal.progress = progress
        
        if progress >= goal.selected_target:
            goal.completed = True
        
        goal.save()
        
        return JsonResponse({
            'success': True,
            'progress': goal.progress,
            'percentage': goal.progress_percentage,
            'completed': goal.completed
        })
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile
            UserProfile.objects.create(user=user)
            # Login the user
            login(request, user)
            messages.success(request, 'ยินดีต้อนรับสู่ Maslow!')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def achievements(request):
    """View user achievements"""
    if not request.user.is_authenticated:
        return redirect('home')
    
    user_achievements = Achievement.objects.filter(user=request.user)
    
    # All possible achievements
    all_achievements = [
        {'type': 'first_goal', 'title': 'ก้าวแรก!', 'icon': '🎯', 'desc': 'ตั้งเป้าหมายแรกสำเร็จ'},
        {'type': 'streak_3', 'title': 'Streak 3 วัน', 'icon': '🔥', 'desc': 'ทำเป้าหมายต่อเนื่อง 3 วัน'},
        {'type': 'streak_7', 'title': 'Streak 7 วัน', 'icon': '⭐', 'desc': 'ทำเป้าหมายต่อเนื่อง 7 วัน'},
        {'type': 'goals_10', 'title': 'Master 10', 'icon': '🏆', 'desc': 'ทำเป้าหมายสำเร็จ 10 ครั้ง'},
        {'type': 'stretch_complete', 'title': 'ท้าทายตัวเอง', 'icon': '💪', 'desc': 'ทำ Stretch Goal สำเร็จ'},
    ]
    
    unlocked_types = set(a.achievement_type for a in user_achievements)
    
    for ach in all_achievements:
        ach['unlocked'] = ach['type'] in unlocked_types
    
    context = {
        'achievements': all_achievements,
        'unlocked_count': len(unlocked_types),
        'total_count': len(all_achievements),
    }
    return render(request, 'achievements.html', context)


# ============== Day 2 Features ==============

@login_required
def open_mystery_box(request, goal_id):
    """Open mystery box after completing a goal - random reward"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user, completed=True)
    
    # Check if already opened for this goal
    existing_reward = UserReward.objects.filter(user=request.user, goal=goal).first()
    if existing_reward:
        return render(request, 'rewards/mystery_box_result.html', {
            'reward': existing_reward.reward,
            'already_opened': True,
            'goal': goal
        })
    
    # Get available rewards weighted by drop rate
    available_rewards = list(MysteryBoxReward.objects.filter(is_active=True))
    
    if not available_rewards:
        # Create default rewards if none exist
        create_default_rewards()
        available_rewards = list(MysteryBoxReward.objects.filter(is_active=True))
    
    # Weighted random selection based on rarity
    rarity_weights = {
        'common': 0.5,
        'rare': 0.3,
        'epic': 0.15,
        'legendary': 0.05
    }
    
    # Filter by rarity chance first
    rarity_roll = random.random()
    if rarity_roll < 0.05:
        target_rarity = 'legendary'
    elif rarity_roll < 0.20:
        target_rarity = 'epic'
    elif rarity_roll < 0.50:
        target_rarity = 'rare'
    else:
        target_rarity = 'common'
    
    # Get rewards of target rarity, or fallback to any
    rarity_rewards = [r for r in available_rewards if r.rarity == target_rarity]
    if not rarity_rewards:
        rarity_rewards = available_rewards
    
    # Random select from rarity pool
    selected_reward = random.choice(rarity_rewards)
    
    # Create user reward
    user_reward = UserReward.objects.create(
        user=request.user,
        reward=selected_reward,
        goal=goal
    )
    
    # If points reward, add to user profile
    if selected_reward.reward_type == 'points':
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        # Store points in level (simplified)
        profile.level += selected_reward.points_value // 100
        profile.save()
    
    return render(request, 'rewards/mystery_box_result.html', {
        'reward': selected_reward,
        'already_opened': False,
        'goal': goal,
        'is_new': True
    })


def create_default_rewards():
    """Create default mystery box rewards"""
    default_rewards = [
        # Common rewards
        {'name': 'แต้มโบนัส 10', 'icon': '⭐', 'type': 'points', 'rarity': 'common', 'points': 10,
         'desc': 'ได้รับแต้มโบนัส 10 แต้ม'},
        {'name': 'แต้มโบนัส 25', 'icon': '✨', 'type': 'points', 'rarity': 'common', 'points': 25,
         'desc': 'ได้รับแต้มโบนัส 25 แต้ม'},
        {'name': 'Quote: ความพยายาม', 'icon': '💬', 'type': 'quote', 'rarity': 'common',
         'desc': 'คำคมให้กำลังใจ', 'quote': 'ความสำเร็จไม่ได้มาจากโชค แต่มาจากความพยายาม'},
        {'name': 'Quote: ก้าวแรก', 'icon': '💬', 'type': 'quote', 'rarity': 'common',
         'desc': 'คำคมให้กำลังใจ', 'quote': 'การเดินทางพันไมล์เริ่มต้นจากก้าวแรก'},
        # Rare rewards
        {'name': 'แต้มโบนัส 50', 'icon': '💎', 'type': 'points', 'rarity': 'rare', 'points': 50,
         'desc': 'ได้รับแต้มโบนัส 50 แต้ม'},
        {'name': 'Badge: นักสู้', 'icon': '🥊', 'type': 'badge', 'rarity': 'rare',
         'desc': 'ปลดล็อค Badge นักสู้'},
        {'name': 'Quote: ไม่ยอมแพ้', 'icon': '🔥', 'type': 'quote', 'rarity': 'rare',
         'desc': 'คำคมพิเศษ', 'quote': 'คนที่ไม่เคยล้มเหลว คือคนที่ไม่เคยลองทำอะไรใหม่'},
        # Epic rewards
        {'name': 'แต้มโบนัส 100', 'icon': '👑', 'type': 'points', 'rarity': 'epic', 'points': 100,
         'desc': 'ได้รับแต้มโบนัส 100 แต้ม'},
        {'name': 'Badge: ผู้พิชิต', 'icon': '🏆', 'type': 'badge', 'rarity': 'epic',
         'desc': 'ปลดล็อค Badge ผู้พิชิต'},
        # Legendary rewards
        {'name': 'แต้มโบนัส 500', 'icon': '🌟', 'type': 'points', 'rarity': 'legendary', 'points': 500,
         'desc': 'ได้รับแต้มโบนัสมหาศาล 500 แต้ม!'},
        {'name': 'Badge: ตำนาน', 'icon': '🦄', 'type': 'badge', 'rarity': 'legendary',
         'desc': 'ปลดล็อค Badge ตำนาน - หายากมาก!'},
    ]
    
    for r in default_rewards:
        MysteryBoxReward.objects.get_or_create(
            name=r['name'],
            defaults={
                'description': r['desc'],
                'icon': r['icon'],
                'reward_type': r['type'],
                'rarity': r['rarity'],
                'points_value': r.get('points', 0),
                'quote_text': r.get('quote', ''),
            }
        )


@login_required
def my_rewards(request):
    """View all collected rewards"""
    rewards = UserReward.objects.filter(user=request.user).select_related('reward')
    
    # Mark as viewed
    rewards.filter(is_new=True).update(is_new=False)
    
    # Group by rarity
    rewards_by_rarity = {
        'legendary': [],
        'epic': [],
        'rare': [],
        'common': [],
    }
    
    for r in rewards:
        rewards_by_rarity[r.reward.rarity].append(r)
    
    context = {
        'rewards': rewards,
        'rewards_by_rarity': rewards_by_rarity,
        'total_count': rewards.count(),
    }
    return render(request, 'rewards/my_rewards.html', context)


# ============== Temptation Bundler ==============

@login_required
def add_temptation(request):
    """Add a new temptation bundle activity"""
    if request.method == 'POST':
        activity_type = request.POST.get('activity_type', 'other')
        activity_name = request.POST.get('activity_name', '')
        activity_url = request.POST.get('activity_url', '')
        
        icon_map = {
            'podcast': '🎙️',
            'music': '🎵',
            'series': '📺',
            'youtube': '▶️',
            'audiobook': '📚',
            'other': '🎯',
        }
        
        TemptationBundle.objects.create(
            user=request.user,
            activity_type=activity_type,
            activity_name=activity_name,
            activity_url=activity_url if activity_url else None,
            icon=icon_map.get(activity_type, '🎯')
        )
        
        messages.success(request, f'✅ เพิ่ม "{activity_name}" สำเร็จ!')
        return redirect('manage_temptations')
    
    activity_types = TemptationBundle.ACTIVITY_TYPE_CHOICES
    return render(request, 'temptation/add.html', {'activity_types': activity_types})


@login_required
def manage_temptations(request):
    """Manage temptation bundle activities"""
    bundles = TemptationBundle.objects.filter(user=request.user, is_active=True)
    
    context = {
        'bundles': bundles,
    }
    return render(request, 'temptation/manage.html', context)


@login_required
def delete_temptation(request, bundle_id):
    """Delete a temptation bundle"""
    bundle = get_object_or_404(TemptationBundle, id=bundle_id, user=request.user)
    bundle.is_active = False
    bundle.save()
    messages.success(request, 'ลบสำเร็จ!')
    return redirect('manage_temptations')


@login_required
def start_focus(request, goal_id):
    """Start a focus session with temptation bundling"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user, completed=False)
    bundles = TemptationBundle.objects.filter(user=request.user, is_active=True)
    
    # Check for active session
    active_session = FocusSession.objects.filter(
        user=request.user,
        status='active'
    ).first()
    
    if active_session:
        return redirect('focus_timer', session_id=active_session.id)
    
    if request.method == 'POST':
        bundle_id = request.POST.get('bundle_id')
        duration = int(request.POST.get('duration', goal.selected_target))
        
        bundle = None
        if bundle_id:
            bundle = get_object_or_404(TemptationBundle, id=bundle_id, user=request.user)
        
        session = FocusSession.objects.create(
            user=request.user,
            goal=goal,
            temptation_bundle=bundle,
            target_duration=duration,
            content_unlocked=True if bundle else False,
        )
        
        return redirect('focus_timer', session_id=session.id)
    
    context = {
        'goal': goal,
        'bundles': bundles,
        'suggested_duration': goal.selected_target,
    }
    return render(request, 'temptation/start_focus.html', context)


@login_required
def focus_timer(request, session_id):
    """Focus timer page with temptation content"""
    session = get_object_or_404(FocusSession, id=session_id, user=request.user)
    
    context = {
        'session': session,
        'goal': session.goal,
        'bundle': session.temptation_bundle,
        'target_seconds': session.target_duration * 60,
        'elapsed_seconds': session.elapsed_seconds,
    }
    return render(request, 'temptation/timer.html', context)


@login_required
@require_POST
def update_timer(request, session_id):
    """Update timer elapsed time via AJAX"""
    session = get_object_or_404(FocusSession, id=session_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        elapsed = int(data.get('elapsed_seconds', 0))
        session.elapsed_seconds = elapsed
        session.save()
        
        return JsonResponse({
            'success': True,
            'elapsed': session.elapsed_seconds,
            'remaining': session.remaining_seconds,
            'percentage': session.progress_percentage,
        })
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False}, status=400)


@login_required
@require_POST
def end_focus(request, session_id):
    """End focus session"""
    session = get_object_or_404(FocusSession, id=session_id, user=request.user)
    
    data = json.loads(request.body) if request.body else {}
    completed = data.get('completed', False)
    
    session.status = 'completed' if completed else 'abandoned'
    session.ended_at = timezone.now()
    session.content_unlocked = False  # Lock content again
    session.save()
    
    # If completed, update goal progress
    if completed:
        goal = session.goal
        goal.progress += session.target_duration
        if goal.progress >= goal.selected_target:
            goal.completed = True
        goal.save()
    
    return JsonResponse({
        'success': True,
        'status': session.status,
        'goal_id': session.goal.id
    })


@login_required
@require_POST  
def pause_focus(request, session_id):
    """Pause/resume focus session - locks content when paused"""
    session = get_object_or_404(FocusSession, id=session_id, user=request.user)
    
    if session.status == 'active':
        session.status = 'paused'
        session.content_unlocked = False  # Lock content!
    else:
        session.status = 'active'
        session.content_unlocked = True if session.temptation_bundle else False
    
    session.save()
    
    return JsonResponse({
        'success': True,
        'status': session.status,
        'content_unlocked': session.content_unlocked
    })

