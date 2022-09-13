import sys

import flask
from flask import Flask, request
from cloud_file_storage_controller.db.db_controller import create_db
from cloud_file_storage_controller.db.schema_db import SystemItem
from typing import Tuple
import config

from logger_config import error_logger, info_logger

app = Flask(__name__)
sys.path.append('../')


@app.route('/imports', methods=["POST"])
def imports():
    try:
        data = request.json
        SystemItem.add(data)
        return flask.make_response({"code": 200})
    except Exception as E:
        error_logger.error(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})


# def delete_all(data: dict):
#     deleted_data =

@app.route('/delete/{id}', methods=["DELETE"])
def delete():
    try:
        data = request.json
        deleted_files = SystemItem.delete(data)
        print(deleted_files)
        return flask.make_response({"code": 200})
    except Exception as E:
        error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})
    # except Exception as E:
    #     return flask.make_response({"code": 404, "message": "Item not found"})        # TODO: add this except


def family(parent_id: dict):
    family_dict = SystemItem.get_children(parent_id)
    print(family_dict)
    for children in family_dict["children"]:
        if children["children"]:
            return family({"id": children["id"]})


@app.route('/nodes/{id}', methods=["GET"])
def nodes():
    try:
        data = request.args
        family(data)
        return flask.make_response({"code": 200})
    except Exception as E:
        error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})
    # except Exception as E:
    #     return flask.make_response({"code": 404, "message": "Item not found"})        # TODO: add this except


@app.route('/updates', methods=["GET"])
def updates():
    try:

        return flask.make_response({"code": 200})
    except Exception as E:
        error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})


@app.route('/node/{id}/history', methods=["GET"])
def nodes_history():
    try:

        return flask.make_response({"code": 200})
    except Exception as E:
        error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})
    # except Exception as E:
    #     return flask.make_response({"code": 404, "message": "Item not found"})        # TODO: add this except


def main():
    create_db()
    app.run(host=config.HOST_ADDRESS, port=config.HOST_PORT)


if __name__ == '__main__':
    main()
