from flask import Blueprint, jsonify, request

from experiment_collection.db import get_db

bp = Blueprint('main', __name__)


@bp.route('/experiment', methods=('GET', 'POST', 'DELETE'))
def experiment_view():
    collection_name = request.form['collection_name']
    name = request.form['name']
    db = get_db()
    if request.method == 'GET':
        js = db.check_experiment(collection_name, name)
    elif request.method == 'POST':
        params = request.form['params']
        metrics = request.form['metrics']
        time = request.form['time']
        js = db.add_experiment(collection_name, name, params, metrics, time)
    elif request.method == 'DELETE':
        js = db.delete_experiment(collection_name, name)
    else:
        raise
    return jsonify(js)


@bp.route('/all_experiments', methods=('POST',))
def all_experiments_view():
    collection_name = request.form['collection_name']
    db = get_db()
    js = db.get_experiments(collection_name)
    return jsonify(js)
