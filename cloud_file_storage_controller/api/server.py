import sys
from datetime import datetime, timedelta
import flask
from flask import Flask, request

sys.path.append("/usr/src/app/")
from cloud_file_storage_controller.db.tableSystemItemHistory import SystemItemHistory
from cloud_file_storage_controller.db.tableSystemItem import SystemItem
from cloud_file_storage_controller.db.dataBase import DataBaseSchema

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
        return '', 200
    except Exception as E:
        # raise E
        error_logger.error(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"}), 400


@app.route('/delete/<file_id>', methods=["DELETE"])
def delete(file_id: str):
    try:
        deleted_files = SystemItem.delete(file_id)
        if not deleted_files:
            info_logger.error({"error": f"System item with id: {file_id} not deleted. Item not found."})
            return flask.make_response({"code": 404, "message": "Item not found"}), 404
        info_logger.info(f"System item with id: {file_id} deleted")
        return '', 200
    except Exception as E:
        error_logger.error(E)
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
        error_logger.error(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"}), 400


@app.route('/updates', methods=["GET"])
def updates():
    try:
        time_now = datetime.now()
        one_day_before = time_now - timedelta(1)
        items = SystemItem.get_items_in_interval(one_day_before.isoformat(), time_now.isoformat())
        return flask.make_response(items), 200
    except Exception as E:
        error_logger.error(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})


@app.route('/node/<node_id>/history', methods=["GET"])
def nodes_history(node_id: str):
    try:
        date_start = request.args.get("dateStart")
        date_end = request.args.get("dateEnd")

        assert datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%SZ")
        assert datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%SZ")

        history = SystemItemHistory.get_items_in_interval(node_id, date_start, date_end)
        return flask.make_response(history), 200
    except Exception as E:
        error_logger.error(E)
        return flask.make_response({"code": 400, "message": "Validation Failed"})


def main():
    DataBaseSchema.create_db()
    # app.run(host=config.HOST_ADDRESS, port=config.HOST_PORT)


if __name__ == '__main__':
    main()
