

'use strict';

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  initNotifications();
  initFlashDismiss();
  initCountUp();
  initActiveLink();
});

function initTheme() {
  const toggle   = document.getElementById('themeToggle');
  const icon     = document.getElementById('themeIcon');
  const html     = document.documentElement;

  const saved = localStorage.getItem('lp-theme') || 'light';
  applyTheme(saved);

  toggle && toggle.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    const next    = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('lp-theme', next);
  });

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }
}

function initSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebarOverlay');
  const openBtn  = document.getElementById('sidebarOpen');
  const closeBtn = document.getElementById('sidebarClose');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    overlay && overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay && overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  openBtn  && openBtn.addEventListener('click', openSidebar);
  closeBtn && closeBtn.addEventListener('click', closeSidebar);
  overlay  && overlay.addEventListener('click', closeSidebar);

  const toggleInside = document.getElementById('sidebarToggleInside');
  if (toggleInside) {
    toggleInside.addEventListener('click', () => {
      document.body.classList.toggle('sidebar-collapsed');
    });
  }

  const navLinks = sidebar.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    const textSpan = link.querySelector('span');
    if (textSpan) {
      link.setAttribute('title', textSpan.textContent.trim());
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth >= 768) closeSidebar();
  });
}

function initNotifications() {
  const btn   = document.getElementById('notifBtn');
  const panel = document.getElementById('notifPanel');
  const markBtn = document.getElementById('markAllRead');

  if (!btn || !panel) return;

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    panel.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (!panel.contains(e.target) && !btn.contains(e.target)) {
      panel.classList.remove('open');
    }
  });

  markBtn && markBtn.addEventListener('click', () => {
    fetch('/notifications/mark_read', { method: 'POST' })
      .then(r => r.json())
      .then(() => {
        
        const badge = btn.querySelector('.notif-badge');
        if (badge) badge.remove();
        
        const list = document.getElementById('notifList');
        if (list) {
          list.innerHTML = `
            <div class="notif-empty">
              <i class="fas fa-check-circle"></i>
              <p>All caught up!</p>
            </div>`;
        }
        panel.classList.remove('open');
      })
      .catch(() => {});
  });
}

function initFlashDismiss() {
  const msgs = document.querySelectorAll('.flash-msg');

  msgs.forEach(msg => {
    
    setTimeout(() => dismissFlash(msg), 5000);

    const closeBtn = msg.querySelector('.flash-close');
    closeBtn && closeBtn.addEventListener('click', () => dismissFlash(msg));
  });

  function dismissFlash(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    el.style.transition = 'opacity .3s ease, transform .3s ease';
    setTimeout(() => el.remove(), 320);
  }
}

function initCountUp() {
  const elements = document.querySelectorAll('.count-up');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el     = entry.target;
        const target = parseInt(el.getAttribute('data-target')) || 0;
        animateCount(el, target);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.2 });

  elements.forEach(el => observer.observe(el));

  function animateCount(el, target) {
    const duration = 800;
    const start    = performance.now();

    function step(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3); 
      el.textContent = Math.round(eased * target);

      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }
}

function initActiveLink() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

const liveSearch = document.getElementById('liveSearch');
if (liveSearch) {
  liveSearch.addEventListener('input', debounce((e) => {
    const q     = e.target.value.toLowerCase();
    const rows  = document.querySelectorAll('.book-row');
    let visible = 0;

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const show = text.includes(q);
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    const badge = document.getElementById('bookCount');
    if (badge) badge.textContent = visible;
  }, 200));
}

window.confirmDelete = function(form, name) {
  if (confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
    form.submit();
  }
};

function updateFinePreview(dueDateStr) {
  const preview = document.getElementById('finePreview');
  if (!preview || !dueDateStr || dueDateStr === '-') {
    if (preview) preview.textContent = '—';
    return;
  }

  const due   = new Date(dueDateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const diff = Math.floor((today - due) / (1000 * 60 * 60 * 24));
  if (diff > 0) {
    preview.textContent = `₹${(diff * 2).toFixed(2)} (${diff} days late)`;
    preview.style.color = 'var(--color-danger)';
  } else {
    preview.textContent = 'No fine';
    preview.style.color = 'var(--color-success)';
  }
}

const returnSelect = document.querySelector('.return-book-select');
if (returnSelect) {
  returnSelect.addEventListener('change', (e) => {
    const opt     = e.target.options[e.target.selectedIndex];
    const dueDate = opt.getAttribute('data-due');
    updateFinePreview(dueDate);

    const idInput = document.querySelector('[name=book_id]');
    if (idInput) idInput.value = opt.value;
  });
}

document.addEventListener('DOMContentLoaded', () => {
    const userToggle = document.getElementById('userDropdownToggle');
    const userMenu = document.getElementById('userDropdownMenu');
    if (userToggle && userMenu) {
        userToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            userMenu.classList.toggle('show');
        });
        document.addEventListener('click', (e) => {
            if (!userMenu.contains(e.target) && !userToggle.contains(e.target)) {
                userMenu.classList.remove('show');
            }
        });
    }
});

window.filterTable = function(query) {
    const q = query.toLowerCase();
    const rows = document.querySelectorAll('.table-pro tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
    });
};
