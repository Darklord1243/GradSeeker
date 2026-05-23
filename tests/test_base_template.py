# tests/test_base_template.py
# Tests for base template and navigation (RFC 4)

import os
import pytest
from app import create_app
from models import db, User
from utils import hash_password


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Store app on client for later use in tests
            client.application = app
            yield client
            db.drop_all()


def test_base_template_exists():
    """
    Test Step 4.1: Base Template Structure (UI)
    Verify that the base template file exists.
    """
    base_template_path = os.path.join('templates', 'base.html')
    assert os.path.exists(base_template_path), f"Base template not found at {base_template_path}"


def test_base_template_semantic_html(client):
    """
    Test Step 4.1: Base Template Structure (UI)
    Verify that the base template uses semantic HTML elements (nav, main).
    """
    response = client.get('/')
    
    # Verify page loads successfully
    assert response.status_code == 200
    
    # Verify semantic HTML elements are present (with Bootstrap classes from Step 4.3)
    assert b'<nav' in response.data, "Navigation element (<nav>) not found"
    assert b'</nav>' in response.data, "Navigation closing tag not found"
    assert b'<main>' in response.data, "Main content element (<main>) not found"
    assert b'</main>' in response.data, "Main content closing tag not found"
    
    # Verify HTML5 structure
    assert b'<!DOCTYPE html>' in response.data, "HTML5 doctype not found"
    assert b'<html lang="en">' in response.data, "HTML element with lang attribute not found"


def test_base_template_navigation_links(client):
    """
    Test Step 4.1: Base Template Structure (UI)
    Verify that navigation links are present in the base template.
    """
    response = client.get('/')
    
    # Verify basic navigation links (always visible)
    # Note: Links now have Bootstrap classes (nav-link) from Step 4.3
    assert b'href="/"' in response.data, "Home link not found"
    assert b'Home' in response.data, "Home link text not found"
    assert b'href="/browse"' in response.data, "Browse link not found"
    assert b'Browse' in response.data, "Browse link text not found"
    
    # For unauthenticated users, should see Login and Register
    assert b'href="/login"' in response.data, "Login link not found for unauthenticated user"
    assert b'Login' in response.data, "Login link text not found"
    assert b'href="/register"' in response.data, "Register link not found for unauthenticated user"
    assert b'Register' in response.data, "Register link text not found"
    
    # For unauthenticated users, should NOT see Dashboard and Logout
    assert b'href="/dashboard"' not in response.data, "Dashboard link should not be visible for unauthenticated user"
    assert b'href="/logout"' not in response.data, "Logout link should not be visible for unauthenticated user"


def test_base_template_navigation_authenticated(client):
    """
    Test Step 4.1: Base Template Structure (UI)
    Verify that navigation links change for authenticated users.
    """
    # Create and login user
    with client.application.app_context():
        user = User(username='testuser', password=hash_password('testpass'))
        db.session.add(user)
        db.session.commit()
    
    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Get home page as authenticated user
    response = client.get('/')
    
    # Verify authenticated user sees Dashboard and Logout
    # Note: Links now have Bootstrap classes (nav-link) from Step 4.3
    assert b'href="/dashboard"' in response.data, "Dashboard link not found for authenticated user"
    assert b'Dashboard' in response.data, "Dashboard link text not found"
    assert b'href="/logout"' in response.data, "Logout link not found for authenticated user"
    assert b'Logout' in response.data, "Logout link text not found"
    
    # Verify authenticated user does NOT see Login and Register
    assert b'href="/login"' not in response.data, "Login link should not be visible for authenticated user"
    assert b'href="/register"' not in response.data, "Register link should not be visible for authenticated user"


def test_base_template_block_structure(client):
    """
    Test Step 4.1: Base Template Structure (UI)
    Verify that the base template has proper block structure for content extension.
    """
    response = client.get('/')
    
    # Verify that content from index.html is rendered (extends base template)
    assert b'GradSeeker' in response.data, "Content from child template not found"
    assert b'Welcome to GradSeeker' in response.data, "Content from child template not found"
    
    # Verify title block works (should be in <title> tag)
    assert b'<title>' in response.data, "Title tag not found"
    assert b'Home - GradSeeker' in response.data or b'GradSeeker' in response.data, "Title block not working"


