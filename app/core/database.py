from app.core.settings import settings
from app.api.endpoints.user.functions import get_password_hash
from app.models import User, Admin
from app.utils.constant.globals import UserRole
from app.core.base import Base, engine, SessionLocal


def create_db_tables():
    """Creates all database tables defined in Base.metadata."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

def create_initial_admin():
    """
    Checks if an admin user exists and creates one if not.
    This function should be called after tables are created.
    """
    db = SessionLocal()
    try:
        # Check if any user with the ADMIN role exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()

        if not existing_admin:
            print("\nNo admin user found. Creating initial admin...")
            # Use settings for admin credentials for better configurability
            admin_email = settings.INITIAL_ADMIN_EMAIL
            admin_password = settings.INITIAL_ADMIN_PASSWORD
            admin_first_name = "Super"
            admin_last_name = "Admin"

            if not admin_email or not admin_password:
                print("WARNING: INITIAL_ADMIN_EMAIL or INITIAL_ADMIN_PASSWORD not set in settings. Skipping initial admin creation.")
                print("Please set these environment variables or define them in app.core.settings.py.")
                return

            hashed_password = get_password_hash(admin_password)

            # Assuming Admin model inherits from User and sets the role correctly
            initial_admin = Admin(
                email=admin_email,
                password=hashed_password,
                first_name=admin_first_name,
                last_name=admin_last_name,
                role=UserRole.ADMIN # Explicitly set the role
            )
            db.add(initial_admin)
            db.commit()
            db.refresh(initial_admin)
            print(f"Initial admin '{initial_admin.email}' created successfully.")
        else:
            print("\nAdmin user already exists. Skipping initial admin creation.")
    except Exception as e:
        db.rollback()
        print(f"Error during initial admin creation: {e}")
    finally:
        db.close()

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
