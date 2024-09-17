import flask

from flamapy.metamodels.fm_metamodel.transformations import UVLReader, JsonWriter

import utils


# Create the App
app = flask.Flask(__name__,
                  template_folder='templates',
                  static_folder='static',
                  static_url_path='/static')


# Define routes and views
@app.route('/')
def index():
    fm = UVLReader('../models/Pizzas.uvl').transform()
    map = utils.get_data_from_model(fm)
    return flask.render_template('index.html', data=map)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)