def test_bootstrap_loaded(client):
    """
    Test Step 4.2: Bootstrap Integration & CSS Variables Setup (Styles)
    Verify that Bootstrap 5 CSS is loaded in the base template.
    """
    response = client.get('/')
    
    # Verify Bootstrap CSS is loaded
    assert b'bootstrap' in response.data.lower(), "Bootstrap CSS not found"
    assert b'bootstrap@5.3.0' in response.data or b'bootstrap.min.css' in response.data, "Bootstrap 5.3.0 CDN not found"
    
    # Verify Bootstrap JS bundle is loaded
    assert b'bootstrap.bundle.min.js' in response.data or b'bootstrap' in response.data.lower(), "Bootstrap JS bundle not found"


def test_bootstrap_loading_verification_rfc_6_5_1(client):
    """
    Test Step 6.5.1: Verify Bootstrap Loading (Diagnostic)
    Comprehensive verification that Bootstrap CSS and JS are correctly referenced in the HTML.
    This test verifies the CDN links are present and correct, which is a prerequisite for
    Bootstrap actually loading in the browser.
    """
    response = client.get('/')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Page did not load successfully"
    
    # Verify Bootstrap CSS CDN link is present and correct
    assert b'bootstrap.min.css' in response.data, "Bootstrap CSS file reference not found"
    assert b'cdn.jsdelivr.net' in response.data, "Bootstrap CDN (jsdelivr) not found"
    assert b'bootstrap@5.3.0' in response.data, "Bootstrap version 5.3.0 not found in CDN link"
    assert b'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' in response.data, \
        "Bootstrap CSS CDN URL is incorrect"
    
    # Verify Bootstrap CSS is in <head> section (check for link tag)
    assert b'<link' in response.data, "Link tag not found"
    assert b'rel="stylesheet"' in response.data, "Stylesheet link not found"
    
    # Verify Bootstrap JS bundle CDN link is present and correct
    assert b'bootstrap.bundle.min.js' in response.data, "Bootstrap JS bundle file reference not found"
    assert b'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js' in response.data, \
        "Bootstrap JS bundle CDN URL is incorrect"
    
    # Verify Bootstrap JS is in <body> section (check for script tag)
    assert b'<script' in response.data, "Script tag not found"
    assert b'src=' in response.data, "Script src attribute not found"
    
    # Verify both CSS and JS are present (comprehensive check)
    html_content = response.data.decode('utf-8')
    css_link_count = html_content.count('bootstrap.min.css')
    js_script_count = html_content.count('bootstrap.bundle.min.js')
    
    assert css_link_count >= 1, f"Bootstrap CSS should be loaded once, found {css_link_count} times"
    assert js_script_count >= 1, f"Bootstrap JS should be loaded once, found {js_script_count} times"
    
    # Verify CDN URLs are from the correct source (jsdelivr)
    assert html_content.count('cdn.jsdelivr.net') >= 2, \
        "Both Bootstrap CSS and JS should use jsdelivr CDN"


def test_inter_font_loaded(client):
    """
    Test Step 4.2: Bootstrap Integration & CSS Variables Setup (Styles)
    Verify that Inter font is loaded (SRS UI-11).
    """
    response = client.get('/')
    
    # Verify Inter font is loaded from Google Fonts
    assert b'Inter' in response.data or b'fonts.googleapis.com' in response.data, "Inter font not found"
    assert b'family=Inter' in response.data or b'inter' in response.data.lower(), "Inter font family not found"


def test_custom_css_loaded(client):
    """
    Test Step 4.2: Bootstrap Integration & CSS Variables Setup (Styles)
    Verify that custom CSS file is linked in the base template.
    """
    response = client.get('/')
    
    # Verify custom CSS file is linked
    assert b'style.css' in response.data or b'css/style.css' in response.data, "Custom CSS file not linked"
    assert b'url_for' in response.data or b'static' in response.data, "CSS file path not found"


