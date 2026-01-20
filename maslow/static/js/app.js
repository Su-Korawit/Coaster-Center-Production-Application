/**
 * Maslow - JavaScript Interactions
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize animations
    initAnimations();

    // Initialize goal level selection
    initLevelSelection();

    // Initialize progress updates
    initProgressUpdates();

    // Auto-dismiss messages
    initMessages();
});

/**
 * Fade-in animations for elements
 */
function initAnimations() {
    const elements = document.querySelectorAll('.animate-on-scroll');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
}

/**
 * Goal level selection (Safe/Growth/Stretch)
 */
function initLevelSelection() {
    const levelOptions = document.querySelectorAll('.level-option');
    const hiddenInput = document.getElementById('goal_level');

    levelOptions.forEach(option => {
        option.addEventListener('click', function () {
            // Remove selected from all
            levelOptions.forEach(opt => opt.classList.remove('selected'));

            // Add selected to clicked
            this.classList.add('selected');

            // Update hidden input
            if (hiddenInput) {
                hiddenInput.value = this.dataset.level;
            }
        });
    });
}

/**
 * Progress update via AJAX
 */
function initProgressUpdates() {
    const progressBtns = document.querySelectorAll('.update-progress-btn');

    progressBtns.forEach(btn => {
        btn.addEventListener('click', async function () {
            const goalId = this.dataset.goalId;
            const progressInput = document.getElementById(`progress-${goalId}`);
            const progress = parseInt(progressInput.value, 10);

            if (isNaN(progress) || progress < 0) {
                showMessage('กรุณาใส่ตัวเลขที่ถูกต้อง', 'error');
                return;
            }

            try {
                const response = await fetch(`/goal/${goalId}/progress/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ progress: progress })
                });

                const data = await response.json();

                if (data.success) {
                    // Update progress bar
                    const progressBar = document.querySelector(`#goal-${goalId} .progress-fill`);
                    if (progressBar) {
                        progressBar.style.width = `${data.percentage}%`;
                    }

                    if (data.completed) {
                        showMessage('🎉 ยอดเยี่ยม! ทำสำเร็จแล้ว!', 'success');
                        location.reload();
                    } else {
                        showMessage('อัพเดทสำเร็จ!', 'success');
                    }
                }
            } catch (error) {
                console.error('Error updating progress:', error);
                showMessage('เกิดข้อผิดพลาด', 'error');
            }
        });
    });
}

/**
 * Get CSRF token from cookie
 */
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show message toast
 */
function showMessage(text, type = 'success') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();

    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.innerHTML = `
        <span>${type === 'success' ? '✓' : '⚠'}</span>
        <span>${text}</span>
    `;

    messagesContainer.appendChild(message);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 300);
    }, 3000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

/**
 * Auto-dismiss messages
 */
function initMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        }, 4000);
    });
}

/**
 * Ripple effect for buttons
 */
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');

        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

/**
 * Typing animation for AI responses
 */
function typeText(element, text, speed = 30) {
    let index = 0;
    element.textContent = '';

    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Apply typing effect to AI bubbles
document.querySelectorAll('.ai-bubble .text[data-typing]').forEach(el => {
    const text = el.textContent;
    typeText(el, text);
});
