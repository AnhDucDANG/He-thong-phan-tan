from flask import Flask
from app.database.connection import init_db
from app.core.config import Config
from app.models.payment_model import Payment

def create_app():
    app = Flask(__name__)
    db = init_db(app)

    @app.route('/')
    def index():
        return "✅ Payment Service connected to SQL Server successfully!"

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="8.0.0.4", port=Config.FLASK_PORT, debug=True)