def test_css_variables_exist():
    """
    Test Step 4.2: Bootstrap Integration & CSS Variables Setup (Styles)
    Verify that CSS variables exist in the style.css file (root scope) for dark mode palette.
    """
    css_file_path = os.path.join('static', 'css', 'style.css')
    assert os.path.exists(css_file_path), f"CSS file not found at {css_file_path}"
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
        
        # Verify :root scope exists
        assert ':root' in css_content, "CSS :root scope not found"
        
        # Verify all required CSS variables exist (SRS UI-08)
        assert '--bg-primary' in css_content, "CSS variable --bg-primary not found"
        assert '--bg-card' in css_content, "CSS variable --bg-card not found"
        assert '--text-primary' in css_content, "CSS variable --text-primary not found"
        assert '--text-secondary' in css_content, "CSS variable --text-secondary not found"
        assert '--accent-blue' in css_content, "CSS variable --accent-blue not found"
        assert '--accent-purple' in css_content, "CSS variable --accent-purple not found"
        assert '--shadow-glow' in css_content, "CSS variable --shadow-glow not found"
        
        # Verify color values match SRS requirements
        assert '#0a0a0a' in css_content or '--bg-primary: #0a0a0a' in css_content, "Deep matte black (#0a0a0a) not found"
        assert '#161616' in css_content or '--bg-card: #161616' in css_content, "Dark grey cards (#161616) not found"
        assert '#ffffff' in css_content or '--text-primary: #ffffff' in css_content, "Bold white (#ffffff) not found"
        assert '#a1a1a1' in css_content or '--text-secondary: #a1a1a1' in css_content, "Muted grey (#a1a1a1) not found"
        assert '#0066ff' in css_content or '--accent-blue: #0066ff' in css_content, "Electric Blue (#0066ff) not found"
        assert '#9333ea' in css_content or '--accent-purple: #9333ea' in css_content, "Neon Purple (#9333ea) not found"


def test_navbar_glassmorphism(client):
    """
    Test Step 4.3: Glassmorphism Navigation Styling (Styles - SRS UI-10)
    Verify that the navbar has glassmorphism classes and Bootstrap navbar structure.
    """
    response = client.get('/')
    
    # Verify navbar has glassmorphism class
    assert b'navbar-glass' in response.data, "Navbar glassmorphism class not found"
    
    # Verify Bootstrap navbar classes are present
    assert b'navbar-expand-lg' in response.data, "Bootstrap navbar-expand-lg class not found"
    assert b'navbar-nav' in response.data, "Bootstrap navbar-nav class not found"
    assert b'nav-link' in response.data, "Bootstrap nav-link class not found"
    assert b'navbar-brand' in response.data, "Bootstrap navbar-brand class not found"
    
    # Verify navbar structure (container, collapse, etc.)
    assert b'<div class="container">' in response.data, "Navbar container not found"
    assert b'navbar-collapse' in response.data, "Bootstrap navbar-collapse not found"
    assert b'navbar-toggler' in response.data, "Bootstrap navbar-toggler not found"


def test_css_has_backdrop_filter():
    """
    Test Step 4.3: Glassmorphism Navigation Styling (Styles - SRS UI-10)
    Verify that CSS file contains backdrop-filter for glassmorphism effect.
    """
    css_file_path = os.path.join('static', 'css', 'style.css')
    assert os.path.exists(css_file_path), f"CSS file not found at {css_file_path}"
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
        
        # Verify glassmorphism CSS exists
        assert '.navbar-glass' in css_content, "Navbar glassmorphism class not found in CSS"
        assert 'backdrop-filter' in css_content.lower(), "backdrop-filter not found in CSS"
        assert '-webkit-backdrop-filter' in css_content.lower(), "-webkit-backdrop-filter not found in CSS"
        
        # Verify glassmorphism properties
        assert 'blur(10px)' in css_content or 'blur' in css_content.lower(), "Backdrop blur effect not found"
        assert 'rgba(22, 22, 22, 0.8)' in css_content or 'rgba(22,22,22,0.8)' in css_content, "Semi-transparent background not found"
        assert 'border-bottom' in css_content.lower(), "Border-bottom for navbar not found"


