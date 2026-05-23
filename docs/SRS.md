# Software Requirements Specification (SRS)
## GradSeeker - A "Shopping Platform" for Master's Degrees

**Version:** 1.0  
**Date:** 12.10  
**Author:** LIN YUHAO
**Target Deadline:** December 31, 2025

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document describes the functional and non-functional requirements for **GradSeeker**, a web application designed as a "Shopping Platform" for Master's Degrees with an algorithmic Compatibility Calculator. The platform helps prospective graduate students discover, shortlist, and evaluate compatibility with graduate programs worldwide.

### 1.2 Core Concept
GradSeeker functions as a shopping platform where:
- **Users** are "Shoppers" who browse and save programs
- **Programs** are "Products" with requirements as "Prices"
- **Universities** are "Brands" that offer multiple programs
- **Shortlist** is the "Shopping Cart" (many-to-many relationship)
- **Compatibility Calculator** is the advanced algorithmic feature that matches user profiles to program requirements

### 1.3 Scope
GradSeeker is a Flask-based web application that allows users to:
- Browse graduate programs using a hierarchical structure (Country → University → Program)
- Create user accounts and maintain profiles with academic credentials ("The Wallet")
- Shortlist programs of interest (many-to-many relationship via "Shopping Cart")
- Calculate compatibility scores between user profiles and program requirements using an intelligent algorithm
- View personalized compatibility ratings on program detail pages and user dashboard

### 1.3 Definitions, Acronyms, and Abbreviations
- **SRS**: Software Requirements Specification
- **GPA**: Grade Point Average
- **TOEFL**: Test of English as a Foreign Language
- **WCAG**: Web Content Accessibility Guidelines
- **AJAX**: Asynchronous JavaScript and XML

### 1.4 References
- Assessment Brief: XJCO2011 Web Application - Final Assessment
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/

---

## 2. Overall Description

### 2.1 Product Perspective
GradSeeker is a standalone web application built using:
- **Backend**: Python 3.10+ (Flask Framework)
- **Database**: SQLite (Local Development), SQLAlchemy (ORM)
- **Frontend**: HTML5, Jinja2 Templates, Bootstrap 5 (for Responsive Design & WCAG Accessibility)
- **Authentication**: Flask-Login
- **Deployment**: PythonAnywhere

### 2.2 Product Functions
The system provides the following major functions:
1. User authentication and profile management ("The Wallet" - academic credentials)
2. Hierarchical program browsing (Country → University → Program)
3. Program shortlisting via "Shopping Cart" (many-to-many relationship)
4. Compatibility calculation algorithm (Advanced Feature)
5. University and program information display
6. User Dashboard displaying shortlisted programs with compatibility scores
7. Responsive, accessible web interface

### 2.3 User Classes and Characteristics
- **Prospective Students**: Primary users who search for and shortlist graduate programs
- **Administrators**: (Future) Users who manage program data

### 2.4 Operating Environment
- Web browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for desktop, tablet, and mobile devices
- PythonAnywhere hosting environment

### 2.5 Design and Implementation Constraints
- Must comply with WCAG accessibility standards
- All JavaScript and CSS must be in separate files. The application must implement custom CSS variables (root scope) to override default framework styling, specifically for the dark mode color palette.
- Cannot use software/services to generate layout code
- Must use a many-to-many relationship meaningfully
- Must implement an advanced feature (complex algorithm or AJAX)

---

## 3. System Features

### 3.1 User Authentication System
**Priority:** High

#### 3.1.1 Description
Users must be able to register, log in, and log out of the system securely.

#### 3.1.2 Functional Requirements
- **FR-01**: Users must register with a username and password
- **FR-1.1**: System shall allow users to register with username and password
- **FR-1.2**: System shall validate username uniqueness
- **FR-1.3**: System shall hash passwords before storage (using secure hashing algorithm)
- **FR-1.4**: System shall allow users to log in with username and password
- **FR-1.5**: System shall maintain user session state
- **FR-1.6**: System shall allow users to log out

