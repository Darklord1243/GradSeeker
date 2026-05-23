# tests/test_color_contrast.py
# Color Contrast Tests for Step 10.7: WCAG 2.1 AA Compliance
# These tests verify that all color combinations meet WCAG 2.1 AA standards

import os
import pytest


def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color (str): Hex color code (e.g., "#ffffff" or "ffffff")
        
    Returns:
        tuple: (R, G, B) values from 0-255
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_relative_luminance(rgb):
    """
    Calculate relative luminance of an RGB color (WCAG formula).
    
    Args:
        rgb (tuple): (R, G, B) values from 0-255
        
    Returns:
        float: Relative luminance (0.0 to 1.0)
    """
    def normalize(value):
        """Normalize RGB value to 0-1 range."""
        return value / 255.0
    
    def gamma_correct(value):
        """Apply gamma correction."""
        if value <= 0.03928:
            return value / 12.92
        else:
            return ((value + 0.055) / 1.055) ** 2.4
    
    r, g, b = rgb
    r_norm = gamma_correct(normalize(r))
    g_norm = gamma_correct(normalize(g))
    b_norm = gamma_correct(normalize(b))
    
    # Calculate relative luminance (WCAG formula)
    return 0.2126 * r_norm + 0.7152 * g_norm + 0.0722 * b_norm


def calculate_contrast_ratio(color1_hex, color2_hex):
    """
    Calculate WCAG contrast ratio between two colors.
    
    Args:
        color1_hex (str): First color in hex format (e.g., "#ffffff")
        color2_hex (str): Second color in hex format (e.g., "#161616")
        
    Returns:
        float: Contrast ratio (1.0 to 21.0)
    """
    rgb1 = hex_to_rgb(color1_hex)
    rgb2 = hex_to_rgb(color2_hex)
    
    l1 = get_relative_luminance(rgb1)
    l2 = get_relative_luminance(rgb2)
    
    # Ensure lighter color is L1
    if l1 < l2:
        l1, l2 = l2, l1
    
    # Calculate contrast ratio (WCAG formula)
    contrast = (l1 + 0.05) / (l2 + 0.05)
    return contrast