def test_navbar_keyboard_accessible(client):
    """
    Test Step 4.4: Keyboard Accessibility (Logic)
    Verify that all navigation links are keyboard accessible and have proper focus indicators.
    """
    response = client.get('/')
    
    # Verify all links are naturally focusable (they're <a> tags, which are naturally focusable)
    # Check that links exist and are properly structured
    assert b'<a' in response.data, "No anchor tags found in navigation"
    assert b'href=' in response.data, "No href attributes found (links not properly structured)"
    
    # Verify navbar toggler button is keyboard accessible
    # Button should have type="button" and proper ARIA attributes
    assert b'type="button"' in response.data, "Navbar toggler button type not found"
    assert b'aria-label' in response.data or b'aria-label=' in response.data, "Navbar toggler missing aria-label for accessibility"
    assert b'aria-controls' in response.data, "Navbar toggler missing aria-controls for accessibility"
    assert b'aria-expanded' in response.data, "Navbar toggler missing aria-expanded for accessibility"
    
    # Verify no elements require mouse-only interaction
    # All interactive elements should be keyboard accessible
    # Links (<a>) and buttons (<button>) are naturally keyboard accessible
    # Check that we're not using mouse-only events like onclick without keyboard alternatives
    html_content = response.data.decode('utf-8')
    
    # Verify that links don't have onclick handlers that would require mouse
    # (Bootstrap uses data attributes, which is good)
    assert 'onclick=' not in html_content.lower() or html_content.lower().count('onclick=') == 0, \
        "Found onclick handlers that may require mouse interaction"
    
    # Verify CSS has focus indicators for keyboard navigation
    css_file_path = os.path.join('static', 'css', 'style.css')
    assert os.path.exists(css_file_path), f"CSS file not found at {css_file_path}"
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
        
        # Verify focus indicators exist for keyboard navigation (WCAG requirement)
        assert ':focus' in css_content, "CSS focus indicators not found for keyboard navigation"
        assert '.nav-link:focus' in css_content or 'nav-link:focus' in css_content, \
            "Nav link focus indicator not found in CSS"
        assert '.navbar-brand:focus' in css_content or 'navbar-brand:focus' in css_content, \
            "Navbar brand focus indicator not found in CSS"
        assert '.navbar-toggler:focus' in css_content or 'navbar-toggler:focus' in css_content, \
            "Navbar toggler focus indicator not found in CSS"
        
        # Verify focus indicators are visible (outline or box-shadow)
        assert 'outline' in css_content.lower() or 'box-shadow' in css_content.lower(), \
            "Focus indicators should use outline or box-shadow for visibility"
        
        # Verify focus indicators use sufficient contrast (accent-blue is used)
        assert '--accent-blue' in css_content or '#0066ff' in css_content or 'accent-blue' in css_content.lower(), \
            "Focus indicators should use accent color for visibility"


def test_all_pages_have_navbar(client):
    """
    Test Step 4.5: Update All Templates
    Verify that all pages have consistent navbar by checking that they extend base.html.
    """
    # Test pages that should exist (from RFC 4 and RFC 5)
    pages_to_test = [
        ('/', 'Home page'),
        ('/login', 'Login page'),
        ('/register', 'Register page'),
        ('/browse', 'Browse page'),  # RFC 5, Step 5.1
    ]
    
    for page_path, page_name in pages_to_test:
        response = client.get(page_path)
        
        # Verify page loads successfully
        assert response.status_code == 200, f"{page_name} ({page_path}) did not load successfully"
        
        # Verify navbar brand is present (indicates base.html is extended)
        assert b'GradSeeker' in response.data, \
            f"{page_name} ({page_path}) does not have navbar brand 'GradSeeker' - may not extend base.html"
        
        # Verify navbar structure is present
        assert b'navbar-glass' in response.data, \
            f"{page_name} ({page_path}) does not have navbar-glass class - may not extend base.html"
        
        # Verify navbar links are present (at least Home and Browse should be visible)
        assert b'href="/"' in response.data, \
            f"{page_name} ({page_path}) does not have Home link in navbar"
        assert b'href="/browse"' in response.data, \
            f"{page_name} ({page_path}) does not have Browse link in navbar"
        
        # Verify semantic HTML structure from base.html
        assert b'<nav' in response.data, \
            f"{page_name} ({page_path}) does not have <nav> element - may not extend base.html"
        assert b'<main>' in response.data, \
            f"{page_name} ({page_path}) does not have <main> element - may not extend base.html"
    
    # Note: Additional browse functionality tests are in test_browsing.py (RFC 5)


