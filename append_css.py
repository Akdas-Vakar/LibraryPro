with open('c:/Users/akdas/OneDrive/Desktop/alishka/frontend/static/css/style.css', 'a') as f:
    f.write('''
/* --- USER DROPDOWN --- */
.user-dropdown { position: relative; margin-left: 1rem; }
.user-dropdown-toggle {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.4rem 0.6rem; border-radius: 8px; cursor: pointer;
  transition: background 0.2s ease;
}
.user-dropdown-toggle:hover { background: rgba(0,0,0,0.05); }
[data-theme="dark"] .user-dropdown-toggle:hover { background: rgba(255,255,255,0.05); }

.user-avatar-sm {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-primary); color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.1rem;
}
.user-name-sm { font-weight: 600; font-size: 0.9rem; color: var(--text-primary); line-height: 1.2; }
.user-role-sm { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }

.user-dropdown-menu {
  position: absolute; top: 110%; right: 0;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 10px; box-shadow: var(--shadow-lg);
  min-width: 180px; padding: 0.5rem 0; z-index: 1050;
  opacity: 0; visibility: hidden; transform: translateY(10px);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.user-dropdown-menu.show { opacity: 1; visibility: visible; transform: translateY(0); }

.user-dropdown-menu a {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 1rem; color: var(--text-primary); text-decoration: none;
  font-size: 0.9rem; font-weight: 500; transition: background 0.2s;
}
.user-dropdown-menu a:hover { background: rgba(0,0,0,0.03); }
[data-theme="dark"] .user-dropdown-menu a:hover { background: rgba(255,255,255,0.05); }

.dropdown-divider { height: 1px; background: var(--border); margin: 0.4rem 0; }
''')
