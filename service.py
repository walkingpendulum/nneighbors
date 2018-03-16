# encoding: utf-8
import logging

import pymongo
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mongo_host", default="mongo-db", help="connect to mongodb instance on the given host")
define("mongo_port", default=27017, help="connect to mongodb instance on the given port")


class BaseApplicationRequestHandler(tornado.web.RequestHandler):
    def initialize(self, mongo_collection, logger):
        self.collection = mongo_collection
        self.logger = logger


class AddHandler(BaseApplicationRequestHandler):
    def post(self):
        body = tornado.escape.json_decode(self.request.body)

        coordinates = body['coordinates']
        name = body['name']

        rec = {'name': name, 'coordinates': coordinates}

        try:
            self.collection.insert_one(rec)
        except pymongo.errors.DuplicateKeyError:
            self.logger.debug('Duplicate key error occured for {}, skip insertion'.format(rec))


class NearHandler(BaseApplicationRequestHandler):
    def post(self):
        body = tornado.escape.json_decode(self.request.body)
        coordinates = body['coordinates']

        cursor = self.collection.find({'coordinates': {'$near': coordinates}}).limit(100)
        result = [{'name': rec['name'], 'coordinates': rec['coordinates']} for rec in cursor]

        self.write(tornado.escape.json_encode(result))
        self.finish()


class Application(tornado.web.Application):
    def __init__(self, mongo_collection, logger, **kwargs):
        super(Application, self).__init__(**kwargs)

        self.create_indexes(mongo_collection)
        self.logger = logger

        self.logger.info('app is up and running on port {0[port]}'.format(options))

    @staticmethod
    def create_indexes(mongo_collection):
        mongo_collection.create_index(
            [
                ('coordinates', pymongo.GEO2D),
                ('name', pymongo.DESCENDING)
            ],
            unique=True,
        )


def main():
    tornado.options.parse_command_line()

    app_logger = logging.getLogger('tornado.application')

    mongo_connection_string = 'mongodb://{0.mongo_host}:{0.mongo_port}/'.format(options)
    mongo_client = pymongo.MongoClient(mongo_connection_string)

    try:
        collection = mongo_client.nneighbors_db.records

        application = Application(
            logger=app_logger,
            mongo_collection=collection,
            handlers=[
                (r"/add", AddHandler, dict(mongo_collection=collection, logger=app_logger)),
                (r"/near", NearHandler, dict(mongo_collection=collection, logger=app_logger)),
            ],
        )

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.current().start()

    finally:
        mongo_client.close()


if __name__ == "__main__":
    main()
