class MissingDatabaseError(RuntimeError):
    ''' Raised when database is missing '''


class DbAdapter:

    __db = None

    def __new__(cls, *args, **kwargs):
        raise Exception("DbAdapter can not be instantiated!")

    @staticmethod
    def set_db(db):
        DbAdapter.__db = db

    @staticmethod
    def get_db():
        return DbAdapter.__db

    @staticmethod
    def fetch(record_id):
        db = DbAdapter.get_db()
        try:
            record = db[record_id]
        except:
            if db is None:
                raise MissingDatabaseError('Database is not set. Use DbAdapter.set_db(my_db)')
            else:
                raise
        else:
            return record


class Record:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        if isinstance(other, Record):
            return other.__dict__ == self.__dict__
        else:
            return NotImplemented

    def __repr__(self):
        if hasattr(self, 'serial'):
            cls = self.__class__.__name__
            return '<{} serial={}>'.format(cls, self.serial)
        else:
            return super().__repr__()


class Event(Record):

    @property
    def venue(self):
        if not hasattr(self, '__venue'):
            self.__venue = DbAdapter.fetch('venue.{}'.format(self.venue_serial))
        return self.__venue

    @property
    def speakers(self):
        if not hasattr(self, '__speakers_list'):
            self.__speakers_list = [DbAdapter.fetch('speaker.{}'.format(speaker_id))
                                    for speaker_id in self.__dict__['speakers']]
        return self.__speakers_list

    def __repr__(self):
        if hasattr(self, 'name'):
            return '<{} {}>'.format(self.__class__.__name__, self.name)
        else:
            return super().__repr__()