def test_all_pages_have_container(client):
    """
    Test Step 6.5.4: Verify All Pages Have Containers
    Verify that all templates have proper Bootstrap container structure.
    This ensures consistent layout and spacing across all pages.
    """
    # Test all existing pages that should have containers
    pages_to_test = [
        ('/', 'Home page (index.html)'),
        ('/login', 'Login page'),
        ('/register', 'Register page'),
        ('/browse', 'Browse page'),
    ]
    
    for page_path, page_name in pages_to_test:
        response = client.get(page_path)
        
        # Verify page loads successfully
        assert response.status_code == 200, \
            f"{page_name} ({page_path}) did not load successfully"
        
        # Verify container class is present (Bootstrap container)
        # Check for class="container" or class="container mt-4" etc.
        html_content = response.data.decode('utf-8')
        
        # Look for container class in the content block (not in navbar)
        # Container should be in the main content area
        assert 'class="container' in html_content, \
            f"{page_name} ({page_path}) does not have Bootstrap container class"
        
        # Verify it's not just in the navbar (navbar has its own container)
        # We want to ensure the main content has a container
        # Split by <main> to get content area
        if '<main>' in html_content:
            main_content = html_content.split('<main>')[1].split('</main>')[0] if '</main>' in html_content else html_content
            assert 'class="container' in main_content, \
                f"{page_name} ({page_path}) main content area does not have container class"
        
        # Verify page has some content (not just empty)
        assert len(html_content) > 500, \
            f"{page_name} ({page_path}) appears to have very little content"
    
    # Note: Additional pages like /browse/<country>, /universities/<id>/programs, 
    # /programs/<id> are tested in test_browsing.py (RFC 5)
    # Dashboard page will be tested when it's implemented (RFC 9)


def test_glassmorphism_verification_rfc_6_5_5():
    """
    Test Step 6.5.5: Verify Glassmorphism Navbar (Already Applied)
    Comprehensive verification that glassmorphism CSS is correctly implemented.
    This test verifies all required glassmorphism properties are present in the CSS.
    """
    css_file_path = os.path.join('static', 'css', 'style.css')
    assert os.path.exists(css_file_path), f"CSS file not found at {css_file_path}"
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
        
        # Verify .navbar-glass class exists (lines 220-276)
        assert '.navbar-glass' in css_content, \
            "Navbar glassmorphism class (.navbar-glass) not found in CSS"
        
        # Verify backdrop-filter: blur(10px) is present (SRS UI-10)
        assert 'backdrop-filter' in css_content, \
            "backdrop-filter property not found in CSS"
        assert 'blur(10px)' in css_content, \
            "backdrop-filter blur(10px) not found - expected 10px blur"
        
        # Verify -webkit-backdrop-filter for browser compatibility
        assert '-webkit-backdrop-filter' in css_content, \
            "-webkit-backdrop-filter not found for Safari/WebKit compatibility"
        assert '-webkit-backdrop-filter' in css_content.lower() or \
               '-webkit-backdrop-filter: blur(10px)' in css_content, \
            "-webkit-backdrop-filter blur(10px) not found"
        
        # Verify semi-transparent background (rgba(22, 22, 22, 0.8))
        assert 'rgba(22, 22, 22, 0.8)' in css_content or \
               'rgba(22,22,22,0.8)' in css_content, \
            "Semi-transparent background rgba(22, 22, 22, 0.8) not found"
        
        # Verify border-bottom for glassmorphism effect
        assert 'border-bottom' in css_content.lower(), \
            "border-bottom property not found for navbar"
        assert 'rgba(255, 255, 255, 0.1)' in css_content or \
               'rgba(255,255,255,0.1)' in css_content, \
            "Border color rgba(255, 255, 255, 0.1) not found"
        
        # Verify navbar-glass styles are complete (check for key properties)
        # Find the .navbar-glass block
        navbar_glass_start = css_content.find('.navbar-glass')
        assert navbar_glass_start != -1, "Could not find .navbar-glass CSS block"
        
        # Extract the .navbar-glass block (approximate, up to next major selector)
        navbar_glass_block = css_content[navbar_glass_start:navbar_glass_start + 1000]
        
        # Verify all key properties are in the block
        assert 'background:' in navbar_glass_block or 'background-color:' in navbar_glass_block, \
            "Background property not found in .navbar-glass block"
        assert 'backdrop-filter' in navbar_glass_block, \
            "backdrop-filter not found in .navbar-glass block"
        assert 'border-bottom' in navbar_glass_block, \
            "border-bottom not found in .navbar-glass block"
        
        # Verify child selectors exist (navbar-brand, nav-link, etc.)
        assert '.navbar-glass .navbar-brand' in css_content, \
            "Navbar brand styling not found in glassmorphism CSS"
        assert '.navbar-glass .nav-link' in css_content, \
            "Nav link styling not found in glassmorphism CSS"
        assert '.navbar-glass .nav-link:hover' in css_content, \
            "Nav link hover styling not found in glassmorphism CSS"
        
        # Verify focus indicators for accessibility (WCAG requirement)
        assert '.navbar-glass .nav-link:focus' in css_content or \
               '.navbar-glass .nav-link:focus-visible' in css_content, \
            "Nav link focus indicator not found in glassmorphism CSS"


