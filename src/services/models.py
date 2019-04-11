from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql.base import ENUM
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey

db = SQLAlchemy()


StatusType = ENUM(
    'pending',
    'completed',
    'processing',
    'failed',
    name="status",
    create_type=True,
)


class Photos(db.Model):
    __tablename__ = 'photos'

    uuid = db.Column(
        UUID,
        server_default=text("gen_random_uuid()"),
        primary_key=True
    )

    url = db.Column(db.String(), nullable=False)
    status = db.Column(StatusType)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )

    def __init__(self, uuid, url, status, created_at):
        self.uuid = uuid
        self.url = url
        self.status = status
        self.created_at = created_at

    def __repr__(self):
        return '<PHOTO {}>'.format(self.uuid)


class PhotoThumbnails(db.Model):
    __tablename__ = 'photos_thumbnails'

    uuid = db.Column(
        UUID,
        server_default=text("gen_random_uuid()"),
        primary_key=True
    )
    photo_uuid = db.Column(UUID, ForeignKey('photos.uuid'), nullable=False)
    url = db.Column(db.String(), nullable=False)
    width = db.Column(db.SmallInteger(), nullable=False)
    height = db.Column(db.SmallInteger(), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )

    def __init__(self, photo_uuid, url, width, height):
        self.photo_uuid = photo_uuid
        self.url = url
        self.width = width
        self.height = height

    def __repr__(self):
        return '<THUMBNAIL {} for PHOTO {}>'.format(self.uuid, self.photo_uuid)
