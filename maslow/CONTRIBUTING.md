# Contributing Guide

## 🚀 Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your keys
3. Create virtual environment: `python -m venv venv`
4. Activate: `.\venv\Scripts\activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run migrations: `python manage.py migrate`
7. Run server: `python manage.py runserver`

---

## 📂 File Ownership

แต่ละคนรับผิดชอบไฟล์ต่างกัน:

### Frontend Developer
```
templates/             # HTML templates ทั้งหมด
static/css/style.css   # Stylesheet
static/js/app.js       # JavaScript
```

### Backend Developer
```
core/models.py         # Database models
core/views.py          # View functions
core/forms.py          # Form classes
core/urls.py           # URL routing
```

### AI/ML Developer
```
core/ai_services.py    # AI integration & prompts
```

---

## 🔄 Workflow การเพิ่ม Feature ใหม่

### 1. สร้าง Branch
```bash
git checkout -b feature/day3-feature-name
```

### 2. เขียน Model (ถ้าต้องการ)
```python
# core/models.py
class NewModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ...
```

### 3. สร้าง Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. เขียน View
```python
# core/views.py
@login_required
def new_view(request):
    return render(request, 'folder/template.html', {})
```

### 5. เพิ่ม URL
```python
# core/urls.py
path('new-path/', views.new_view, name='new_view'),
```

### 6. สร้าง Template
```html
{% extends 'base.html' %}
{% block content %}
<!-- Your content -->
{% endblock %}
```

### 7. อัพเดท Home (ถ้าเป็น Day ใหม่)
แก้ไข `templates/home.html` เพิ่ม Day page ใหม่

### 8. Test & Commit
```bash
python manage.py runserver
git add .
git commit -m "feat: add feature name"
git push origin feature/day3-feature-name
```

---

## 📋 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Model | PascalCase | `UserReward`, `FocusSession` |
| View | snake_case | `goal_create`, `open_mystery_box` |
| URL name | snake_case | `'start_focus'`, `'my_rewards'` |
| Template folder | lowercase | `rewards/`, `temptation/` |
| CSS class | kebab-case | `.feature-card`, `.day-header` |

---

## 🎯 Day Structure

```
Day N
├── Feature A
│   ├── Model (if needed)
│   ├── View function
│   ├── URL pattern
│   ├── Template folder
│   └── Forms (if needed)
│
└── Feature B
    └── ...
```

---

## ✅ PR Checklist

Before submitting PR:

- [ ] Code runs without errors
- [ ] Migrations work (`makemigrations` + `migrate`)
- [ ] No console errors in browser
- [ ] Mobile responsive
- [ ] Thai language texts are correct
- [ ] Updated README if adding new feature
- [ ] Tested with login/logout flow

---

## 🐛 Common Issues

### Migration conflicts
```bash
python manage.py migrate --fake
python manage.py makemigrations
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
```

### Template not found
Check that template path matches URL and view exactly.
