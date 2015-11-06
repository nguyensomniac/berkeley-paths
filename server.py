from flask import Flask
from app import app
import os
from flask.ext import assets

env = assets.Environment(app)
# Tell flask-assets where to look for our coffeescript and sass files.
env.load_path = [
    os.path.join(os.path.dirname(__file__), 'bower_components'),
    os.path.join(os.path.dirname(__file__), 'app', 'static', 'js'),
    os.path.join(os.path.dirname(__file__), 'app', 'static', 'css')
]


env.register(
    'js_all',
    assets.Bundle(
        'jquery.js',
        'mapbox.js',
        'map.js',
        'survey.js',
        output='all.js'
    )
)

env.register(
    'css_all',
    assets.Bundle(
        'mapbox.js/mapbox.css',
        'skeleton/css/skeleton.css',
        'style.css',
        output='all.css'
    )
)

if __name__ == '__main__':
    app.run(port=8000, debug=True)