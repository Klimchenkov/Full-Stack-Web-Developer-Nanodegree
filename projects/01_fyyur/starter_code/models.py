from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import sys

db = SQLAlchemy()
migrate = Migrate()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__= 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def the_show(self):
        return {
                    "venue_id": self.Venue.id,
                    "venue_name": self.Venue.name,
                    "artist_id": self.Artist.id,
                    "artist_name": self.Artist.name,
                    "artist_image_link": self.Artist.image_link,
                    "start_time": str(self.start_time)
                }
    
    @classmethod
    def create_show(cls,data):
        success = True
        try:
            show=cls(**data)
            db.session.add(show)
            db.session.commit()
        except:
            success = False
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        return success

  

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link= db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False) 
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def upcoming_shows(self):
        shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==self.id).filter(Show.start_time > datetime.now()).all()
        upcoming_shows=[{
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        } for show, artist in shows]
        return upcoming_shows

    def past_shows(self):
        shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==self.id).filter(Show.start_time < datetime.now()).all()
        past_shows=[{
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        } for show, artist in shows]
        return past_shows

    def venue_data(self):
        return {
                "id": self.id,
                "name": self.name,
                "genres": self.genres,
                "address": self.address,
                "city": self.city,
                "state": self.state,
                "phone": self.phone,
                "website": self.website_link,
                "facebook_link": self.facebook_link,
                "seeking_talent": self.seeking_talent,
                "seeking_description": self.seeking_description,
                "image_link": self.image_link,
                "past_shows": self.past_shows(),
                "upcoming_shows": self.upcoming_shows(),
                "past_shows_count": len(self.past_shows()),
                "upcoming_shows_count": len(self.upcoming_shows()),
            }

    @classmethod
    def venues_by_area(cls):
        data=[]
        areas = db.session.query(cls.city, cls.state).group_by(cls.city, cls.state).all()
        for area in areas:
            venues = cls.query.filter(cls.city == area.city).filter(cls.state == area.state).all()
            data.append({ "city": area.city,
                          "state": area.state,
                          "venues": [{
                              "id": venue.id,
                              "name": venue.name,
                              "num_upcoming_shows": len(venue.upcoming_shows())
                          } for venue in venues]})
        return data

    @classmethod
    def create_venue(cls, data):
        success = True
        try:
            venue = cls(**data)
            db.session.add(venue)
            db.session.commit()
        except:
            print(sys.exc_info())
            success = False
            db.session.rollback()
        finally:
            db.session.close()
        return success

    def update_venue(self, name, city, state, address, phone, image_link, genres, facebook_link, website_link, seeking_talent, seeking_description):
        success=True
        try:
   
            self.name = name
            self.city = city
            self.state = state
            self.address = address
            self.phone = phone
            self.image_link = image_link
            self.genres = genres
            self.facebook_link = facebook_link
            self.website_link = website_link
            self.seeking_talent = seeking_talent
            self.seeking_description = seeking_description
            db.session.commit()
        except:
            print(sys.exc_info())
            db.session.rollback()
            success = False
        finally:
            db.session.close()

        return success

    def delete_venue(self):
        success=True
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            print(sys.exc_info())
            success=False
            db.session.rollback()
        finally:
            db.session.close()
        return success

    @classmethod
    def search_venue(cls, search_term):
        venues = cls.query.filter(cls.name.ilike(f'%{search_term}%'))
        return { "count": venues.count(),
                 "data": [{
                     "id": venue.id,
                     "name": venue.name,
                     "num_upcoming_shows": len(venue.upcoming_shows())
                     } for venue in venues]}


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.PickleType)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link= db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def upcoming_shows(self):
        shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id==self.id).filter(Show.start_time > datetime.now()).all()
        upcoming_shows=[{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        } for show, venue in shows]
        return upcoming_shows

    def past_shows(self):
        shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id==self.id).filter(Show.start_time < datetime.now()).all()
        past_shows=[{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        } for show, venue in shows]
        return past_shows

    def artist_data(self):
        return {
                "id": self.id,
                "name": self.name,
                "genres": self.genres,
                "city": self.city,
                "state": self.state,
                "phone": self.phone,
                "website": self.website_link,
                "facebook_link": self.facebook_link,
                "seeking_venue": self.seeking_venue,
                "seeking_description": self.seeking_description,
                "image_link": self.image_link,
                "past_shows": self.past_shows(),
                "upcoming_shows": self.upcoming_shows(),
                "past_shows_count": len(self.past_shows()),
                "upcoming_shows_count": len(self.upcoming_shows()),
            }

    def update_artist(self, name, city, state, phone, image_link, genres, facebook_link, website_link, seeking_venue, seeking_description):
        success=True
        try:
   
            self.name = name
            self.city = city
            self.state = state
            self.phone = phone
            self.image_link = image_link
            self.genres = genres
            self.facebook_link = facebook_link
            self.website_link = website_link
            self.seeking_venue = seeking_venue
            self.seeking_description = seeking_description
            db.session.commit()
        except:
            print(sys.exc_info())
            db.session.rollback()
            success = False
        finally:
            db.session.close()

        return success


    @classmethod
    def search_artist(cls, search_term):
        artists = cls.query.filter(cls.name.ilike(f'%{search_term}%'))
        return { "count": artists.count(),
                 "data": [{
                     "id": artist.id,
                     "name": artist.name,
                     "num_upcoming_shows": len(artist.upcoming_shows())
                     } for artist in artists]}

    @classmethod
    def create_artist(cls, data):
        success = True
        try:
            artist=cls(**data)
            db.session.add(artist)
            db.session.commit()
        except:
            success = False
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        return success