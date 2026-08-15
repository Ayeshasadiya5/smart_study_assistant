import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from database.models import db, Subject, StudyMaterial
from services.pdf_processor import validate_pdf_file, generate_safe_filename
from services.rag_service import rag_service
from routes.auth import admin_required
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    materials = StudyMaterial.query.order_by(StudyMaterial.upload_date.desc()).all()
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template(
        'admin_dashboard.html',
        materials=materials,
        subjects=subjects,
        years=Config.YEARS,
        semesters=Config.SEMESTERS,
        material_types=Config.MATERIAL_TYPES,
    )


@admin_bp.route('/add-subject', methods=['POST'])
@login_required
@admin_required
def add_subject():
    name = request.form.get('name', '').strip()
    subject_code = request.form.get('subject_code', '').strip()
    year = request.form.get('year', '').strip()
    semester = request.form.get('semester', '').strip()
    description = request.form.get('description', '').strip()

    if not name or not year or not semester:
        flash('Name, year, and semester are required.', 'danger')
        return redirect(url_for('admin.dashboard'))

    subject = Subject(
        name=name,
        subject_code=subject_code,
        year=year,
        semester=semester,
        description=description,
    )
    db.session.add(subject)
    db.session.commit()
    flash(f'Subject "{name}" added successfully.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload():
    subjects = Subject.query.order_by(Subject.name).all()
    if request.method == 'POST':
        try:
            file = request.files.get('pdf_file')
            validate_pdf_file(file)

            title = request.form.get('title', '').strip()
            year = request.form.get('year', '').strip()
            semester = request.form.get('semester', '').strip()
            subject_id = request.form.get('subject_id', type=int)
            material_type = request.form.get('material_type', '').strip()
            unit = request.form.get('unit', '').strip()
            description = request.form.get('description', '').strip()

            if not title or not year or not semester or not subject_id or not material_type:
                flash('Please fill all required fields.', 'danger')
                return render_template('upload.html', subjects=subjects,
                                       years=Config.YEARS, semesters=Config.SEMESTERS,
                                       material_types=Config.MATERIAL_TYPES)

            subject = Subject.query.get(subject_id)
            if not subject:
                flash('Selected subject not found.', 'danger')
                return redirect(url_for('admin.upload'))

            safe_filename = generate_safe_filename(file.filename)
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(Config.UPLOAD_FOLDER, safe_filename)
            file.save(filepath)

            material = StudyMaterial(
                title=title,
                filename=safe_filename,
                filepath=filepath,
                year=year,
                semester=semester,
                subject_id=subject_id,
                material_type=material_type,
                unit=unit or None,
                description=description,
            )
            db.session.add(material)
            db.session.commit()

            success, message = rag_service.process_material(material.id, filepath, title)
            if success:
                flash(f'PDF uploaded and processed successfully. {message}', 'success')
            else:
                flash(f'PDF uploaded but AI processing note: {message}', 'warning')

            return redirect(url_for('admin.dashboard'))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'danger')

    return render_template(
        'upload.html',
        subjects=subjects,
        years=Config.YEARS,
        semesters=Config.SEMESTERS,
        material_types=Config.MATERIAL_TYPES,
    )


@admin_bp.route('/delete/<int:material_id>', methods=['POST'])
@login_required
@admin_required
def delete_material(material_id):
    material = StudyMaterial.query.get_or_404(material_id)

    if os.path.exists(material.filepath):
        try:
            os.remove(material.filepath)
        except OSError:
            pass

    rag_service.delete_material_store(material.id)
    db.session.delete(material)
    db.session.commit()
    flash('Study material deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))
