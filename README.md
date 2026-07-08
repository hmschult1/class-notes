# Class Notes/Alumni Update Form

A Flask web application for collecting and storing alumni update submissions through a multi-step form. The app gathers contact information, family updates, children, employment and education changes, life achievements, volunteer interests, and optional class-note content, then saves the data to a MySQL database and sends an email notification.

## Features

- Multi-step alumni update wizard
- Personal and contact information collection
- Family, child, employment, and education updates
- Life achievements and volunteer preferences
- Optional class-note submission with image upload support
- Review step before final submission
- Email notification via SendGrid
- Database persistence with Flask-SQLAlchemy and Flask-Migrate

## Project Structure

- app/ - Flask application package
  - routes/ - form wizard routes and submission logic
  - templates/forms/ - HTML templates for each form step
  - static/ - CSS, JavaScript, and uploaded files
  - utils/ - helper modules such as SendGrid integration
- config.py - application configuration
- run.py - application entry point
- migrations/ - Alembic migration files

## Requirements

The app uses the following Python packages:

- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-WTF
- PyMySQL
- python-dotenv
- sendgrid

## Local Setup

1. Clone the repository and change into the project directory.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install flask flask-sqlalchemy flask-migrate flask-wtf pymysql python-dotenv sendgrid
   ```

4. Copy the example environment file and update the values:

   ```bash
   copy .env.example .env
   ```

   Edit .env and set the values for:

   - SECRET_KEY
   - MYSQL_HOST
   - MYSQL_PORT
   - MYSQL_DATABASE
   - MYSQL_USER
   - MYSQL_PASSWORD
   - SENDGRID_API_KEY

## Database Setup

The application expects a MySQL database to be available. After configuring the connection details, initialize or upgrade the database schema:

```bash
flask db upgrade
```

If migrations have not been initialized in your environment yet, run:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Running the Application

Start the development server with:

```bash
python run.py
```

The app will be available at:

```text
http://127.0.0.1:5000/alumni-update/step1
```

## Environment Variables

The application reads configuration from the .env file. The example file includes these variables:

- SECRET_KEY - Flask secret key
- MYSQL_HOST - MySQL host
- MYSQL_PORT - MySQL port (default: 3306)
- MYSQL_DATABASE - database name
- MYSQL_USER - database username
- MYSQL_PASSWORD - database password
- SENDGRID_API_KEY - API key for sending emails

## Notes

- The form flow is implemented as a wizard and stores intermediate data in the user session until submission.
- Uploaded class-note images are stored under the app static uploads directory.
- Email delivery failures are logged rather than blocking the submission flow.