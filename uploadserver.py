#!/usr/bin/python
#encoding=utf-8
import Image
import logging
import json
import os
import tempfile
import tornado.web
from tornado.options import define, options, parse_command_line
from fdfs_client.client import Fdfs_client

define("port", default=8080, help="run on the given port", type=int)
define("config_type", default="dev", help="config type")


class UploadHandler(tornado.web.RequestHandler):
    @property
    def client(self):
        return self.application.client

    def get(self):
        self.render("index.html")

    def post(self):
        images = self.request.files.get("images")
        image_pathes = []
        for image in images:
            tf = tempfile.NamedTemporaryFile()
            tf.write(image.body)
            tf.seek(0)
            img = Image.open(tf)
            img_path = self.client.upload_by_buffer(img.convert("RGBA").tostring("jpeg", "RGB"), file_ext_name="jpg")
            img_path = os.sep.join(img_path.get('Remote file_id').split(os.sep)[1:])
            image_pathes.append(img_path)
        res = dict(status=1, image_pathes=image_pathes)
        self.finish(json.dumps(res))


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", UploadHandler),
        ],
        cookie_secret="IloveYou",
        xsrf_cookies=False,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
    )
    app.client = Fdfs_client()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
