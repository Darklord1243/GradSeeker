// Interactive Pixel World Map JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Available countries - IDs match the <g> group IDs in the SVG
    const availableCountries = ['japan', 'ireland', 'usa', 'singapore', 'hong-kong'];
    
    // Country display names and slugs
    const countryData = {
        'usa': { name: 'United States of America', slug: 'usa' },
        'ireland': { name: 'Ireland', slug: 'ireland' },
        'japan': { name: 'Japan', slug: 'japan' },
        'singapore': { name: 'Singapore', slug: 'singapore' },
        'hong-kong': { name: 'Hong Kong', slug: 'hong-kong' }
    };
    
    // Initialize map
    initializePixelMap();
    
    /**
     * Initialize the pixel-based world map
     */
    function initializePixelMap() {
        setupClickHandlers();
        setupKeyboardNavigation();
        setupTooltips();
        setupTextFallback();
        setupTouchEvents();
        setupAriaLabels();
    }
    
    /**
     * Setup click handlers for country pixel groups
     */
    function setupClickHandlers() {
        availableCountries.forEach(function(countryId) {
            const group = document.getElementById(countryId);
            if (group) {
                // Click handler for the entire group
                group.addEventListener('click', function(e) {
                    e.preventDefault();
                    navigateToCountry(countryId);
                });
                
                // Also handle clicks on hitbox elements
                const hitbox = group.querySelector('.country-hitbox');
                if (hitbox) {
                    hitbox.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        navigateToCountry(countryId);
                    });
                }
            }
        });
    }
    
    /**
     * Navigate to country's universities page
     */
    function navigateToCountry(countryId) {
        const data = countryData[countryId];
        if (data) {
            // Add visual feedback
            const group = document.getElementById(countryId);
            if (group) {
                group.classList.add('clicked');
            }
            
            // Navigate after a brief delay for visual feedback
            setTimeout(function() {
                window.location.href = '/browse/' + data.slug;
            }, 150);
        }
    }
    
    /**
     * Setup keyboard navigation for accessibility (WCAG 2.1 Level AA)
     */
    function setupKeyboardNavigation() {
        availableCountries.forEach(function(countryId) {
            const group = document.getElementById(countryId);
            if (group) {
                // Make group focusable
                group.setAttribute('tabindex', '0');
                group.setAttribute('role', 'button');
                
                // Keyboard event handler
                group.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        navigateToCountry(countryId);
                    }
                });
            }
        });
    }
    
    /**
     * Setup ARIA labels for screen reader support
     */
    function setupAriaLabels() {
        availableCountries.forEach(function(countryId) {
            const group = document.getElementById(countryId);
            if (group) {
                const data = countryData[countryId];
                if (data) {
                    group.setAttribute('aria-label', 'Select ' + data.name + ' to browse universities');
                    
                    // Link to instructions
                    const instructions = document.getElementById('map-instructions');
                    if (instructions) {
                        group.setAttribute('aria-describedby', 'map-instructions');
                    }
                }
            }
        });
        
        // Set up SVG container ARIA
        const worldMap = document.getElementById('world-map');
        if (worldMap) {
            worldMap.setAttribute('role', 'application');
            worldMap.setAttribute('aria-label', 'Interactive pixel world map for country selection');
        }
    }
    
    /**
     * Setup tooltips for country hover
     */
    function setupTooltips() {
        const tooltip = document.getElementById('map-tooltip');
        if (!tooltip) return;
        
        const tooltipName = tooltip.querySelector('.tooltip-name');
        
        availableCountries.forEach(function(countryId) {
            const group = document.getElementById(countryId);
            if (group) {
                // Mouse enter - show tooltip
                group.addEventListener('mouseenter', function(e) {
                    const data = countryData[countryId];
                    if (data && tooltipName) {
                        tooltipName.textContent = data.name;
                        tooltip.classList.add('visible');
                        tooltip.setAttribute('aria-hidden', 'false');
                        positionTooltip(e, tooltip);
                    }
                });
                
                // Mouse move - update tooltip position
                group.addEventListener('mousemove', function(e) {
                    positionTooltip(e, tooltip);
                });
                
                // Mouse leave - hide tooltip
                group.addEventListener('mouseleave', function() {
                    tooltip.classList.remove('visible');
                    tooltip.setAttribute('aria-hidden', 'true');
                });
            }
        });
    }
    
    /**
     * Position tooltip near cursor
     */
    function positionTooltip(e, tooltip) {
        const container = document.querySelector('.map-container');
        if (!container) return;
        
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left + 15;
        const y = e.clientY - rect.top - 10;
        
        // Keep tooltip within container bounds
        const tooltipRect = tooltip.getBoundingClientRect();
        const maxX = rect.width - tooltipRect.width - 20;
        const maxY = rect.height - tooltipRect.height - 20;
        
        tooltip.style.left = Math.min(x, maxX) + 'px';
        tooltip.style.top = Math.min(Math.max(y, 10), maxY) + 'px';
    }
    
    /**
     * Setup text-based fallback dropdown
     */
    function setupTextFallback() {
        const countrySelect = document.getElementById('country-select');
        if (!countrySelect) return;
        
        countrySelect.addEventListener('change', function() {
            const selectedSlug = this.value;
            if (selectedSlug) {
                window.location.href = '/browse/' + selectedSlug;
            }
        });
    }
    
    /**
     * Setup touch events for mobile
     */
    function setupTouchEvents() {
        availableCountries.forEach(function(countryId) {
            const group = document.getElementById(countryId);
            if (group) {
                let touchStartTime = 0;
                let touchStartX = 0;
                let touchStartY = 0;
                let hasMoved = false;
                
                // Touch start
                group.addEventListener('touchstart', function(e) {
                    touchStartTime = Date.now();
                    if (e.touches.length > 0) {
                        touchStartX = e.touches[0].clientX;
                        touchStartY = e.touches[0].clientY;
                    }
                    hasMoved = false;
                    
                    // Visual feedback
                    group.classList.add('touching');
                }, { passive: true });
                
                // Touch move - detect scrolling
                group.addEventListener('touchmove', function(e) {
                    if (e.touches.length > 0) {
                        const deltaX = Math.abs(e.touches[0].clientX - touchStartX);
                        const deltaY = Math.abs(e.touches[0].clientY - touchStartY);
                        if (deltaX > 10 || deltaY > 10) {
                            hasMoved = true;
                        }
                    }
                }, { passive: true });
                
                // Touch end - trigger navigation if it was a tap
                group.addEventListener('touchend', function(e) {
                    const touchDuration = Date.now() - touchStartTime;
                    
                    // Remove visual feedback
                    group.classList.remove('touching');
                    
                    // Only navigate if it was a quick tap without movement
                    if (touchDuration < 500 && !hasMoved) {
                        e.preventDefault();
                        navigateToCountry(countryId);
                    }
                }, { passive: false });
                
                // Touch cancel
                group.addEventListener('touchcancel', function() {
                    group.classList.remove('touching');
                    hasMoved = false;
                });
            }
        });
        
        // Also handle hitbox touch events for small countries
        availableCountries.forEach(function(countryId) {
            const group = document.getElementById(countryId);
            if (group) {
                const hitbox = group.querySelector('.country-hitbox');
                if (hitbox) {
                    hitbox.addEventListener('touchend', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        navigateToCountry(countryId);
                    }, { passive: false });
                }
            }
        });
    }
});
