"""SQLAlchemy models for the alumni update application.

This module defines the normalized data model used by the multi-step
alumni update form flow. Models correspond to the normalized schema
(`Alumni`, `AlumniUpdate`, related address/education/family/child
tables, and class notes). These classes are referenced by the form
submission code in `app/routes/form_routes.py` when persisting session
data to the database.
"""

from flask_sqlalchemy import SQLAlchemy
import datetime
from app import db
import enum


class PhoneType(enum.Enum):
    """Enum stored in `alumni.phone_type` to indicate phone kind.

    Stored values are short strings matched to WTForms radio choices.
    """
    MOBILE = "mobile"
    HOME = "home"


class Alumni(db.Model):
    """Primary alumni/person table.

    Holds canonical contact fields and relationships to addresses,
    Geneva education records, and `AlumniUpdate` submissions.
    """
    __tablename__ = "alumni"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    maiden_name = db.Column(db.String(100))
    pref_salutation = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    phone_type = db.Column(db.Enum(PhoneType), nullable=True)

    addresses = db.relationship(
        "AlumniAddress",
        back_populates="alumnus",
        cascade="all, delete-orphan"
    )

    geneva_educations = db.relationship(
        "AlumniGenevaEducation",
        back_populates="alumnus",
        cascade="all, delete-orphan"
    )

    updates = db.relationship(
        "AlumniUpdate",
        back_populates="alumnus",
        cascade="all, delete-orphan"
    )


class AlumniUpdate(db.Model):
    """A single submission/update event linked to an `Alumni`.

    This table stores which update types were selected, class-note
    preference, volunteer selections, and relationships to child,
    family, employment, education, and class note records.
    """
    __tablename__ = "alumni_updates"

    id = db.Column(db.Integer, primary_key=True)

    alumnus_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni.id"),
        nullable=False
    )

    submitted_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    
    update_types = db.Column(db.JSON, nullable=True)
    wants_class_note = db.Column(db.Boolean, default=False)
    additional_updates = db.Column(db.Text)
    volunteer_choices = db.Column(db.JSON, nullable=True)
    other_volunteer = db.Column(db.Text)

    viewed = db.Column(db.Boolean, default=False)

    alumnus = db.relationship(
        "Alumni",
        back_populates="updates"
    )

    family_update = db.relationship(
        "AlumniFamilyUpdate",
        back_populates="alumni_update",
        uselist=False,
        cascade="all, delete-orphan"
    )

    children = db.relationship(
        "AlumniChild",
        back_populates="alumni_update",
        cascade="all, delete-orphan"
    )

    employment_updates = db.relationship(
        "AlumniEmploymentUpdate",
        back_populates="alumni_update",
        cascade="all, delete-orphan"
    )

    education_updates = db.relationship(
        "AlumniEducationUpdate",
        back_populates="alumni_update",
        cascade="all, delete-orphan"
    )

    class_note = db.relationship(
        "AlumniClassNote",
        back_populates="alumni_update",
        uselist=False,
        cascade="all, delete-orphan"
    )


class AlumniAddress(db.Model):
    __tablename__ = "alumni_addresses"

    id = db.Column(db.Integer, primary_key=True)

    alumnus_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni.id"),
        nullable=False
    )

    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    alumnus = db.relationship(
        "Alumni",
        back_populates="addresses"
    )


class AlumniGenevaEducation(db.Model):
    __tablename__ = "alumni_geneva_educations"

    id = db.Column(db.Integer, primary_key=True)

    alumnus_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni.id"),
        nullable=False
    )

    degree_level = db.Column(db.String(50))  # undergrad, graduate, online
    degree = db.Column(db.String(150))
    graduation_year = db.Column(db.String(4))

    alumnus = db.relationship(
        "Alumni",
        back_populates="geneva_educations"
    )


class AlumniFamilyUpdate(db.Model):
    __tablename__ = "alumni_family_updates"

    id = db.Column(db.Integer, primary_key=True)

    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False,
        unique=True
    )

    marital_status = db.Column(db.String(20))
    spouse_name = db.Column(db.String(150))
    is_spouse_geneva_grad = db.Column(db.Boolean, default=False)
    spouse_geneva_degrees = db.Column(db.JSON, nullable=True)
    spouse_undergrad_year = db.Column(db.String(4))
    spouse_graduate_year = db.Column(db.String(4))
    spouse_online_year = db.Column(db.String(4))
    marry_date = db.Column(db.Date)

    alumni_update = db.relationship(
        "AlumniUpdate",
        back_populates="family_update"
    )


class AlumniChild(db.Model):
    __tablename__ = "alumni_children"

    id = db.Column(db.Integer, primary_key=True)

    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False
    )

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)

    alumni_update = db.relationship(
        "AlumniUpdate",
        back_populates="children"
    )

    def __repr__(self):
        return f"<AlumniChild {self.first_name} {self.last_name} ({self.gender})>"


class AlumniEmploymentUpdate(db.Model):
    __tablename__ = "alumni_employment_updates"

    id = db.Column(db.Integer, primary_key=True)

    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False
    )

    employer = db.Column(db.String(150))
    position = db.Column(db.String(150))
    start_date = db.Column(db.Date)

    alumni_update = db.relationship(
        "AlumniUpdate",
        back_populates="employment_updates"
    )


class AlumniEducationUpdate(db.Model):
    __tablename__ = "alumni_education_updates"

    id = db.Column(db.Integer, primary_key=True)

    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False
    )

    institution = db.Column(db.String(150))
    degree = db.Column(db.String(150))
    graduation_year = db.Column(db.String(4))

    alumni_update = db.relationship(
        "AlumniUpdate",
        back_populates="education_updates"
    )


class AlumniClassNote(db.Model):
    __tablename__ = "alumni_class_notes"

    id = db.Column(db.Integer, primary_key=True)

    alumni_update_id = db.Column(
        db.Integer,
        db.ForeignKey("alumni_updates.id"),
        nullable=False,
        unique=True
    )

    nameplate = db.Column(db.String(255))
    class_note_text = db.Column(db.Text)
    image_filename = db.Column(db.String(255))

    published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime(timezone=True))

    alumni_update = db.relationship(
        "AlumniUpdate",
        back_populates="class_note"
    )