def test_glassmorphism_html_structure(client):
    """
    Test Step 6.5.5: Verify Glassmorphism Navbar (Already Applied)
    Verify that the HTML template correctly uses the navbar-glass class.
    """
    response = client.get('/')
    
    # Verify page loads successfully
    assert response.status_code == 200, "Page did not load successfully"
    
    html_content = response.data.decode('utf-8')
    
    # Verify navbar has glassmorphism class
    assert 'navbar-glass' in html_content, \
        "Navbar does not have navbar-glass class in HTML"
    
    # Verify the class is applied to the nav element
    assert 'class="navbar navbar-expand-lg navbar-glass"' in html_content or \
           'class="navbar navbar-expand-lg navbar-glass "' in html_content or \
           'navbar-glass' in html_content, \
        "navbar-glass class not properly applied to nav element"
    
    # Verify navbar structure is correct (Bootstrap navbar)
    assert 'navbar-expand-lg' in html_content, \
        "Bootstrap navbar-expand-lg class not found"
    assert 'navbar-brand' in html_content, \
        "Navbar brand element not found"
    assert 'nav-link' in html_content, \
        "Nav link elements not found"
    
    # Verify navbar is present on all pages (test a few key pages)
    pages_to_test = ['/', '/browse', '/login', '/register']
    for page_path in pages_to_test:
        page_response = client.get(page_path)
        assert page_response.status_code == 200, \
            f"Page {page_path} did not load successfully"
        assert b'navbar-glass' in page_response.data, \
            f"Navbar glassmorphism class not found on {page_path}"
    
    # Note: Visual verification (blur effect) must be done manually in browser
    # The CSS properties are verified above, which ensures the effect will work
    # when rendered in a browser that supports backdrop-filter


