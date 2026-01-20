# Maslow - Goal Setting Web Application

> AI-powered goal setting app ที่ช่วยให้คุณตั้งเป้าหมายอย่างมีพลัง

## 🚀 Quick Start

```bash
# 1. Clone project
cd maslow

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (optional)
python manage.py createsuperuser

# 7. Run server
python manage.py runserver 0.0.0.0:8000
```

**Access:**
- **Web:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/

---

## 📁 Project Structure

```
maslow/
├── core/                   # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── forms.py           # Form classes
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   ├── ai_services.py     # AI/Gemini integration
│   └── migrations/        # Database migrations
│
├── maslow/                 # Django project settings
│   ├── settings.py        # Project settings
│   └── urls.py            # Root URL config
│
├── templates/              # HTML Templates
│   ├── base.html          # Base template
│   ├── home.html          # Main home with Day navigation
│   ├── landing.html       # Landing page
│   ├── goal/              # Goal creation flow
│   ├── rewards/           # Mystery Box feature
│   ├── temptation/        # Temptation Bundler feature
│   ├── articles/          # Knowledge articles
│   └── registration/      # Login/Register
│
├── static/
│   ├── css/style.css      # Main stylesheet
│   └── js/app.js          # JavaScript
│
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

---

## 🎯 Features by Day

| Day | Feature Name | Thai Name | File Location |
|-----|-------------|-----------|---------------|
| **Day 1** | Goals Aren't Chores | เป้าหมายต้องไม่ใช่งานบ้าน | `templates/goal/` |
| **Day 1** | Put a Number on It | ใส่ตัวเลขกำหนดทิศทาง | `templates/goal/baseline.html`, `select_level.html` |
| **Day 2** | Incentives Matter | แรงจูงใจภายนอก | `templates/rewards/` |
| **Day 2** | Intrinsic Motivation | แรงจูงใจในและความสุข | `templates/temptation/` |

---

## 👥 Developer Guide

### การเพิ่ม Day ใหม่ (เช่น Day 3)

#### Step 1: วางแผน Features
```
Day 3 Features:
- Feature 5: [ชื่อ Feature]
- Feature 6: [ชื่อ Feature]
```

#### Step 2: สร้าง Models (ถ้าจำเป็น)
```python
# core/models.py
class NewFeatureModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... fields
```

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 3: สร้าง Views
```python
# core/views.py
@login_required
def new_feature_view(request):
    # ... logic
    return render(request, 'new_feature/template.html', context)
```

#### Step 4: เพิ่ม URLs
```python
# core/urls.py
path('new-feature/', views.new_feature_view, name='new_feature'),
```

#### Step 5: สร้าง Templates
```bash
mkdir templates/new_feature
# สร้างไฟล์ HTML
```

#### Step 6: อัพเดท home.html
เพิ่ม Day 3 page ใน `swipe-container`:
```html
<!-- Day 3 Page -->
<div class="swipe-page" id="day3Page">
    <div class="day-header">
        <div class="day-title">Day: 3</div>
    </div>
    <div class="feature-list">
        <!-- Feature cards -->
    </div>
</div>
```

#### Step 7: อัพเดท Day Dots
```html
<div class="day-dots">
    <div class="day-dot"></div>
    <div class="day-dot"></div>
    <div class="day-dot"></div>  <!-- Day 3 -->
</div>
```

---

### การแก้ไข Feature ที่มีอยู่

#### 📝 ไฟล์ที่ต้องแก้ตาม Feature:

| Feature | Models | Views | Templates | Forms |
|---------|--------|-------|-----------|-------|
| Goals Aren't Chores | `Goal`, `WhyLadderSession` | `goal_create`, `goal_why`, `goal_transform` | `goal/*.html` | `GoalInitialForm`, `WhyLadderForm` |
| Put a Number on It | `Goal` | `goal_baseline`, `goal_select_level` | `goal/baseline.html`, `select_level.html` | `BaselineForm`, `GoalLevelForm` |
| Incentives Matter | `MysteryBoxReward`, `UserReward` | `open_mystery_box`, `my_rewards` | `rewards/*.html` | - |
| Intrinsic Motivation | `TemptationBundle`, `FocusSession` | `add_temptation`, `start_focus`, `focus_timer` | `temptation/*.html` | - |

---

### ⚡ AI Integration

AI ใช้ Google Gemini API ผ่านไฟล์ `core/ai_services.py`

```python
from .ai_services import maslow_ai

# ใช้งาน
question = maslow_ai.generate_why_question(goal, previous_answers)
transformed = maslow_ai.transform_goal(goal, motivation)
targets = maslow_ai.suggest_goal_levels(goal, baseline, unit)
```

**ต้องการ:** `GEMINI_API_KEY` ใน `.env`

---

### 🎨 Styling

CSS อยู่ที่ `static/css/style.css`

**CSS Variables:**
```css
--primary: #6366f1;      /* สีหลัก */
--bg-primary: #fafafa;   /* พื้นหลัง */
--text-primary: #1f2937; /* ข้อความ */
```

**Main Components:**
- `.feature-card` - การ์ด Feature
- `.day-header` - หัว Day
- `.profile-footer` - Footer user
- `.btn` - ปุ่มต่างๆ

---

## 📋 Checklist สำหรับ PR

- [ ] ทดสอบบน Local แล้ว
- [ ] Migration ทำงานได้
- [ ] ไม่มี console errors
- [ ] Responsive บน mobile
- [ ] อัพเดท README ถ้าเพิ่ม Feature ใหม่

---

## 🔑 Environment Variables

```env
# .env
SECRET_KEY=your-secret-key
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
```

---

## 👨‍💻 Team Contacts

| Role | Name | Responsibility |
|------|------|----------------|
| Lead | - | Overall architecture |
| Frontend | - | Templates, CSS, JS |
| Backend | - | Models, Views, API |
| AI | - | Prompt engineering |

---

## 📄 License

MIT License
