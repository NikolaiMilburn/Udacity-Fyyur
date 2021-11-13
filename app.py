#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import add
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import ValidationError
from forms import *
from models import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

from models import db
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)
csrf = CSRFProtect(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []

    areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    for area in areas:
        data_venues = []

        venues = Venue.query \
            .filter_by(state=area.state) \
            .filter_by(city=area.city) \
            .all()

        for venue in venues:
            upcoming_shows = db.session \
                .query(Show) \
                .filter(Show.venue_id == venue.id) \
                .filter(Show.start_time > datetime.now()) \
                .all()

            data_venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(upcoming_shows)
            })

        data.append({
            'city': area.city,
            'state': area.state,
            'venues': data_venues
        })

    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form['search_term']
    search = '%{}%'.format(search_term)

    venues = Venue.query \
        .filter(Venue.name.ilike(search)) \
        .all()

    data_venues = []
    for venue in venues:
        upcoming_shows = Show.query \
            .filter(Show.venue_id == venue.id) \
            .filter(Show.start_time > datetime.now()) \
            .all()
        
        data_venues.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(upcoming_shows)
        })

    response = {
        'count': len(venues),
        'data': data_venues
    }

    form = VenueForm()
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''), form=form)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter(Venue.id == venue_id).first()

  past_shows = Show.query \
    .filter(Show.venue_id == venue_id) \
    .filter(Show.start_time < datetime.now()) \
    .all()

  if len(past_shows) > 0:
    data_past_shows = []

    for show in past_shows:
      artist = Artist.query \
        .filter(Artist.id == show.artist_id) \
        .first()

      data_past_shows.append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.start_time)
      })

      data.past_shows = data_past_shows
      data.past_shows_count = len(data_past_shows)

  upcoming_shows = Show.query \
    .filter(Show.venue_id == venue_id) \
    .filter(Show.start_time > datetime.now()) \
    .all()

  if len(upcoming_shows) > 0:
    data_upcoming_shows = []

    for show in upcoming_shows:
      artist = Artist.query \
        .filter(Artist.id == show.artist_id) \
        .first()

      data_upcoming_shows.append({
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.start_time)
      })

      data.upcoming_shows = data_upcoming_shows
      data.upcoming_shows_count = len(data_upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)
    form.validate()
  
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website = request.form['website_link']
        seeking_talent = True if 'seeking_talent' in request.form else False
        seeking_description = request.form['seeking_description']
        genres = request.form.getlist('genres')
        venue = Venue(name=name, city=city, state=state,
        address=address, phone=phone, image_link=image_link,
        facebook_link=facebook_link, website=website,
        seeking_talent=seeking_talent, seeking_description=seeking_description,
        genres=genres)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        flash('An error ocurred. Venue ' + name + ' could not be listed.')
    else:
        flash('Venue ' + name + ' was successfully listed!')

    return render_template('pages/home.html')
  
@app.route('/venues/<venue_id>', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        flash('An error ocurred. Venue could not be removed.')
    else:
        flash('Venue was successfully removed!')

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()

    data = []

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form['search_term']
    search = '%{}%'.format(search_term)

    artists = Artist.query \
        .filter(Artist.name.ilike(search)) \
        .all()

    data_artists = []
    for artist in artists:
        upcoming_shows = Show.query \
            .filter(Show.artist_id == artist.id) \
            .filter(Show.start_time > datetime.now()) \
            .all()
        
        data_artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(upcoming_shows)
        })

    response = {
        'count': len(artists),
        'data': data_artists
    }

    form = ArtistForm()

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''), form=form)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.filter(Artist.id == artist_id).first()

    past_shows = Show.query \
        .filter(Show.artist_id == artist_id) \
        .filter(Show.start_time < datetime.now()) \
        .all()

    if len(past_shows) > 0:
        data_past_shows = []

        for show in past_shows:
            venue = Venue.query \
                .filter(Venue.id == show.venue_id) \
                .first()

            data_past_shows.append({
              'venue_id': venue.id,
              'venue_name': venue.name,
              'venue_image_link': venue.image_link,
              'start_time': str(show.start_time)
            })

        data.past_shows = data_past_shows
        data.past_shows_count = len(data_past_shows)

    upcoming_shows = Show.query \
        .filter(Show.artist_id == artist_id) \
        .filter(Show.start_time > datetime.now()) \
        .all()

    if len(upcoming_shows) > 0:
        data_upcoming_shows = []

        for show in upcoming_shows:
            venue = Venue.query \
                .filter(Venue.id == show.venue_id) \
                .first()

            data_upcoming_shows.append({
              'venue_id': venue.id,
              'venue_name': venue.name,
              'venue_image_link': venue.image_link,
              'start_time': str(show.start_time)
            })

        data.upcoming_shows = data_upcoming_shows
        data.upcoming_shows_count = len(data_upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.filter(Artist.id == artist_id).first()

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    form = ArtistForm(request.form)
    form.validate()

    try:
        artist = Artist.query.filter(Artist.id == artist_id).first()

        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website = request.form['website_link']
        artist.seeking_venue = True if 'seeking_venue' in request.form else False
        artist.seeking_description = request.form['seeking_description']
        artist.genres = request.form.getlist('genres')

        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        flash('An error ocurred. Artist ' + request.form['name'] + ' could not be updated.')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).first()

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data= venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    form = VenueForm(request.form)
    form.validate
  
    try:
        venue = Venue.query.filter(Venue.id == venue_id).first()

        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']
        venue.website = request.form['website_link']
        venue.seeking_venue = True if 'seeking_venue' in request.form else False
        venue.seeking_description = request.form['seeking_description']
        venue.genres = request.form.getlist('genres')

        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        flash('An error ocurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm(request.form)
    form.validate()
  
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        image_link = request.form['image_link']
        website = request.form['website_link']
        seeking_venue = True if 'seeking_venue' in request.form else False
        seeking_description = request.form['seeking_description']
        genres = request.form.getlist('genres')

        artist = Artist(name=name, city=city, state=state, 
            phone=phone, image_link=image_link,
            facebook_link=facebook_link, website=website,
            seeking_venue=seeking_venue, seeking_description=seeking_description,
            genres=genres)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        flash('An error ocurred. Artist ' + name + ' could not be listed.')
    else:
        flash('Artist ' + name + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.order_by(Show.start_time.desc()).all()
    data = []
    for show in shows:
        venue = Venue.query.filter(Venue.id == show.venue_id).first()
        artist =Artist.query.filter(Artist.id == show.artist_id).first()

        data.append({
            'venue_id': show.venue_id,
            'venue_name': venue.name,
            'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': str(show.start_time)
        })


    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm(request.form)
    form.validate()
  
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if error:
        flash('An error ocurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
    csrf.init_app(app)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
