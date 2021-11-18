from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, InputRequired, ValidationError
import re
from enums import Genre, State
from models import *


#----------------------------------------------------------------------------#
# Custom Validators.
#----------------------------------------------------------------------------#

def validate_phone(form, field):
    pattern = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    if not pattern.match(field.data):
        raise ValidationError('Invalid phone number')

def validate_genres(form, field):
    if not set(field.data).issubset(dict(Genre.choices()).keys()):
        raise ValidationError("Invalid Genre Selection")

def validate_state(form, field):
    if field.data not in dict(State.choices()).keys():
        raise ValidationError("Invalid State")

def validate_artist_id(form, field):
    artist = db.session.query(Artist.id).filter_by(id = field.data).first()
    if artist is None:
        raise ValidationError("Invalid Artist Id")

def validate_venue_id(form, field):
    venue = db.session.query(Venue.id).filter_by(id = field.data).first()
    if venue is None:
        raise ValidationError("Invalid Venue Id")



#----------------------------------------------------------------------------#
# Forms.
#----------------------------------------------------------------------------#

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id', validators=[DataRequired(), validate_artist_id]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired(), validate_venue_id]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired(message=('Please enter valid time'))],
        default= datetime.today()
    )


class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), validate_state],
        choices = State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[InputRequired(), validate_phone]
    )
    image_link = StringField(
        'image_link', validators=[URL(message=('Invalid Image Link'))]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres],
        choices = Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(message=('Invalid Facebook Link'))]
    )
    website_link = StringField(
        'website_link', validators=[URL(message=('Invalid Website Link'))]
    )

    seeking_talent = BooleanField('seeking_talent', default=False)

    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), validate_state],
        choices = State.choices()
    )
    phone = StringField(
        'phone', [InputRequired(), validate_phone]
    )
    image_link = StringField(
        'image_link', validators=[URL(message=('Invalid Image Link'))]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres],
        choices = Genre.choices()
     )
    facebook_link = StringField(
        'facebook_link', validators=[URL(message=('Invalid Facebook Link'))]
     )

    website_link = StringField(
        'website_link', validators=[URL(message=('Invalid Website Link'))]
     )

    seeking_venue = BooleanField('seeking_venue', default=False)

    seeking_description = StringField(
            'seeking_description'
     )

