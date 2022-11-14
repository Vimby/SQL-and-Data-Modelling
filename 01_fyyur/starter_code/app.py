#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils import errors
import json
from time import timezone
from xmlrpc.client import DateTime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
 # TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, datetime):
        date = dateutil.parser.parse(value)
  else:
        date = value
 # date = dateutil.parser.parse(value)
  #if format == 'full':
  #    format="EEEE MMMM, d, y 'at' h:mma"
  #elif format == 'medium':
    #  format="EE MM, dd, y h:mma"
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
 # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

def venues():
   error = False
   try:
     venues = Venue.query.all()
     num_upcoming_shows = Venue.query.join(Show).filter(Show.start_time > datetime.now()).count()
     venues_list = []
     for venue in venues:
      venues_list.append({
        "city": venue.city,
      "state": venue.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      }]
      })
      
   except:
    error = True
    print(sys.exc_info)

   finally:
        db.session.close()

   if error:
       abort(500)

   else:
      return render_template('pages/venues.html', areas=venues_list)


  
#Search Venue by a query
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_query = request.form.get('search_term', ' ')
  search_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_query}%')).all()
  result = []

  for search in search_result:
   result.append({
      "id": search.id,
      "name": search.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == search.id).filter(Show.start_time > datetime.now()).all())
    })
  
  response={
    "count": len(search_result),
    "data": result
  }
  '''
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  '''
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#Get Venue by Id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue_list = Venue.query.get(venue_id)
  upcoming_shows_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  past_shows_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_list:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  for show in upcoming_shows_list:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time  
    })

  all_venue_details = {
    "id": venue_list.id,
    "name": venue_list.name,
    "genres": venue_list.genres,
    "address": venue_list.address,
    "city": venue_list.city,
    "state": venue_list.state,
    "phone": venue_list.phone,
    "website": venue_list.website,
    "facebook_link": venue_list.facebook_link,
    "seeking_talent": venue_list.seeking_talent,
    "seeking_description": venue_list.seeking_description,
    "image_link": venue_list.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=all_venue_details)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form =VenueForm()
  
  # TODO: insert form data as a new Venue record in the db, instead
   # TODO: modify data to be the data object returned from db insertion
  if form.validate_on_submit():
    create_venue = Venue (
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    website = form.website_link.data,
    image_link =form.image_link.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    genres=form.genres.data
    )
    db.session.add(create_venue)
    db.session.commit()

  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
       flash('Venue ' + request.form['name'] + ' could not be listed.')
       db.session.rollback()
       print(sys.exc_info())
      
  return render_template('pages/home.html', form=form)
 
 
      #Delete Venue

@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. 

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Deletion was successful')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Deletion was not successful')

  finally:
    db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name).order_by(Artist.id).all()
  artists_list = []
  for artist in artists:
   artists_list.append({
    "id": artist.id,
     "name": artist.name
  })
  '''
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  '''
  return render_template('pages/artists.html', artists= artists_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
 
  search_term = request.form.get('search_term', ' ')
  search_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  answer = []

  for search in search_result:
   answer.append({
      "id": search.id,
      "name": search.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == search.id).filter(Show.start_time > datetime.now()).all())
    })
  
  response={
    "count": len(search_result),
    "data": answer
  }
  '''
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  '''
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist_list = Artist.query.get(artist_id)
  upcoming_shows_list = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  past_shows_list = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []

  for show in past_shows_list:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    })
  for show in upcoming_shows_list:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time 
    })

  all_artist_list = {
    "id": artist_list.id,
    "name": artist_list.name,
    "genres": artist_list.genres,
    "city": artist_list.city,
    "state": artist_list.state,
    "phone": artist_list.phone,
    "website": artist_list.website,
    "facebook_link": artist_list.facebook_link,
    "seeking_venue": artist_list.seeking_venue,
    "seeking_description": artist_list.seeking_description,
    "image_link": artist_list.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
 
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html',artist = all_artist_list )

  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_list = Artist.query.get(artist_id)
  if artist_list: 
    form.name.data = artist_list.name
    form.genres.data = artist_list.genres
    form.city.data = artist_list.city
    form.state.data = artist_list.state
    form.phone.data = artist_list.phone
    form.website_link.data = artist_list.website
    form.facebook_link.data = artist_list.facebook_link
    form.seeking_venue.data = artist_list.seeking_venue
    form.seeking_description.data = artist_list.seeking_description
    form.image_link.data = artist_list.image_link
    

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_list)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
      artist = Artist.query.get(artist_id)
      form = ArtistForm(request.form)
      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
    
      try:
       db.session.commit()
       flash('Artist ' + request.form['name'] + ' was successfully updated!')

      except:
       db.session.rollback()
       flash('Artist ' + request.form['name'] + ' was not updated!')
    
      finally:
       db.session.close()
       return redirect(url_for('show_artist', artist_id=artist_id))

#Update Venue
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_list = Venue.query.get(venue_id)
  if venue_list: 
    form.name.data = venue_list.name
    form.genres.data = venue_list.genres
    form.address.data = venue_list.address
    form.city.data = venue_list.city
    form.state.data = venue_list.state
    form.phone.data = venue_list.phone
    form.website_link.data = venue_list.website
    form.facebook_link.data = venue_list.facebook_link
    form.seeking_talent.data = venue_list.seeking_talent
    form.seeking_description.data = venue_list.seeking_description
    form.image_link.data = venue_list.image_link 

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_list)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
      venue = Venue.query.get(venue_id)
      form = VenueForm(request.form)
      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.website_link = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data
      try:
       db.session.commit()
       flash('Venue ' + request.form['name'] + ' was successfully updated!')

      except:
       db.session.rollback()
       flash('Venue ' + request.form['name'] + ' was not updated!')

      finally:
       db.session.close()
       return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission(): 
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

 form = ArtistForm()
 if form.validate_on_submit():
       create_artist = Artist (
       name = form.name.data,
       city = form.city.data,
       state = form.state.data,
       phone = form.phone.data,
       website = form.website_link.data,
       image_link =form.image_link.data,
       facebook_link = form.facebook_link.data,
       seeking_venue = form.seeking_venue.data,
       seeking_description = form.seeking_description.data,
       genres= form.genres.data
       )
       db.session.add(create_artist)
       db.session.commit()

  # on successful db insert, flash success
       flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
 else:
      flash('Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())

 return render_template('pages/home.html')

  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
    shows_list = []
    shows = Show.query.all()
    for show in shows:
      artist = Artist.query.get(show.artist_id)
      venue = Venue.query.get(show.venue_id)

      shows_list.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      })

    return render_template('pages/shows.html', shows=shows_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
     form = ShowForm()
     if form.validate_on_submit():   
      create_show = Show (
      artist_id =form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time =form.start_time.data
      )
      db.session.add(create_show)
      db.session.commit()

  # on successful db insert, flash success
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     else:
     
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      print(sys.exc_info())

     
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
db.init_app(app)
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
