from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class CellTower(db.Model):
    __tablename__ = 'cell_towers'

    id = db.Column(db.Integer, primary_key=True)
    cell_id = db.Column(db.Integer, nullable=False)
    lac = db.Column(db.Integer, nullable=False)
    mcc = db.Column(db.Integer, nullable=False)
    mnc = db.Column(db.Integer, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    radio = db.Column(db.String(10), nullable=False, default='GSM')
    range_m = db.Column(db.Integer)
    signal_avg = db.Column(db.Integer)
    operator = db.Column(db.String(100))
    samples = db.Column(db.Integer)
    source = db.Column(db.String(50), default='opencellid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('cell_id', 'lac', 'mcc', 'mnc', 'radio', name='uq_cell_identity'),
        db.Index('idx_lat_lon', 'lat', 'lon'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'cell_id': self.cell_id,
            'lac': self.lac,
            'mcc': self.mcc,
            'mnc': self.mnc,
            'lat': self.lat,
            'lon': self.lon,
            'radio': self.radio,
            'range_m': self.range_m,
            'signal_avg': self.signal_avg,
            'operator': self.operator,
            'samples': self.samples,
            'source': self.source,
        }


class ApiUsage(db.Model):
    __tablename__ = 'api_usage'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today, unique=True)
    count = db.Column(db.Integer, nullable=False, default=0)

    @classmethod
    def get_today(cls):
        today = date.today()
        usage = cls.query.filter_by(date=today).first()
        if not usage:
            usage = cls(date=today, count=0)
            db.session.add(usage)
            db.session.commit()
        return usage

    @classmethod
    def increment(cls):
        usage = cls.get_today()
        usage.count += 1
        db.session.commit()
        return usage.count

    @classmethod
    def can_call(cls, limit):
        usage = cls.get_today()
        return usage.count < limit
