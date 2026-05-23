import csv
import os
from models import db, University, Program


def read_csv_data(filename):
    """
    Reads CSV file and returns list of dictionaries.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, filename)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    data = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if any(row.values()):
                    data.append(row)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    if not data:
        raise ValueError("CSV file is empty or contains no valid data")

    return data


def _parse_int(value, default=None):
    """Helper function to parse integer values, handling empty strings."""
    if not value or value.strip() == '':
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _parse_float(value, default=None):
    """Helper function to parse float values, handling empty strings."""
    if not value or value.strip() == '':
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _parse_bool(value):
    """Parse boolean values from CSV (1/0, True/False, yes/no)."""
    if not value:
        return False
    value_str = str(value).strip().lower()
    if value_str in ('1', 'true', 'yes', 'y'):
        return True
    elif value_str in ('0', 'false', 'no', 'n', ''):
        return False
    return False


def load_data_to_db(app, csv_file='universities.csv', clear_existing=False):
    """
    Loads data from CSV file into the database.
    """
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///') and ':memory:' not in db_uri:
            db_path = db_uri.replace('sqlite:///', '')
            if db_path.startswith('/'):
                db_path = db_path[1:]
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

        db.create_all()
        if clear_existing:
            db.session.query(Program).delete()
            db.session.query(University).delete()
            db.session.commit()

        data = read_csv_data(csv_file)

        universities_created = 0
        programs_created = 0
        university_cache = {}

        for row in data:
            try:
                uni_name = row.get('university_name')
                prog_name = row.get('program_name')
                min_gpa_val = row.get('min_gpa')

                if not uni_name or not uni_name.strip():
                    raise ValueError(f"Row missing university_name: {row}")
                if not prog_name or not prog_name.strip():
                    raise ValueError(f"Row missing program_name: {row}")
                if not min_gpa_val or not min_gpa_val.strip():
                    raise ValueError(f"Row missing min_gpa: {row}")

                university_name = uni_name.strip()
                program_name = prog_name.strip()

                if university_name in university_cache:
                    university = university_cache[university_name]
                else:
                    university = db.session.query(University).filter_by(
                        name=university_name
                    ).first()
                    if not university:
                        university = University(
                            name=university_name,
                            country=row.get('country', '').strip() or None,
                            qs_rank=_parse_int(row.get('qs_rank')),
                            logo_url=row.get('logo_url', '').strip() or None
                        )
                        db.session.add(university)
                        db.session.flush()
                        universities_created += 1
                    university_cache[university_name] = university

                existing_program = db.session.query(Program).filter_by(
                    name=program_name,
                    university_id=university.id
                ).first()

                if existing_program:
                    continue

                min_gpa = _parse_float(row.get('min_gpa'))
                if min_gpa is None:
                    raise ValueError(
                        f"Invalid min_gpa for program {program_name}: "
                        f"{row.get('min_gpa')}"
                    )

                program = Program(
                    university_id=university.id,
                    name=program_name,
                    category=row.get('category', '').strip() or None,
                    min_gpa=min_gpa,
                    min_toefl=_parse_int(row.get('min_toefl'), default=0),
                    tuition_fee=row.get('tuition_fee', '').strip() or None,
                    deadline=row.get('deadline', '').strip() or None,
                    research_focus=_parse_bool(row.get('research_focus')),
                    industry_focus=_parse_bool(row.get('industry_focus'))
                )
                db.session.add(program)
                programs_created += 1

            except Exception as e:
                print(f"Error processing row: {row}")
                print(f"Error: {e}")
                continue

        try:
            db.session.commit()
            print(
                f"Successfully loaded {universities_created} universities "
                f"and {programs_created} programs"
            )
            return universities_created, programs_created
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error committing to database: {e}")


if __name__ == '__main__':
    """
    Main function to run the data loading script directly.
    """
    import argparse
    from app import create_app

    parser = argparse.ArgumentParser(
        description='Load university and program data from CSV into database'
    )
    parser.add_argument(
        '--clear', action='store_true',
        help='Clear existing data before loading (deletes all existing data)'
    )
    parser.add_argument(
        '--csv', default='universities.csv',
        help='Path to CSV file (default: universities.csv)'
    )

    args = parser.parse_args()

    app = create_app()

    if args.clear:
        prompt = ("WARNING: This will delete all existing data. "
                  "Continue? (yes/no): ")
        response = input(prompt)
        if response.lower() != 'yes':
            print("Aborted.")
            exit(0)

    try:
        universities_created, programs_created = load_data_to_db(
            app,
            csv_file=args.csv,
            clear_existing=args.clear
        )
        print("\n✓ Successfully loaded:")
        print(f"  - {universities_created} universities")
        print(f"  - {programs_created} programs")
    except Exception as e:
        print(f"\n✗ Error loading data: {e}")
        exit(1)
