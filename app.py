import os
from flask import Flask, render_template, request, redirect, flash, abort
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from models import db, User, University, Program, shortlist
from utils import (
    hash_password, verify_password, country_to_slug, slug_to_country,
    get_logo_url
)


def get_or_404(model, ident):
    instance = db.session.get(model, ident)
    if instance is None:
        abort(404)
    return instance


def create_app():
    app = Flask(__name__)

    instance_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'instance'
    )
    os.makedirs(instance_path, exist_ok=True)

    db_path = os.path.join(instance_path, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SECRET_KEY'] = 'dev-secret-key'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.template_filter('country_slug')
    def country_slug_filter(country_name):
        return country_to_slug(country_name)

    app.jinja_env.globals['get_logo_url'] = get_logo_url

    @app.route('/')
    def index():
        total_programs = db.session.query(Program).count()
        total_universities = db.session.query(University).count()
        total_countries = db.session.query(
            University.country
        ).distinct().count()

        return render_template(
            'index.html',
            total_programs=total_programs,
            total_universities=total_universities,
            total_countries=total_countries
        )

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        Registration page
        Handles user registration with validation and password hashing.
        """
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('register.html')

            existing_user = db.session.query(User).filter_by(
                username=username
            ).first()
            if existing_user:
                flash('Username already exists', 'error')
                return render_template('register.html')

            user = User(
                username=username,
                password=hash_password(password)
            )

            try:
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect('/login')
            except Exception:
                db.session.rollback()
                flash(
                    'An error occurred during registration. Try again.',
                    'error'
                )
                return render_template('register.html')

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Login page
        Handles user authentication with Flask-Login.
        """
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('login.html')

            user = db.session.query(User).filter_by(username=username).first()

            if user and verify_password(user.password, password):
                login_user(user)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('/dashboard')
            else:
                flash('Invalid credentials', 'error')

        return render_template('login.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """
        User dashboard
        Shows shortlisted programs with compatibility scores.
        """
        shortlist_query = db.session.query(
            Program,
            shortlist.c.date_added
        ).join(
            shortlist, Program.id == shortlist.c.program_id
        ).filter(
            shortlist.c.user_id == current_user.id
        ).order_by(
            shortlist.c.date_added.desc()
        )

        shortlist_entries = shortlist_query.all()

        shortlist_data = [(entry[0], entry[1]) for entry in shortlist_entries]

        return render_template('dashboard.html', shortlist_data=shortlist_data)

    @app.route('/dashboard/update-profile', methods=['POST'])
    @login_required
    def update_profile():
        """
        Profile update route
        Updates user's academic credentials.
        """
        try:
            gpa_str = request.form.get('gpa', '').strip()
            toefl_str = request.form.get('toefl_score', '').strip()
            internship_str = request.form.get('internship_exp', '').strip()
            research_str = request.form.get('research_papers', '').strip()

            if gpa_str:
                try:
                    gpa = float(gpa_str)
                    if gpa < 0 or gpa > 4.0:
                        flash('GPA must be between 0.0 and 4.0', 'error')
                        return redirect('/dashboard')
                    current_user.gpa = gpa
                except ValueError:
                    flash(
                        'Invalid GPA format. Enter number 0.0-4.0',
                        'error'
                    )
                    return redirect('/dashboard')
            else:
                current_user.gpa = 0.0

            if toefl_str:
                try:
                    toefl_score = int(toefl_str)
                    if toefl_score < 0 or toefl_score > 120:
                        flash('TOEFL score must be between 0 and 120', 'error')
                        return redirect('/dashboard')
                    current_user.toefl_score = toefl_score
                except ValueError:
                    flash(
                        'Invalid TOEFL score format. Enter a number 0-120',
                        'error'
                    )
                    return redirect('/dashboard')
            else:
                current_user.toefl_score = 0

            if internship_str:
                try:
                    internship_exp = int(internship_str)
                    if internship_exp < 0:
                        flash('Internship experience cannot be negative',
                              'error')
                        return redirect('/dashboard')
                    current_user.internship_exp = internship_exp
                except ValueError:
                    flash(
                        'Invalid internship experience. Enter a whole number',
                        'error'
                    )
                    return redirect('/dashboard')
            else:
                current_user.internship_exp = 0

            if research_str:
                try:
                    research_papers = int(research_str)
                    if research_papers < 0:
                        flash('Research papers count cannot be negative',
                              'error')
                        return redirect('/dashboard')
                    current_user.research_papers = research_papers
                except ValueError:
                    flash(
                        'Invalid research papers count. Enter a whole number',
                        'error'
                    )
                    return redirect('/dashboard')
            else:
                current_user.research_papers = 0

            db.session.commit()
            flash('Profile updated successfully', 'success')

        except Exception:
            db.session.rollback()
            flash(
                'An error occurred updating your profile. Try again.',
                'error'
            )

        return redirect('/dashboard')

    @app.route('/logout')
    @login_required
    def logout():
        """
        Logout page
        Handles user logout and redirects to home page.
        """
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect('/')

    @app.route('/browse')
    def browse():
        """
        Browse page
        Displays country selection for program browsing.
        Queries distinct countries from the database.
        """
        countries = db.session.query(University.country).distinct().all()
        country_list = [country[0] for country in countries if country[0]]
        country_list.sort()
        return render_template('browse.html', countries=country_list)

    @app.route('/browse/<country_slug>')
    def universities(country_slug):
        """
        Universities page
        Displays universities in the selected country.
        """
        countries = db.session.query(University.country).distinct().all()
        country_list = [country[0] for country in countries if country[0]]

        country_name = slug_to_country(country_slug, country_list)

        if not country_name:
            flash(f'Country "{country_slug}" not found.', 'error')
            return redirect('/browse')

        unis = db.session.query(University).filter_by(
            country=country_name
        ).all()

        unis.sort(
            key=lambda u: (u.qs_rank if u.qs_rank else float('inf'), u.name)
        )

        return render_template(
            'universities.html', universities=unis, country=country_name
        )

    @app.route('/universities/<int:university_id>/programs')
    def programs(university_id):
        """
        Programs page
        Displays all programs for a selected university.
        """
        university = get_or_404(University, university_id)
        programs_list = db.session.query(Program).filter_by(
            university_id=university_id
        ).all()

        programs_list.sort(key=lambda p: p.name)

        return render_template(
            'programs.html', programs=programs_list, university=university
        )

    @app.route('/programs/<int:program_id>')
    def program_detail(program_id):
        """
        Program detail page
        Displays detailed information about a specific program.
        """
        program = get_or_404(Program, program_id)
        return render_template('program_detail.html', program=program)

    @app.route('/shortlist/add/<int:program_id>', methods=['POST'])
    @login_required
    def add_to_shortlist(program_id):
        """
        Add program to shortlist
        Adds a program to the current user's shortlist (Shopping Cart).
        Prevents duplicate entries.
        """
        program = get_or_404(Program, program_id)

        if program not in current_user.shortlisted_programs:
            current_user.shortlisted_programs.append(program)
            db.session.commit()
            flash('Program added to shortlist', 'success')
        else:
            flash('Program already in shortlist', 'info')

        return redirect(request.referrer or '/')

    @app.route('/shortlist/remove/<int:program_id>', methods=['POST'])
    @login_required
    def remove_from_shortlist(program_id):
        """
        Remove program from shortlist
        Removes a program from the current user's shortlist (Shopping Cart).
        """
        program = get_or_404(Program, program_id)

        if program in current_user.shortlisted_programs:
            current_user.shortlisted_programs.remove(program)
            db.session.commit()
            flash('Program removed from shortlist', 'success')
        else:
            flash('Program not found in shortlist', 'info')

        return redirect('/dashboard')

    return app
