import os
from flask import Flask, render_template, request, jsonify
from core.models import db, CellTower, ApiUsage
from core.input_validator import validate_search_params
from sources.opencellid import search_area
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

os.makedirs(config.DATA_DIR, exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/towers/search', methods=['POST'])
def search_towers():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    params, errors = validate_search_params(data)
    if errors:
        return jsonify({'error': errors}), 400

    result = search_area(params['lat'], params['lon'], params['radius_km'])
    return jsonify(result)


@app.route('/api/towers/<int:tower_id>')
def get_tower(tower_id):
    tower = CellTower.query.get(tower_id)
    if not tower:
        return jsonify({'error': 'Tower not found'}), 404
    return jsonify(tower.to_dict())


@app.route('/api/status')
def status():
    usage = ApiUsage.get_today()
    total_towers = CellTower.query.count()
    radio_counts = (
        db.session.query(CellTower.radio, db.func.count(CellTower.id))
        .group_by(CellTower.radio)
        .all()
    )
    return jsonify({
        'api_calls_today': usage.count,
        'api_daily_limit': config.OPENCELLID_DAILY_LIMIT,
        'api_key_configured': bool(config.OPENCELLID_API_KEY),
        'total_towers': total_towers,
        'towers_by_radio': {r: c for r, c in radio_counts},
    })


if __name__ == '__main__':
    import os
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=5001, debug=debug)
