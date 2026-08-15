from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file, abort, jsonify
from flask_login import login_required, current_user
from database.models import db, StudyMaterial, SearchHistory
from services.search_service import (
    search_study_materials,
    sanitize_subject_name,
    sanitize_regulation,
    build_web_context_for_ai,
)
from config import Config

student_bp = Blueprint('student', __name__)


def _session_context():
    return {
        'regulation': session.get('selected_regulation'),
        'subject': session.get('selected_subject_name'),
    }


def _store_subject_context(regulation, subject_name):
    session['selected_regulation'] = regulation
    session['selected_subject_name'] = subject_name
    session.pop('selected_subject_id', None)
    session.pop('selected_year', None)
    session.pop('selected_semester', None)


@student_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        'dashboard.html',
        regulations=Config.REGULATIONS,
        session_context=_session_context(),
    )


@student_bp.route('/materials')
@login_required
def materials():
    regulation = request.args.get('regulation', session.get('selected_regulation', '')).strip()
    subject_name = request.args.get('subject_name', session.get('selected_subject_name', '')).strip()

    if regulation and subject_name:
        try:
            subject_name = sanitize_subject_name(subject_name)
            regulation = sanitize_regulation(regulation)
            _store_subject_context(regulation, subject_name)
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('student.dashboard'))

    return render_template(
        'materials.html',
        regulation=regulation,
        subject_name=subject_name,
        auto_search=bool(regulation and subject_name),
        session_context=_session_context(),
    )


@student_bp.route('/api/search-materials')
@login_required
def api_search_materials():
    regulation = request.args.get('regulation', '').strip()
    subject_name = request.args.get('subject_name', '').strip()

    if not regulation or not subject_name:
        return jsonify({
            'success': False,
            'error': 'Regulation and subject name are required.',
        }), 400

    try:
        regulation = sanitize_regulation(regulation)
        subject_name = sanitize_subject_name(subject_name)
        results = search_study_materials(regulation, subject_name, db_session=db.session)
        _store_subject_context(regulation, subject_name)

        session['last_search_results'] = [
            {
                'title': r['title'],
                'description': r.get('description', ''),
                'source': r.get('source', ''),
                'type': r.get('type', ''),
            }
            for r in results[:10]
        ]

        history = SearchHistory(
            user_id=current_user.id,
            year='Not Specified',
            semester='Not Specified',
            regulation=regulation,
            subject_name=subject_name,
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'subject_name': subject_name,
            'regulation': regulation,
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Search failed: {str(e)}'}), 500


@student_bp.route('/view/<int:material_id>')
@login_required
def view_pdf(material_id):
    material = StudyMaterial.query.get_or_404(material_id)
    return render_template(
        'pdf_viewer.html',
        material=material,
        session_context=_session_context(),
    )


@student_bp.route('/serve/<int:material_id>')
@login_required
def serve_pdf(material_id):
    material = StudyMaterial.query.get_or_404(material_id)
    if not material.filepath or not __import__('os').path.exists(material.filepath):
        abort(404)
    return send_file(material.filepath, mimetype='application/pdf')


@student_bp.route('/download/<int:material_id>')
@login_required
def download_pdf(material_id):
    material = StudyMaterial.query.get_or_404(material_id)
    if not material.filepath or not __import__('os').path.exists(material.filepath):
        abort(404)
    return send_file(
        material.filepath,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{material.title}.pdf',
    )


@student_bp.route('/questions')
@login_required
def questions():
    return render_template(
        'questions.html',
        regulations=Config.REGULATIONS,
        session_context=_session_context(),
    )
