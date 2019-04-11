import logging
import sys

from flask import Flask
from flask import jsonify
from flask import request
from flask_marshmallow import Marshmallow

from conf import AMQP_URI
from conf import DB_URI
from conf import FILE_PATH
from conf import QUEUE_NAME
from consumer import PikaThreadedConsumer
from models import db
from models import Photos
from tasks import trigger_process_photo_task

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
ma = Marshmallow(app)


class PhotosSchema(ma.Schema):
    class Meta:
        fields = (
            'uuid',
            'url',
            'status',
            'created_at',
        )


@app.errorhandler(ValueError)
def handle_value_error(error):
    response = jsonify({
        'error': 'value_error',
        'message': str(error)
    })
    response.status_code = 400
    return response


@app.route("/")
def index():
    return jsonify(success=True)


@app.route("/photos/pending", methods=["GET"])
def photos_pending():
    photos = Photos.query.filter(Photos.status == 'pending')
    result = PhotosSchema(many=True).dump(photos)
    return jsonify(result.data)


@app.route("/photos/process", methods=["POST"])
def photos_process():
    photos_uuids = request.json['uuids']

    if not photos_uuids:
        raise ValueError('uuids should not be empty')

    photos = Photos.query.filter(Photos.uuid.in_(photos_uuids))

    # check if bad uuids passed
    not_found = set(photos_uuids) - set([str(i.uuid) for i in photos])
    if not_found:
        raise ValueError(f'{",".join(not_found)} not exists!')

    for photo in photos:

        # check if inproper status
        if photo.status != 'pending':
            raise ValueError((
                f'{photo.uuid} status is `{photo.status}`'
                ' but have to be `pending`'
            )
            )
        trigger_process_photo_task(photo.uuid)
        logger.info(f'process photo {photo.uuid} task triggered')

    return jsonify({'uuids': photos_uuids})


def main():
    queue_consumer = PikaThreadedConsumer(
        AMQP_URI,
        QUEUE_NAME,
        DB_URI,
        FILE_PATH,
    )
    queue_consumer.start()
    app.run(host='0.0.0.0', port=3000)


if __name__ == '__main__':
    main()
