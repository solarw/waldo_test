import os

QUEUE_NAME = 'photo-proccessor'
AMQP_URI = os.environ["AMQP_URI"]
DB_URI = os.environ["PG_CONNECTION_URI"]
FILE_PATH = '/waldo-app-thumbs'
