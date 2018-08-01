import shelve
from record_classes import DbAdapter

DB_NAME = './datafiles/oscon_schedule_db'
CHECK_KEY = 'conference.115'

oscon_db = shelve.open(DB_NAME)

DbAdapter.set_db(oscon_db)
evt = oscon_db['event.33463']

print(evt.name, evt.serial,
      evt.venue.name, evt.venue.category,
      evt.speakers[0].name, evt.speakers[0].position,
      evt.speakers[1].name, evt.speakers[1].position,
      sep='\n')