#### 3.1.3 User Profile Management ("The Wallet")
- **FR-02**: Upon registration (or immediately after), the user must complete their profile (GPA, TOEFL, Experience) to activate the "Calculator"
- **FR-1.7**: Users shall be able to view their dashboard/profile
- **FR-1.8**: Users shall be able to edit their academic credentials ("The Wallet"):
  - GPA (Grade Point Average) - Float, e.g., 3.58
  - TOEFL score - Integer, e.g., 104
  - Internship experience - Integer (months), e.g., 6
  - Research papers count - Integer, e.g., 2

### 3.2 Program Browsing System (The "Shop" Flow)
**Priority:** High

#### 3.2.1 Description
Users browse graduate programs using a hierarchical structure. The "Browse" page should not list every program at once, but instead guide users through a structured navigation flow. The country selection is enhanced with an interactive world map visualization for improved user engagement.

#### 3.2.2 Functional Requirements
- **FR-03**: Hierarchy View - The browsing system must follow a three-step hierarchical structure:
  - **Step 1**: User selects Country (Filter: Japan / Ireland / USA / Singapore / Hong Kong)
    - **FR-3.1**: System shall display an interactive world map on the Browse page
    - **FR-3.2**: Available countries (Japan, Ireland, USA, Singapore, Hong Kong) shall be visually highlighted/clickable on the map
    - **FR-3.3**: Users shall be able to click on highlighted countries on the map to proceed to Step 2
    - **FR-3.4**: System shall provide an alternative text-based country selection (dropdown/list) for accessibility (WCAG requirement)
    - **FR-3.5**: Map interaction shall be keyboard accessible (Tab navigation, Enter/Space to select)
    - **FR-3.6**: Map regions shall have proper ARIA labels for screen readers
    - **FR-3.7**: Map shall be responsive and work on mobile devices (touch-friendly)
  - **Step 2**: User sees a list of Universities in that country
  - **Step 3**: User clicks a University to see its Programs
- **FR-2.1**: System shall display available graduate programs in the selected hierarchy
- **FR-2.2**: System shall display program details including:
  - Program name (e.g., "MSc Creative Informatics")
  - University name and country
  - Category (CS, AI, Data Science, Engineering, etc.)
  - Minimum GPA requirement ("The Price")
  - Minimum TOEFL requirement ("The Price")
  - Tuition fee (String format, e.g., "535,800 JPY/year")
  - Application deadline
  - Research focus indicator (Boolean)
  - Industry focus indicator (Boolean)
- **FR-2.3**: System shall allow navigation through the hierarchy (Country → University → Program)
- **FR-2.4**: System shall display university information including QS ranking and logo
- **FR-04**: Pre-Populated Data - The database must be seeded via a script (`load_data.py`) reading from a CSV file (`universities.csv`), so the shop is not empty

### 3.3 Program Shortlisting (The "Shopping Cart" - Many-to-Many Relationship)
**Priority:** High

#### 3.3.1 Description
Users can shortlist multiple programs, and programs can be shortlisted by multiple users. This many-to-many relationship functions as a "Shopping Cart" where users save programs to their personal dashboard. This relationship enhances user experience by allowing personalized program collections and enabling the compatibility calculator to work across all shortlisted items.

#### 3.3.2 Functional Requirements
- **FR-06**: On any Program card, there must be an "Add to List" button
- **FR-3.1**: Authenticated users shall be able to add programs to their shortlist (Shopping Cart)
- **FR-3.2**: System shall prevent duplicate shortlist entries
- **FR-07**: The User Dashboard must display a table of all shortlisted programs
- **FR-3.3**: Users shall be able to view their shortlisted programs on their Dashboard
- **FR-08**: Users can remove items from their shortlist
- **FR-3.4**: Users shall be able to remove programs from their shortlist
- **FR-3.5**: System shall track the date when a program was added to shortlist
- **FR-3.6**: System shall display compatibility scores for shortlisted programs on the Dashboard

#### 3.3.3 Business Value
The many-to-many relationship (Shopping Cart) enables:
- Personalized program collections per user
- Compatibility calculations for all saved programs
- Analytics on popular programs (future feature)
- Comparison features between shortlisted programs
- User-specific recommendations
- Enhanced user experience similar to e-commerce platforms

