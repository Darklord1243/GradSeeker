from werkzeug.security import generate_password_hash, check_password_hash


def country_to_slug(country_name):
    """
    Convert a country name to a slug.
    """
    if not country_name:
        return ""
    return country_name.lower().replace(" ", "-")


def slug_to_country(slug, available_countries):
    """
    Convert a URL slug back to a country name by matching against
    available countries.
    """
    if not slug or not available_countries:
        return None

    slug_lower = slug.lower()
    for country in available_countries:
        if country_to_slug(country) == slug_lower:
            return country

    return None


def hash_password(password):
    """
    Hash a password using werkzeug's secure password hashing.
    """
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """
    Verify a password against its hash.
    """
    return check_password_hash(password_hash, password)


def get_logo_url(university):
    """
    Get the logo URL for a university, handling both local and external images.
    """
    if not university or not university.logo_url:
        return None

    logo_url = university.logo_url.strip()

    if logo_url.startswith(('http://', 'https://')):
        return logo_url

    try:
        from flask import url_for
        return url_for('static', filename=f'images/logos/{logo_url}')
    except RuntimeError:
        return f'/static/images/logos/{logo_url}'
