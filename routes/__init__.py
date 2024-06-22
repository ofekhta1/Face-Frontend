from flask import Flask

# Import your blueprints
from .home import home_bp
from .search import search_bp
from .template_matching import template_matching_bp
from .check_family import check_family_bp
from .clustering import clustering_bp
from .upload import upload_bp
from .gallery import gallery_bp
from .utils import utils_bp


def register_routes(app: Flask):
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(template_matching_bp)
    app.register_blueprint(check_family_bp)
    app.register_blueprint(clustering_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(utils_bp)
