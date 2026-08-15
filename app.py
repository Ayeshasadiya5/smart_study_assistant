import os
import sqlalchemy as sa
from sqlalchemy import inspect
from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from flask_login import LoginManager
from config import Config
from database.models import db, User
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp
from routes.ai import ai_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.VECTORSTORE_FOLDER, exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', error='Page not found.', code=404), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', error='Access forbidden.', code=403), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error='Something went wrong.', code=500), 500

    @app.errorhandler(413)
    def too_large(e):
        return render_template('error.html', error='File too large. Maximum size is 16 MB.', code=413), 413

    with app.app_context():
        db.create_all()
        _migrate_schema()
        _seed_admin(app)

    return app


def _migrate_schema():
    """Add new columns/tables for existing SQLite databases."""
    inspector = inspect(db.engine)
    if 'chat_history' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('chat_history')}
        migrations = []
        if 'subject_name' not in cols:
            migrations.append('ALTER TABLE chat_history ADD COLUMN subject_name VARCHAR(200)')
        if 'year' not in cols:
            migrations.append('ALTER TABLE chat_history ADD COLUMN year VARCHAR(50)')
        if 'semester' not in cols:
            migrations.append('ALTER TABLE chat_history ADD COLUMN semester VARCHAR(50)')
        if 'regulation' not in cols:
            migrations.append('ALTER TABLE chat_history ADD COLUMN regulation VARCHAR(20)')
        for sql in migrations:
            try:
                with db.engine.connect() as conn:
                    conn.execute(sa.text(sql))
                    conn.commit()
            except Exception:
                pass

    if 'search_history' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('search_history')}
        if 'regulation' not in cols:
            try:
                with db.engine.connect() as conn:
                    conn.execute(sa.text(
                        'ALTER TABLE search_history ADD COLUMN regulation VARCHAR(20)'
                    ))
                    conn.commit()
            except Exception:
                pass


def _seed_admin(app):
    """Create default admin if none exists."""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@smartnotes.ai',
            role='admin',
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: admin@smartnotes.ai / admin123')


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