### 3.4 Compatibility Calculator (Advanced Feature)
**Priority:** High

#### 3.4.1 Description
An intelligent algorithmic feature that calculates compatibility between a user's profile ("The Wallet") and program requirements ("The Price"), providing personalized recommendations. This is the primary advanced feature that demonstrates 2nd year programming skills through complex Python logic.

**Note:** The interactive world map (Section 3.2.2) also contributes to demonstrating advanced JavaScript skills, as it requires custom JavaScript implementation for map interaction, click handling, and accessibility features (not solely library code).

#### 3.4.2 Functional Requirements
- **FR-05**: The system must implement a Python method `calculate_compatibility(user, program)` that returns a status and a color code
- **FR-4.1**: System shall calculate compatibility score based on:
  - User GPA vs. Program minimum GPA requirement (Hard Requirement)
  - User TOEFL score vs. Program minimum TOEFL requirement (Hard Requirement)
  - User research papers vs. Program research focus (Soft Power)
  - User internship experience vs. Program industry focus (Soft Power)
- **FR-4.2**: System shall categorize compatibility as:
  - "Safe / High Chance" - Green indicator
  - "Target / Medium Chance" - Yellow indicator
  - "Reach / Low Chance" - Red indicator
- **FR-4.3**: Compatibility score shall be displayed on program detail pages
- **FR-4.4**: Compatibility score shall be displayed in user's Dashboard (shortlist view)

#### 3.4.3 Algorithm Logic (Python Implementation)
The algorithm uses a scoring system with the following Python logic:

```python
def calculate_compatibility(user, program):
    """
    Calculates compatibility score between user profile and program requirements.
    Returns: (status_string, color_class)
    """
    score = 0
    
    # Hard Requirements (GPA/TOEFL)
    if user.gpa >= program.min_gpa:
        score += 2
    elif user.gpa >= program.min_gpa - 0.2:
        score += 1  # Close enough
    
    if user.toefl_score >= program.min_toefl:
        score += 1
    
    # Soft Power (Research/Internship)
    if program.research_focus and user.research_papers > 0:
        score += 2  # Huge bonus for research programs
    if program.industry_focus and user.internship_exp >= 3:
        score += 1  # Bonus for applied programs
    
    # Result Thresholds
    if score >= 4:
        return "Safe / High Chance", "success"  # Green
        # Alternative return format: "High Chance (Safe)", "success"
    elif score >= 2:
        return "Target / Medium Chance", "warning"  # Yellow
        # Alternative return format: "Moderate Chance (Target)", "warning"
    else:
        return "Reach / Low Chance", "danger"  # Red
        # Alternative return format: "Low Chance (Reach)", "danger"
```

**Scoring Breakdown:**
- Hard requirements (GPA, TOEFL): Base score (0-3 points)
- Soft requirements (research papers, internships): Bonus points (0-3 points)
- Total possible score: 0-6 points
- Final score determines compatibility category

### 3.5 UI/UX & Accessibility Requirements (WCAG)
**Priority:** High

#### 3.5.1 Description
The application must be accessible and usable across devices and for users with disabilities. The user interface shall adopt an 'Immersive Cinematic' (Dark Mode) aesthetic, inspired by modern media discovery platforms (e.g., Flim.ai, Netflix). This design choice emphasizes visual hierarchy and reduces eye strain during long browsing sessions. While visually rich, the design must strictly maintain high contrast ratios to remain WCAG 2.1 AA compliant.

