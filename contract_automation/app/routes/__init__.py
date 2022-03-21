from .contract_add import contract_add_bp
from .index import index_bp

def init_route(app):
    app.register_blueprint(contract_add_bp)
    app.register_blueprint(index_bp)