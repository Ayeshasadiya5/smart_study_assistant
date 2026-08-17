from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from backend.database.models import db, ChatHistory
from backend.services.ai_service import ai_service
from backend.services.search_service import (
    sanitize_subject_name,
    sanitize_regulation,
    build_web_context_for_ai,
)

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


def _ai_session_context():
    return {
        'regulation': session.get('selected_regulation'),
        'subject': session.get('selected_subject_name'),
    }


@ai_bp.route('/chat')
@login_required
def chat_page():
    return render_template(
        'chatbot.html',
        session_context=_ai_session_context(),
        ai_enabled=ai_service.enabled,
    )


@ai_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    material_id = data.get('material_id')

    if not question:
        return jsonify({'error': 'Please enter a question.'}), 400

    subject_context = {
        'regulation': session.get('selected_regulation', 'Not selected'),
        'subject': session.get('selected_subject_name', 'Not selected'),
    }

    web_context = ''
    last_results = session.get('last_search_results')
    if last_results:
        web_context = build_web_context_for_ai(last_results)

    result = ai_service.chat(
        question=question,
        subject_context=subject_context,
        material_id=material_id,
        web_context=web_context,
        db_session=db.session,
    )

    chat_entry = ChatHistory(
        user_id=current_user.id,
        subject_name=session.get('selected_subject_name'),
        regulation=session.get('selected_regulation'),
        question=question,
        answer=result['answer'],
    )
    db.session.add(chat_entry)
    db.session.commit()

    return jsonify({
        'answer': result['answer'],
        'sources': result.get('sources', []),
    })


@ai_bp.route('/generate-questions', methods=['POST'])
@login_required
def generate_questions():
    data = request.get_json() or {}
    regulation = data.get('regulation', session.get('selected_regulation', '')).strip()
    subject_name = data.get('subject_name', session.get('selected_subject_name', '')).strip()
    unit = data.get('unit', '').strip()

    try:
        subject_name = sanitize_subject_name(subject_name)
        regulation = sanitize_regulation(regulation)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    session['selected_regulation'] = regulation
    session['selected_subject_name'] = subject_name

    web_context = ''
    last_results = session.get('last_search_results')
    if last_results:
        web_context = build_web_context_for_ai(last_results)

    result = ai_service.generate_questions(
        subject_name=subject_name,
        regulation=regulation,
        unit=unit or None,
        web_context=web_context,
        db_session=db.session,
    )

    if result.get('error'):
        return jsonify({'error': result['error']}), 500

    return jsonify({
        'questions': result['questions'],
        'subject': subject_name,
        'regulation': regulation,
        'unit': unit,
        'label': 'AI-Generated Important Questions',
    })
