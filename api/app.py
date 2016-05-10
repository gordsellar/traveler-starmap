import io
import csv

from flask import (
    Flask,
    send_file,
    jsonify,
    request,
    abort,
    make_response,
)

from flask_cors import CORS

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func

from starmap import generator, map
from starmap.models import db, Subsector, World


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/starmap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


@app.route("/", methods=['POST'])
def new_subsector():
    """
    Generate subsector, store in database
    Should return subsector details

    We need some limit on the number of subectors
    """
    subsector = create_subsector()
    return make_response(jsonify(subsector.to_json()), 201)


@app.route("/search/")
def search():
    """
    Does a search of worlds and subsectors.
    """
    results = []

    query = request.args.get('q', '').strip()
    if not query:
        abort(400)

    query = query + '%'

    subsectors = (
        Subsector.query
        .filter(Subsector.name.ilike(query))
        .order_by(Subsector.name)
        .limit(6)
    )

    for subsector in subsectors:
        results.append({
            'subsector': {
                'id': subsector.id,
                'name': subsector.name,
            },
            'world': None,
        })

    worlds = (
        World.query
        .options(joinedload(World.subsector))
        .filter(World.name.ilike(query))
        .order_by(World.name)
        .limit(6)
    )

    for world in worlds:
        results.append({
            'subsector': {
                'id': world.subsector.id,
                'name': world.subsector.name,
            },
            'world': world.to_json(),
        })

    return jsonify({'results': results})


@app.route("/random/")
def get_random_subsector():
    """
    Returns a random subsector. If no subsectors exist yet,
    then creates a new subsector and returns that.
    """

    status_code = 200
    subsector = Subsector.query.order_by(func.random()).first()

    if subsector is None:
        subsector = create_subsector()
        status_code = 201

    return make_response(jsonify(subsector.to_json()), status_code)


@app.route("/<int:id>/")
def get_subsector_detail(id):
    """
    Returns details for specific subsector
    If format=csv then return details CSV download
    """
    subsector = Subsector.query.get_or_404(id)
    return jsonify(subsector.to_json())


@app.route("/<int:id>/csv/")
def download_csv(id):
    """
    Download details as a CSV
    """
    fp = io.StringIO()
    subsector = Subsector.query.get_or_404(id)

    writer = csv.writer(fp)

    writer.writerow([
        "Name",
        "Coords",
        "UWP",
        "Starport",
        "Travel zone",
        "Size",
        "Atmosphere",
        "Temperature",
        "Hydrographics",
        "Population",
        "Government",
        "Law level",
        "Tech level",
        "Notes",
        "Gas giant?",
        "Scout base?",
        "Naval base?",
        "Research base?",
        "Pirate base?",
        "Traveler's Aid Society?",
        "Imperial consulate?",
    ])

    for world in subsector.worlds:

        writer.writerow([
            world.name,
            world.coords_desc,
            world.uwp,
            world.starport,
            world.travel_zone,
            world.size_desc,
            world.atmosphere_desc,
            world.temperature_desc,
            world.hydrographics_desc,
            world.population_desc,
            world.government_desc,
            world.law_level_desc,
            world.tech_level,
            world.long_trade_classifications,
            yesno(world.is_gas_giant),
            yesno(world.is_scout_base),
            yesno(world.is_naval_base),
            yesno(world.is_research_base),
            yesno(world.is_pirate_base),
            yesno(world.is_tas),
            yesno(world.is_consulate),
        ])

    return send_file(
        io.BytesIO(fp.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='subsector.csv',
    )


@app.route("/<int:id>/map/")
def download_map(id):
    """
    Download map as a PNG
    """
    fp = io.BytesIO()
    subsector = Subsector.query.get_or_404(id)
    map.draw_map(fp, subsector.worlds)
    fp.seek(0)
    return send_file(
        fp,
        mimetype='image/png',
        as_attachment=True,
        attachment_filename='starmap.png',
    )


def create_subsector():
    # if > 1000 return random

    if Subsector.query.count() > 1000:
        return Subsector.query.order_by(func.random()).first()

    # names file should be arg/setting
    subsector = generator.generate_subsector('./names.txt')

    db.session.add(subsector)
    db.session.commit()
    return subsector


def yesno(value):
    return "Yes" if value else "No"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
