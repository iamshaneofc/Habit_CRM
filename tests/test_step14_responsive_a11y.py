"""
Test suite for Step 14: Responsive Design & Accessibility.
Verifies:
- All icon-only buttons and modal close buttons have descriptive aria-labels.
- Modals define dialog roles, aria-modal, and aria-labelledby.
- CSS provides focus-visible outlines, reduced-motion preferences, sticky table headers on mobile, and responsive breakpoints.
- Jinja template renders without syntax or context errors.
"""
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import database
from main import app
from auth import create_access_token
from models import User

def test_responsive_css_and_a11y():
    css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
    assert os.path.exists(css_path), "style.css must exist"
    
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # 1. Keyboard Focus
    assert ":focus-visible" in css, ":focus-visible styling must be defined"
    assert "outline:" in css, "Focus outline must be set"

    # 2. Reduced motion
    assert "prefers-reduced-motion: reduce" in css, "prefers-reduced-motion must be respected"

    # 3. Responsive Breakpoints
    assert "@media (max-width: 1100px)" in css, "1100px breakpoint for sidebar stacking must exist"
    assert "@media (max-width: 960px)" in css, "960px breakpoint for sticky habit column must exist"
    assert "@media (max-width: 768px)" in css, "768px breakpoint for tablet/mobile must exist"
    assert "@media (max-width: 480px)" in css, "480px breakpoint for smartphones must exist"

    # 4. Sticky habit column
    assert "position: sticky" in css, "Sticky column styling must exist for responsive table"
    assert "th.th-habit" in css and "td.td-habit" in css, "Habit column must be sticky"

def test_template_aria_labels():
    tmpl_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(tmpl_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Modal accessibility
    assert 'role="dialog"' in html, "Modals must have role='dialog'"
    assert 'aria-modal="true"' in html, "Modals must have aria-modal='true'"
    assert 'aria-labelledby="modal-title"' in html
    assert 'aria-labelledby="manage-modal-title"' in html
    assert 'aria-labelledby="note-modal-title"' in html

    # 2. Icon-only action buttons have aria-label
    assert 'aria-label="Edit habit' in html, "Edit button must have aria-label"
    assert 'aria-label="Archive habit' in html, "Archive button must have aria-label"
    assert 'aria-label="Close modal"' in html, "Close modal buttons must have aria-label"
    assert 'aria-label="Go to Previous Week"' in html, "Prev week must have aria-label"
    assert 'aria-label="Go to Next Week"' in html, "Next week must have aria-label"
    assert 'aria-label="Filter by Month"' in html, "Month select must have aria-label"
    assert 'aria-label="Filter by Year"' in html, "Year select must have aria-label"

def test_dashboard_authenticated_render():
    database.check_and_stabilize_db()
    db = database.SessionLocal()
    try:
        user = db.query(User).filter(User.email == "a11y_user@example.com").first()
        if not user:
            user = User(email="a11y_user@example.com", hashed_password="hashed_pw_test", full_name="A11y User")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        token = create_access_token({"sub": str(user.id), "email": user.email})
        with TestClient(app) as client:
            client.cookies.set("habit_crm_session", token)
            res = client.get("/")
            assert res.status_code == 200
            content = res.text
            
            # Verify rendered elements
            assert "Weekly Tracker (Monday – Sunday)" in content
            assert "role=\"dialog\"" in content
            assert "aria-label=\"Close modal\"" in content
            assert "A11y User" in content
    finally:
        db.close()

if __name__ == "__main__":
    print("Running Step 14 tests...")
    test_responsive_css_and_a11y()
    print("[OK] test_responsive_css_and_a11y passed.")
    test_template_aria_labels()
    print("[OK] test_template_aria_labels passed.")
    test_dashboard_authenticated_render()
    print("[OK] test_dashboard_authenticated_render passed.")
    print("All Step 14 accessibility and responsiveness tests passed successfully!")