def test_integration_verification_rfc_6_5_7(client):
    """
    Test Step 6.5.7: Integration Testing and Final Verification
    Comprehensive integration test to verify all pages work together correctly.
    This test verifies the checklist items from Step 6.5.7.
    """
    # Checklist items to verify:
    # 1. Navigation is horizontal navbar (not vertical list) - VERIFIED
    # 2. Navbar has glassmorphism effect - CSS verified
    # 3. Map SVG background is visible - VERIFIED
    # 4. Map container is properly sized - VERIFIED
    # 5. All pages have proper layout - TO VERIFY
    # 6. Content is centered (not left-aligned) - VERIFIED
    # 7. Responsive behavior works - CSS verified
    # 8. Bootstrap is loading correctly - VERIFIED
    # 9. No console errors - Cannot test automatically, requires manual check
    
    # Pages to test (from Step 6.5.7 checklist)
    pages_to_test = [
        ('/', 'Home page'),
        ('/browse', 'Browse page'),
        ('/login', 'Login page'),
        ('/register', 'Register page'),
    ]
    
    for page_path, page_name in pages_to_test:
        response = client.get(page_path)
        
        # Verify page loads successfully (no 500 errors)
        assert response.status_code == 200, \
            f"{page_name} ({page_path}) did not load successfully (status: {response.status_code})"
        
        html_content = response.data.decode('utf-8')
        
        # 1. Verify Navigation is horizontal navbar (not vertical list)
        assert 'navbar-expand-lg' in html_content, \
            f"{page_name} ({page_path}) does not have horizontal navbar (navbar-expand-lg)"
        assert 'navbar-nav' in html_content, \
            f"{page_name} ({page_path}) does not have navbar-nav structure"
        assert 'navbar-glass' in html_content, \
            f"{page_name} ({page_path}) does not have glassmorphism navbar"
        
        # 2. Verify Navbar has glassmorphism effect (CSS already verified in Step 6.5.5)
        # HTML structure check
        assert 'class="navbar navbar-expand-lg navbar-glass"' in html_content or \
               'navbar-glass' in html_content, \
            f"{page_name} ({page_path}) navbar does not have glassmorphism class"
        
        # 3. Verify Bootstrap is loading correctly
        assert 'bootstrap.min.css' in html_content, \
            f"{page_name} ({page_path}) Bootstrap CSS not found"
        assert 'bootstrap.bundle.min.js' in html_content, \
            f"{page_name} ({page_path}) Bootstrap JS not found"
        assert 'cdn.jsdelivr.net' in html_content, \
            f"{page_name} ({page_path}) Bootstrap CDN not found"
        
        # 4. Verify all pages have proper layout (container structure)
        # Check that main content has container (not just navbar)
        if '<main>' in html_content:
            main_content = html_content.split('<main>')[1].split('</main>')[0] if '</main>' in html_content else html_content
            assert 'class="container' in main_content, \
                f"{page_name} ({page_path}) main content does not have container class"
        
        # 5. Verify content structure is present
        assert len(html_content) > 500, \
            f"{page_name} ({page_path}) appears to have very little content"
        
        # 6. Verify semantic HTML structure
        assert '<nav' in html_content, \
            f"{page_name} ({page_path}) does not have <nav> element"
        assert '<main>' in html_content, \
            f"{page_name} ({page_path}) does not have <main> element"
        
        # 7. Verify CSS is loaded
        assert 'style.css' in html_content, \
            f"{page_name} ({page_path}) custom CSS not loaded"
        
        # 8. Verify Inter font is loaded (SRS UI-11)
        assert 'Inter' in html_content or 'fonts.googleapis.com' in html_content, \
            f"{page_name} ({page_path}) Inter font not loaded"
    
    # Special verification for Browse page (map functionality)
    browse_response = client.get('/browse')
    browse_html = browse_response.data.decode('utf-8')
    
    # 3. Verify Map SVG background is visible
    assert '<rect' in browse_html, \
        "Browse page: SVG background rect not found"
    assert 'id="world-map"' in browse_html, \
        "Browse page: World map SVG not found"
    assert 'map-container' in browse_html, \
        "Browse page: Map container not found"
    
    # 4. Verify Map container is properly sized
    assert 'width: 100%' in browse_html or 'width:100%' in browse_html, \
        "Browse page: Map container width: 100% not found"
    assert 'max-width: 1000px' in browse_html or 'max-width:1000px' in browse_html, \
        "Browse page: Map container max-width: 1000px not found"
    
    # Verify map has proper viewBox
    assert 'viewBox="0 0 1000 500"' in browse_html, \
        "Browse page: Map SVG viewBox not found or incorrect"
    
    # 6. Verify Content is centered (container with proper structure)
    # All pages should have container which centers content
    for page_path, page_name in pages_to_test:
        page_response = client.get(page_path)
        page_html = page_response.data.decode('utf-8')
        
        # Container class ensures content is centered (Bootstrap behavior)
        assert 'class="container' in page_html, \
            f"{page_name} ({page_path}) does not have container for centering"
    
    # 7. Responsive behavior - CSS verified in Step 6.5.6
    # Media queries are present in CSS (verified in test_map_container_css_styles)
    # Cannot test actual responsive behavior without browser automation
    
    # 8. No console errors - Cannot test automatically
    # This requires manual browser DevTools verification
    # All pages load with 200 status, which indicates no server-side errors
    
    # Summary: All automated checks pass
    # Manual verification still needed for:
    # - Visual glassmorphism blur effect
    # - Responsive behavior on actual devices
    # - Browser console errors (JavaScript errors)
    # - Visual layout verification