#### 3.5.2 Functional Requirements
- **UI-01**: Navigation Bar must be consistent on all pages (horizontal navbar recommended for accessibility)
- **UI-02**: Colors for "Safe/Reach" status must be color-blind friendly (use Text Labels + Color, not color alone)
- **UI-03**: All images (University Logos) must have alt tags described in the database
- **UI-04**: The layout must use Bootstrap "Cards" or "Tables" that resize for mobile devices
- **UI-05**: Interactive world map must have keyboard navigation support (Tab, Enter, Space keys)
- **UI-06**: Interactive world map must have ARIA labels and roles for screen reader compatibility
- **UI-07**: Interactive world map must provide a text-based alternative (dropdown/list) for users who cannot interact with the map
- **UI-08**: Cinematic Dark Theme. The application shall utilize a deep matte black background (e.g., #0a0a0a) with dark grey cards (#161616), departing from standard light-themed academic tools.
- **UI-09**: Borderless Card Design. Program and University elements shall be displayed in borderless cards that utilize shadow depth and hover states (translation/glow) to indicate interactivity, rather than traditional borders.
- **UI-10**: Glassmorphism Navigation. The navigation bar shall employ a semi-transparent, backdrop-blur effect (backdrop-filter: blur) to maintain context while scrolling.
- **UI-11**: Typography Hierarchy. The application shall use modern Sans-Serif typography (e.g., 'Inter') with clear weight distinctions: Bold White (#ffffff) for headings and Medium Muted Grey (#a1a1a1) for metadata.
- **UI-12**: Visual Focus. Key call-to-action elements (e.g., "Compatibility Badges") shall use vibrant accent colors (Electric Blue, Neon Purple) to guide user attention against the dark background.
- **FR-5.1**: System shall be responsive on desktop, tablet, and mobile devices
- **FR-5.2**: System shall comply with WCAG 2.1 Level AA standards
- **FR-5.3**: All images shall have alt text (stored in database logo_url descriptions)
- **FR-5.4**: Navigation shall be keyboard accessible
- **FR-5.5**: Color contrast shall meet WCAG standards
- **FR-5.6**: Forms shall have proper labels and error messages
- **FR-5.7**: System shall use semantic HTML elements
- **FR-5.8**: Interactive map elements shall be focusable and have visible focus indicators

---

## 4. Database Requirements

### 4.1 Database Schema

#### 4.1.1 User Model (The Shopper)
- `id` (Integer, Primary Key): Unique ID
- `username` (String, Unique, Not Null): For login
- `password` (String, Not Null): Hashed password (Security) - should be hashed using secure hashing algorithm (e.g., bcrypt) before storage
- **Profile Stats ("The Wallet"):**
  - `gpa` (Float, Default: 0.0): e.g., 3.58
  - `toefl_score` (Integer, Default: 0): e.g., 104
  - `internship_exp` (Integer, Default: 0): Months of internship experience
  - `research_papers` (Integer, Default: 0): Number of published papers/posters

#### 4.1.2 University Model (The Brand)
- `id` (Integer, Primary Key): Unique ID
- `name` (String, Unique, Not Null): e.g., "The University of Tokyo"
- `country` (String, Not Null): e.g., "Japan"
- `qs_rank` (Integer): e.g., 28
- `logo_url` (String): URL to image
- **Relationship**: One-to-Many with Program

#### 4.1.3 Program Model (The Product)
- `id` (Integer, Primary Key): Unique ID
- `university_id` (Integer, Foreign Key): Links to University
- `name` (String, Not Null): e.g., "MSc Creative Informatics"
- `category` (String): e.g., "CS", "AI", "Data Science"
- **The Price (Requirements):**
  - `min_gpa` (Float, Not Null): e.g., 3.2
  - `min_toefl` (Integer, Default: 0): e.g., 90
  - `tuition_fee` (String): e.g., "535,800 JPY/year"
  - `research_focus` (Boolean, Default: False): True if it heavily favors research exp.
  - `industry_focus` (Boolean, Default: False): True if it favors internship exp.
- **Relationship**: Many-to-Many with User (via Shortlist)
- **Additional Fields for Future Web Mining (V2.0):**
  - `source_url` (String): The specific URL of the department's admission page. Purpose: To allow a future web scraper to visit the site and check for updates.
  - `last_updated` (DateTime): Timestamp of when the data was last verified. Purpose: To flag "stale" information that needs re-checking.

#### 4.1.4 Shortlist Association Table (The Shopping Cart - Many-to-Many)
- **Type**: Association Table (Many-to-Many)
- `user_id` (Integer, Foreign Key → User, Primary Key): Links to User
- `program_id` (Integer, Foreign Key → Program, Primary Key): Links to Program
- `date_added` (DateTime, Auto-generated): Timestamp when program was added
- **Purpose**: Allows users to "save" programs to their personal dashboard (Shopping Cart functionality)

### 4.2 Data Pre-population
- **FR-04**: Pre-Populated Data - The database must be seeded via a script (`load_data.py`) reading from a CSV file (`universities.csv`), so the shop is not empty
- **FR-6.1**: Database shall be pre-populated with university data from CSV
- **FR-6.2**: Database shall be pre-populated with program data from CSV
- **FR-6.3**: Pre-population script (`load_data.py`) shall be provided for setup
- **FR-6.4**: CSV file (`universities.csv`) must contain at least 5 rows of data (universities and programs)
- **FR-6.5**: The hierarchical structure (Country → University → Program) must be maintained in the data

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- **NFR-1**: Page load time shall be under 3 seconds
- **NFR-2**: Database queries shall be optimized

### 5.2 Security Requirements
- **NFR-3**: Passwords shall be hashed using secure hashing algorithm (e.g., bcrypt)
- **NFR-4**: User sessions shall be managed securely
- **NFR-5**: SQL injection prevention via ORM
- **NFR-6**: XSS prevention through proper input sanitization
- **NFR-7**: CSRF protection for forms

### 5.3 Usability Requirements
- **NFR-8**: Interface shall be intuitive and easy to navigate
- **NFR-9**: Consistent horizontal navbar across all pages
- **NFR-10**: Clear error messages for user actions
- **NFR-15**: Visual Engagement. The interface shall prioritize "Visual Discovery" by using distinct University logos and spacious layouts, ensuring the platform feels like a discovery tool rather than a spreadsheet.

### 5.4 Reliability Requirements
- **NFR-11**: System shall handle errors gracefully
- **NFR-12**: Database transactions shall maintain data integrity

### 5.5 Deployment Requirements
- **NFR-13**: Application shall be deployed on PythonAnywhere
- **NFR-14**: Deployed site shall remain live for at least 3 weeks after submission

---

## 6. User Stories

### 6.1 Authentication
- **US-1**: As a prospective student, I want to create an account so that I can save my preferences
- **US-2**: As a user, I want to log in so that I can access my shortlisted programs
- **US-3**: As a user, I want to update my academic credentials so that compatibility scores are accurate

### 6.2 Program Discovery
- **US-4**: As a user, I want to browse all available programs so that I can discover options
- **US-5**: As a user, I want to filter programs by university/country so that I can find relevant options
- **US-6**: As a user, I want to see program details so that I can make informed decisions

### 6.3 Shortlisting
- **US-7**: As a user, I want to shortlist programs so that I can track my favorites
- **US-8**: As a user, I want to view my shortlist so that I can review my options
- **US-9**: As a user, I want to remove programs from my shortlist so that I can manage my list

### 6.4 Compatibility
- **US-10**: As a user, I want to see compatibility scores so that I know my chances of admission
- **US-11**: As a user, I want compatibility scores updated when I change my profile

---

## 7. System Architecture

### 7.1 Technology Stack
- **Backend Framework**: Flask
- **Database ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript
- **CSS Framework**: Bootstrap (partial use, custom CSS required)
- **Deployment**: PythonAnywhere

### 7.2 Project Structure
```
GradSeeker/
├── app.py                 # Main Flask application
├── models.py              # Database models (User, University, Program, Shortlist)
├── load_data.py           # Script to populate database from CSV
├── universities.csv       # Data file with university and program information
├── static/
│   ├── css/
│   │   └── style.css     # Custom CSS (Bootstrap 5 + custom styles)
│   └── js/
│       ├── main.js       # Custom JavaScript (general functionality)
│       └── map.js        # Interactive world map JavaScript (custom implementation)
├── templates/
│   ├── base.html         # Base template with consistent navbar
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard (profile + shortlist)
│   ├── browse.html       # Browse by country
│   ├── universities.html # Universities in selected country
│   ├── programs.html     # Programs for selected university
│   └── program_detail.html # Program details with compatibility score
└── instance/
    └── database.db       # SQLite database
```

---

## 8. Development Roadmap

### 8.1 Phase 1: Foundation (Days 1-2)
- Initialize Flask structure (`__init__.py`, `models.py`)
- **CRITICAL**: Create the `universities.csv` data file with at least 5 rows
- Write the `load_data.py` script to parse the CSV and populate the database
- Ensure database schema matches Section 4.1 exactly
- Test database creation and data loading

### 8.2 Phase 2: Logic & Views (Days 3-4)
- Implement auth routes (Login/Signup)
- Implement main routes (Browse by Country → University → Program)
- Write the `calculate_compatibility` Python function in `models.py`
- Create base template with consistent horizontal navbar
- Implement hierarchical browsing views
- **Interactive Map Implementation**: Create custom JavaScript (`static/js/map.js`) for world map interaction
  - Implement click handlers for country selection
  - Add keyboard navigation support (Tab, Enter, Space)
  - Add ARIA labels and roles for accessibility
  - Create fallback dropdown/list for accessibility
  - Ensure mobile responsiveness (touch events)

### 8.3 Phase 3: The "Shopping Cart" (Day 5)
- Create the shortlist route (Add/Remove from DB)
- Build the "My Dashboard" page that displays the saved list
- Display calculated compatibility badges on dashboard
- Implement "Add to List" button on program cards

### 8.4 Phase 4: Polish & Deploy (Day 6)
- Implement Cinematic Dark Theme (SRS UI-08 to UI-12)
  - Set up CSS variables for dark mode color palette
  - Apply deep matte black background (#0a0a0a) and dark grey cards (#161616)
  - Implement borderless card design with hover effects
  - Apply glassmorphism navigation bar
  - Set up Inter typography hierarchy
  - Style compatibility badges with accent colors (Electric Blue, Neon Purple)
- Ensure WCAG 2.1 AA compliance (high contrast on dark background)
- Implement spacious layouts for visual engagement (SRS NFR-15)
- Test responsive design on multiple devices
- Deploy to PythonAnywhere
- Verify Accessibility (Lighthouse Audit)

### 8.5 Implementation Instruction
**Important**: Do not start coding the HTML templates yet. Start by creating the `models.py` file exactly matching the schema in Section 4.1, and the `universities.csv` file with at least 5 rows of data. This ensures the backbone is solid before we dress it up.

---

## 9. Testing Requirements

### 9.1 Functional Testing
- Test user registration and login
- Test program browsing and filtering
- Test shortlist add/remove functionality
- Test compatibility calculation accuracy
- Test profile update functionality

### 9.2 Accessibility Testing
- Test with screen readers
- Test keyboard navigation
- Test color contrast
- Test form labels and error messages
- Validate WCAG compliance

### 9.3 Responsiveness Testing
- Test on desktop (1920x1080, 1366x768)
- Test on tablet (768x1024)
- Test on mobile (375x667, 414x896)

### 9.4 Security Testing
- Test password hashing
- Test session management
- Test SQL injection prevention
- Test XSS prevention

---

## 10. Future Enhancements (Out of Scope)

- Email notifications for application deadlines
- Program comparison feature
- Advanced recommendation engine using machine learning
- Social features (sharing shortlists)
- University admin panel for program management
- Web scraping for automatic program data updates

---

## 11. Appendices

### 11.1 Glossary
- **Shopping Platform**: The core metaphor - users shop for programs like products
- **The Wallet**: User's academic credentials (GPA, TOEFL, internships, research papers)
- **The Price**: Program requirements (min GPA, min TOEFL, research/industry focus)
- **The Brand**: Universities that offer programs
- **The Product**: Graduate programs available for shortlisting
- **Shopping Cart / Shortlist**: Many-to-many relationship allowing users to save multiple programs
- **Compatibility Calculator**: Advanced algorithmic feature that matches user profiles to program requirements
- **Dashboard**: User's personal page displaying profile and shortlisted programs
- **QS Rank**: Quacquarelli Symonds World University Rankings

### 11.2 Change Log
| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Date] | [Name] | Initial SRS document |

---

**Document Status:** Draft - Ready for Review