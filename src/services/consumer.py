import logging
import threading

import pika
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.session import sessionmaker

from models import Photos
from models import PhotoThumbnails
from thumb_util import make_thumb_data


class PikaThreadedConsumer(threading.Thread):
    """Process rabbitmq queue and generate thumbnails for photos.

    :param uri: ampq uri to connect
    :param queue_name: queue to listen
    :param db_uri: postgre uri to connect
    :param path: dir to store thumbnail files generated
    :returns threading.Thread object, use .start() method to launch in thread
             or .run() to run in main thread
    :rtype: threading.Thread
    """

    def __init__(self, uri: str, queue_name: str, db_uri: str,
                 path: str, *args, **kwargs):
        super(PikaThreadedConsumer, self).__init__(*args, **kwargs)
        self.uri = uri
        self.queue = queue_name
        self.db_uri = db_uri
        self.path = path
        self.logger = logging.getLogger(f'consumer: {queue_name}')

    def set_up_db(self):
        self.engine = create_engine(self.db_uri)
        self.session_maker = sessionmaker(bind=self.engine)

    def session(self) -> Session:
        return self.session_maker()

    def set_pika(self):
        connection = pika.BlockingConnection(
            pika.URLParameters(
                self.uri
            )
        )
        self.channel = connection.channel()

    def run(self):
        self.set_up_db()
        self.set_pika()

        for _, _, body in self.channel.consume(self.queue):
            self.logger.info(f'got message. body: {body}')
            self.process_message(body)

    def process_message(self, body: bytes):
        session = self.session()

        uuid = body.decode('utf-8')
        photo = session.query(Photos).get(uuid)
        if photo.status != 'pending':
            self.logger.info(f'{uuid} has wrong status `{photo.status}`. skip')
            return

        photo.status = 'processing'
        session.commit()

        self.logger.info(f'processing photo {uuid}')

        try:
            self.make_thumbnail(photo)
        except Exception:
            photo.status = 'failed'
            session.commit()
            self.logger.exception(f'fail on make_thumbnail for photo {uuid}')
            return

        photo.status = 'completed'
        session.commit()

        self.logger.info(f'thumbnail made for {uuid}')

        return

    def make_thumbnail(self, photo: Photos) -> PhotoThumbnails:
        self.logger.info(f'make thumb for {photo.url}')

        data, w, h = make_thumb_data(photo.url, 320, 320)
        filename = f'{photo.uuid}_{w}x{h}.jpg'
        fullpath = f'{self.path}/{filename}'

        with open(fullpath, 'wb') as f:
            f.write(data)

        self.logger.info(f'saved thumb  {fullpath} size: {len(data)}')

        session = self.session()
        thumb = PhotoThumbnails(
            photo_uuid=photo.uuid,
            width=w,
            height=h,
            url=filename,
        )
        session.add(thumb)
        session.commit()
        return thumb
