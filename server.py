from flask import Flask
from app import app
import os
from flask.ext import assets

env = assets.Environment(app)

# Tell flask-assets where to look for our coffeescript and sass files.
env.load_path = [
    os.path.join(os.path.dirname(__file__), 'bower_components'),
    os.path.join(os.path.dirname(__file__), 'app', 'src')
]

env.register(
    'js_vendor',
    assets.Bundle(
        'jquery/dist/jquery.min.js',
        'underscore/underscore.js',
        'leaflet/dist/leaflet.js',
        'mapbox.js/mapbox.standalone.js',
        filters='jsmin',
        output='vendor.js'
    )
)
env.register(
    'js_app',
    assets.Bundle(
        'js/*.js',
        filters='jsmin',
        output='app.js'
    )
)
env.register(
    'css_all',
    assets.Bundle(
        'skeleton/css/normalize.css',
        'mapbox.js/mapbox.css',
        'skeleton/css/skeleton.css',
        'css/*.css',
        filters='cssmin',
        output='all.css'
    )
)
if __name__ == '__main__':
    app.run(port=8000, debug=True)