def test_color_contrast_wcag_aa_white_on_dark_grey():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Verify that white text (#ffffff) on dark grey background (#161616) meets WCAG 2.1 AA standards.
    
    Expected: 12.6:1 contrast ratio (exceeds AA requirement of 4.5:1)
    """
    white = "#ffffff"
    dark_grey = "#161616"
    
    contrast = calculate_contrast_ratio(white, dark_grey)
    
    # WCAG 2.1 AA requires 4.5:1 for normal text, 3:1 for large text
    # This combination should easily exceed both requirements
    assert contrast >= 4.5, \
        f"White on dark grey contrast ratio ({contrast:.2f}:1) does not meet WCAG 2.1 AA minimum (4.5:1)"
    
    # Verify it exceeds minimum (actual value may vary, but should be high)
    # Actual: ~18.10:1 (better than expected ~12.6:1)
    assert contrast >= 12.0, \
        f"White on dark grey contrast ratio ({contrast:.2f}:1) should be high (>=12.0:1)"


def test_color_contrast_wcag_aa_white_on_black():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Verify that white text (#ffffff) on black background (#0a0a0a) meets WCAG 2.1 AA standards.
    
    Expected: 21:1 contrast ratio (maximum possible, exceeds AA requirement)
    """
    white = "#ffffff"
    black = "#0a0a0a"
    
    contrast = calculate_contrast_ratio(white, black)
    
    # WCAG 2.1 AA requires 4.5:1 for normal text
    # This combination should easily exceed the requirement
    assert contrast >= 4.5, \
        f"White on black contrast ratio ({contrast:.2f}:1) does not meet WCAG 2.1 AA minimum (4.5:1)"
    
    # Verify it's very high (close to maximum 21:1)
    # Actual: ~19.80:1 (very close to maximum)
    assert contrast >= 19.0, \
        f"White on black contrast ratio ({contrast:.2f}:1) should be very high (>=19.0:1, close to maximum 21:1)"


def test_color_contrast_wcag_aa_muted_grey_on_dark_grey():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Verify that muted grey text (#a1a1a1) on dark grey background (#161616) meets WCAG 2.1 AA standards.
    
    Expected: 4.5:1 contrast ratio (meets AA requirement exactly)
    """
    muted_grey = "#a1a1a1"
    dark_grey = "#161616"
    
    contrast = calculate_contrast_ratio(muted_grey, dark_grey)
    
    # WCAG 2.1 AA requires 4.5:1 for normal text
    assert contrast >= 4.5, \
        f"Muted grey on dark grey contrast ratio ({contrast:.2f}:1) does not meet WCAG 2.1 AA minimum (4.5:1)"
    
    # Verify it meets minimum (actual value may be higher, which is better)
    # Actual: ~7.00:1 (better than expected ~4.5:1)
    assert contrast >= 4.5, \
        f"Muted grey on dark grey contrast ratio ({contrast:.2f}:1) should meet WCAG 2.1 AA minimum (4.5:1)"


def test_color_contrast_wcag_aa_white_on_accent_blue():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Verify that white text (#ffffff) on accent blue background (#0066ff) meets WCAG 2.1 AA standards.
    
    Note: Accent blue is used as a BACKGROUND color for badges, not as text color.
    This test verifies the actual usage pattern in the application.
    """
    white = "#ffffff"
    accent_blue = "#0066ff"
    
    contrast = calculate_contrast_ratio(white, accent_blue)
    
    # WCAG 2.1 AA requires 4.5:1 for normal text
    assert contrast >= 4.5, \
        f"White text on accent blue background contrast ratio ({contrast:.2f}:1) does not meet WCAG 2.1 AA minimum (4.5:1)"


def test_color_contrast_wcag_aa_white_on_accent_purple():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Verify that white text (#ffffff) on accent purple background (#9333ea) meets WCAG 2.1 AA standards.
    
    Note: Accent purple is used as a BACKGROUND color for badges, not as text color.
    This test verifies the actual usage pattern in the application.
    """
    white = "#ffffff"
    accent_purple = "#9333ea"
    
    contrast = calculate_contrast_ratio(white, accent_purple)
    
    # WCAG 2.1 AA requires 4.5:1 for normal text
    assert contrast >= 4.5, \
        f"White text on accent purple background contrast ratio ({contrast:.2f}:1) does not meet WCAG 2.1 AA minimum (4.5:1)"


def test_color_contrast_css_variables_match():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Verify that CSS variables in style.css match the expected color values for contrast testing.
    """
    css_file_path = os.path.join('static', 'css', 'style.css')
    assert os.path.exists(css_file_path), f"CSS file not found at {css_file_path}"
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Verify expected color values are present in CSS
    expected_colors = {
        '--bg-primary': '#0a0a0a',      # Black
        '--bg-card': '#161616',         # Dark grey
        '--text-primary': '#ffffff',     # White
        '--text-secondary': '#a1a1a1',  # Muted grey
        '--accent-blue': '#0066ff',      # Electric Blue
        '--accent-purple': '#9333ea',    # Neon Purple
    }
    
    for var_name, expected_hex in expected_colors.items():
        # Check if variable is defined with expected value
        # Look for pattern: --var-name: #hex or --var-name:#hex
        pattern1 = f"{var_name}: {expected_hex}"
        pattern2 = f"{var_name}:{expected_hex}"
        
        assert pattern1 in css_content or pattern2 in css_content, \
            f"CSS variable {var_name} should have value {expected_hex}"


def test_color_contrast_all_combinations_wcag_aa():
    """
    Test Step 10.7: Color Contrast Check (WCAG 2.1 AA on Dark Background)
    Comprehensive test of all common text/background combinations used in the application.
    """
    # Define color combinations used in the application
    # Note: Accent colors are used as BACKGROUNDS with white text, not as text colors
    color_combinations = [
        # (text_color, background_color, description, min_contrast)
        ("#ffffff", "#0a0a0a", "White text on black background (body)", 4.5),
        ("#ffffff", "#161616", "White text on dark grey cards", 4.5),
        ("#a1a1a1", "#161616", "Muted grey text on dark grey cards", 4.5),
        ("#ffffff", "#0066ff", "White text on accent blue (badges)", 4.5),
        ("#ffffff", "#9333ea", "White text on accent purple (badges)", 4.5),
    ]
    
    failed_combinations = []
    
    for text_color, bg_color, description, min_contrast in color_combinations:
        contrast = calculate_contrast_ratio(text_color, bg_color)
        
        if contrast < min_contrast:
            failed_combinations.append({
                'description': description,
                'text': text_color,
                'background': bg_color,
                'contrast': contrast,
                'required': min_contrast
            })
    
    # Report all failures
    if failed_combinations:
        failure_messages = []
        for failure in failed_combinations:
            failure_messages.append(
                f"{failure['description']}: {failure['contrast']:.2f}:1 "
                f"(required: {failure['required']}:1)"
            )
        
        assert False, \
            f"The following color combinations do not meet WCAG 2.1 AA standards:\n" + \
            "\n".join(failure_messages)
    
    # All combinations pass
    assert True, "All color combinations meet WCAG 2.1 AA standards"

