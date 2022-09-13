import sys
from datetime import datetime, timedelta
import flask
from flask import Flask, request
from cloud_file_storage_controller.db.db_controller import create_db
from cloud_file_storage_controller.db.schema_db import SystemItem, SystemItemHistory
from typing import Tuple
import config

from logger_config import error_logger, info_logger

app = Flask(__name__)
sys.path.append('../')

#
# class Responses:
#     OK = '', 200
#     INVALID = flask.make_response({"code": 400, "message": "Validation Failed"}), 400
#     NOT_FOUND = flask.make_response({"code": 404, "message": "Item not found"}), 404


@app.route('/imports', methods=["POST"])
def imports():
    try:
        data = request.json
        SystemItem.add(data)
        return '', 200
    except Exception as E:
        # raise E
        error_logger.error(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"}), 400


@app.route('/delete/<file_id>', methods=["DELETE"])
def delete(file_id):
    try:
        deleted_files = SystemItem.delete({"id": file_id})
        if not deleted_files:
            return flask.make_response({"code": 404, "message": "Item not found"}), 404
        return '', 200
    except Exception as E:
        # error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"}), 400


@app.route('/nodes/<parent_id>', methods=["GET"])
def nodes(parent_id):
    try:
        parent = SystemItem.get(parent_id)
        if not parent:
            return flask.make_response({"code": 404, "message": "Item not found"}), 404
        parent['children'] = SystemItem.get_children({"id": parent_id})
        return flask.make_response(parent), 200
    except Exception as E:
        # error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"}), 400


@app.route('/updates', methods=["GET"])
def updates():
    try:
        time_now = datetime.now()
        one_day_before = time_now - timedelta(1)
        items = SystemItem.get_items_in_interval(one_day_before.isoformat(), time_now.isoformat())
        return flask.make_response(items), 200
    except Exception as E:
        error_logger(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})


@app.route('/node/<node_id>/history', methods=["GET"])
def nodes_history(node_id):
    try:
        time_now = datetime.now()
        one_day_before = time_now - timedelta(1)
        history = SystemItemHistory.get_items_in_interval(node_id, one_day_before.isoformat(), time_now.isoformat())
        return flask.make_response(history), 200
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
