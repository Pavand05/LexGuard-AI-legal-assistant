import os
import string
import random
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Case, CaseMember, CaseDocument, CaseMessage, AppointmentRequest, AppointmentRejection, Activity

cases_bp = Blueprint('cases_api', __name__)

def generate_case_code():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(6))
        # Ensure code doesn't exist already
        if not Case.query.filter_by(code=code).first():
            return f"CASE-{code}"

def log_user_activity(user_id, action):
    act = Activity(user_id=user_id, action=action)
    db.session.add(act)
    db.session.commit()

# Helper to verify if user is a member of the case
def get_member_or_error(user_id, case_id):
    case = db.session.get(Case, case_id)
    if not case:
        return None, jsonify({"error": "Case not found"}), 404
    
    member = CaseMember.query.filter_by(case_id=case_id, user_id=user_id).first()
    if not member:
        return None, jsonify({"error": "Unauthorized access to this case"}), 403
    
    return case, None, None


# ──────────────────────────────────────────────────────────────────────────────
# CASE ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@cases_bp.route('/cases', methods=['POST'])
@jwt_required()
def create_case():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    role_in_case = (data.get('role') or 'Creator').strip()

    if not title:
        return jsonify({"error": "Case title is required"}), 400

    code = generate_case_code()
    new_case = Case(
        code=code,
        title=title,
        description=description,
        created_by_id=user_id
    )
    db.session.add(new_case)
    db.session.commit()

    # Add creator as the first member
    member = CaseMember(
        case_id=new_case.id,
        user_id=user_id,
        role_in_case=role_in_case
    )
    db.session.add(member)
    db.session.commit()

    log_user_activity(user_id, f"Created new case: '{title}' as a {role_in_case}")

    return jsonify({
        "message": "Case created successfully",
        "case": new_case.to_dict(),
        "role": role_in_case
    }), 201


@cases_bp.route('/cases/join', methods=['POST'])
@jwt_required()
def join_case():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip().upper()
    role_in_case = (data.get('role') or 'Participant').strip()

    if not code:
        return jsonify({"error": "Case code is required"}), 400

    # Handle optional CASE- prefix
    if not code.startswith("CASE-"):
        code = f"CASE-{code}"

    case = Case.query.filter_by(code=code).first()
    if not case:
        return jsonify({"error": "Invalid case code. Case not found"}), 404

    # Check if already a member
    existing_member = CaseMember.query.filter_by(case_id=case.id, user_id=user_id).first()
    if existing_member:
        return jsonify({"error": "You are already a member of this case"}), 400

    # Add member
    member = CaseMember(
        case_id=case.id,
        user_id=user_id,
        role_in_case=role_in_case
    )
    db.session.add(member)
    db.session.commit()

    log_user_activity(user_id, f"Joined case: '{case.title}' as a {role_in_case}")

    return jsonify({
        "message": "Successfully joined the case",
        "case": case.to_dict(),
        "role": role_in_case
    }), 200


@cases_bp.route('/cases', methods=['GET'])
@jwt_required()
def list_cases():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Find all cases this user is a member of
    memberships = CaseMember.query.filter_by(user_id=user_id).all()
    case_ids = [m.case_id for m in memberships]
    
    cases = Case.query.filter(Case.id.in_(case_ids)).order_by(Case.created_at.desc()).all()
    
    result = []
    for c in cases:
        c_dict = c.to_dict()
        # Find current user's role in this case
        m = CaseMember.query.filter_by(case_id=c.id, user_id=user_id).first()
        c_dict['my_role'] = m.role_in_case if m else 'Member'
        
        # Get count of members, documents, messages
        c_dict['members_count'] = len(c.members)
        c_dict['documents_count'] = len(c.documents)
        c_dict['messages_count'] = len(c.messages)
        result.append(c_dict)

    return jsonify({"cases": result})


@cases_bp.route('/cases/<int:case_id>', methods=['GET'])
@jwt_required()
def get_case_details(case_id):
    user_id = int(get_jwt_identity())
    case, err_res, status = get_member_or_error(user_id, case_id)
    if err_res:
        return err_res, status

    case_dict = case.to_dict()
    case_dict['members'] = [m.to_dict() for m in case.members]
    case_dict['documents'] = [d.to_dict() for d in case.documents]
    
    # Get current user's role in case
    m = CaseMember.query.filter_by(case_id=case.id, user_id=user_id).first()
    case_dict['my_role'] = m.role_in_case if m else 'Member'

    return jsonify({"case": case_dict})


# ──────────────────────────────────────────────────────────────────────────────
# CASE DOCUMENTS ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@cases_bp.route('/cases/<int:case_id>/documents', methods=['POST'])
@jwt_required()
def upload_case_document(case_id):
    user_id = int(get_jwt_identity())
    case, err_res, status = get_member_or_error(user_id, case_id)
    if err_res:
        return err_res, status

    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file provided"}), 400

    filename = secure_filename(file.filename)
    
    # Save isolated inside upload folders/cases/<case_id>/
    cases_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cases', str(case_id))
    os.makedirs(cases_upload_dir, exist_ok=True)
    
    # Prepend timestamp to avoid naming collisions
    stored_name = f"{int(datetime.now(timezone.utc).timestamp())}_{filename}"
    file_path = os.path.join(cases_upload_dir, stored_name)
    file.save(file_path)

    case_doc = CaseDocument(
        case_id=case_id,
        user_id=user_id,
        filename=os.path.join('cases', str(case_id), stored_name),
        original_name=file.filename
    )
    db.session.add(case_doc)
    db.session.commit()

    log_user_activity(user_id, f"Uploaded document '{file.filename}' to case '{case.title}'")

    return jsonify({
        "message": "Document uploaded successfully to case",
        "document": case_doc.to_dict()
    }), 201


@cases_bp.route('/cases/<int:case_id>/documents', methods=['GET'])
@jwt_required()
def list_case_documents(case_id):
    user_id = int(get_jwt_identity())
    case, err_res, status = get_member_or_error(user_id, case_id)
    if err_res:
        return err_res, status

    docs = CaseDocument.query.filter_by(case_id=case_id).order_by(CaseDocument.uploaded_at.desc()).all()
    return jsonify({"documents": [d.to_dict() for d in docs]})


# ──────────────────────────────────────────────────────────────────────────────
# CASE MESSAGES / CHAT ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@cases_bp.route('/cases/<int:case_id>/messages', methods=['POST'])
@jwt_required()
def send_case_message(case_id):
    user_id = int(get_jwt_identity())
    case, err_res, status = get_member_or_error(user_id, case_id)
    if err_res:
        return err_res, status

    data = request.get_json(silent=True) or {}
    message_text = (data.get('message') or '').strip()

    if not message_text:
        return jsonify({"error": "Message content cannot be empty"}), 400

    msg = CaseMessage(
        case_id=case_id,
        user_id=user_id,
        message=message_text
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "message": "Message sent",
        "chat_message": msg.to_dict()
    }), 201


@cases_bp.route('/cases/<int:case_id>/messages', methods=['GET'])
@jwt_required()
def list_case_messages(case_id):
    user_id = int(get_jwt_identity())
    case, err_res, status = get_member_or_error(user_id, case_id)
    if err_res:
        return err_res, status

    # Return last 100 messages
    messages = CaseMessage.query.filter_by(case_id=case_id).order_by(CaseMessage.created_at.asc()).limit(100).all()
    return jsonify({"messages": [m.to_dict() for m in messages]})


# ──────────────────────────────────────────────────────────────────────────────
# APPOINTMENT ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@cases_bp.route('/appointments', methods=['POST'])
@jwt_required()
def book_appointment():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'user':
        return jsonify({"error": "Only regular users can book appointments"}), 403

    data = request.get_json(silent=True) or {}
    case_id = data.get('case_id')
    description = (data.get('description') or '').strip()

    if not description:
        return jsonify({"error": "Case description is required for appointment booking"}), 400

    # If case_id is provided, verify ownership/membership
    if case_id is not None:
        case = db.session.get(Case, case_id)
        if not case:
            return jsonify({"error": "Case not found"}), 404
        # Verify user belongs to the case
        member = CaseMember.query.filter_by(case_id=case_id, user_id=user_id).first()
        if not member:
            return jsonify({"error": "You do not belong to this case"}), 403

    # Check if there is already a pending appointment for this case
    if case_id is not None:
        existing = AppointmentRequest.query.filter_by(case_id=case_id, status='pending').first()
        if existing:
            return jsonify({"error": "There is already an open appointment request for this case"}), 400

    appt = AppointmentRequest(
        user_id=user_id,
        case_id=case_id,
        description=description,
        status='pending'
    )
    db.session.add(appt)
    db.session.commit()

    case_name = case.title if case_id else "No Case Consultation"
    log_user_activity(user_id, f"Booked an appointment request for: '{case_name}'")

    return jsonify({
        "message": "Appointment request submitted successfully",
        "appointment": appt.to_dict()
    }), 201


@cases_bp.route('/appointments/mine', methods=['GET'])
@jwt_required()
def my_appointments():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == 'user':
        appts = AppointmentRequest.query.filter_by(user_id=user_id).order_by(AppointmentRequest.created_at.desc()).all()
    else:
        appts = AppointmentRequest.query.filter_by(accepted_by_id=user_id).order_by(AppointmentRequest.created_at.desc()).all()

    return jsonify({"appointments": [a.to_dict() for a in appts]})


@cases_bp.route('/appointments/pending', methods=['GET'])
@jwt_required()
def pending_appointments():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'lawyer':
        return jsonify({"error": "Unauthorized. Only lawyers can view pending appointments"}), 403

    # Get rejected IDs for this lawyer
    rejections = AppointmentRejection.query.filter_by(lawyer_id=user_id).all()
    rejected_ids = [r.appointment_request_id for r in rejections]

    # Find pending appointments that this lawyer hasn't rejected
    query = AppointmentRequest.query.filter_by(status='pending')
    if rejected_ids:
        query = query.filter(AppointmentRequest.id.notin_(rejected_ids))

    appts = query.order_by(AppointmentRequest.created_at.desc()).all()
    return jsonify({"appointments": [a.to_dict() for a in appts]})


@cases_bp.route('/appointments/<int:appt_id>/accept', methods=['POST'])
@jwt_required()
def accept_appointment(appt_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'lawyer':
        return jsonify({"error": "Unauthorized. Only lawyers can accept appointments"}), 403

    appt = db.session.get(AppointmentRequest, appt_id)
    if not appt:
        return jsonify({"error": "Appointment request not found"}), 404

    if appt.status != 'pending':
        return jsonify({"error": "This appointment request is no longer available"}), 400

    # Accept appointment
    appt.status = 'accepted'
    appt.accepted_by_id = user_id

    # If it was associated with an existing case
    if appt.case_id:
        case = db.session.get(Case, appt.case_id)
        if case:
            case.lawyer_id = user_id
            
            # Check if lawyer is already member
            member = CaseMember.query.filter_by(case_id=case.id, user_id=user_id).first()
            if not member:
                member = CaseMember(
                    case_id=case.id,
                    user_id=user_id,
                    role_in_case="Lawyer"
                )
                db.session.add(member)
            db.session.commit()
            
            # Send system message in case chat
            sys_msg = CaseMessage(
                case_id=case.id,
                user_id=user_id,
                message=f"Lawyer {user.name} has joined the case and accepted the appointment request."
            )
            db.session.add(sys_msg)
            
            log_user_activity(appt.user_id, f"Lawyer {user.name} accepted appointment for case '{case.title}'")
    else:
        # Create a new case for this "No Case" appointment
        client = db.session.get(User, appt.user_id)
        client_name = client.name if client else "Client"
        
        case_title = f"Consultation: {client_name}"
        code = generate_case_code()
        
        new_case = Case(
            code=code,
            title=case_title,
            description=f"Consultation booked by user: {appt.description}",
            created_by_id=appt.user_id,
            lawyer_id=user_id
        )
        db.session.add(new_case)
        db.session.commit()

        # Add both members
        m_client = CaseMember(case_id=new_case.id, user_id=appt.user_id, role_in_case="Client")
        m_lawyer = CaseMember(case_id=new_case.id, user_id=user_id, role_in_case="Lawyer")
        db.session.add(m_client)
        db.session.add(m_lawyer)
        db.session.commit()

        # Associate this appt with the new case
        appt.case_id = new_case.id
        db.session.commit()

        sys_msg = CaseMessage(
            case_id=new_case.id,
            user_id=user_id,
            message=f"Consultation case created. Lawyer {user.name} and Client {client_name} are connected."
        )
        db.session.add(sys_msg)

        log_user_activity(appt.user_id, f"Lawyer {user.name} accepted your consultation request. Case '{case_title}' created.")

    log_user_activity(user_id, f"Accepted appointment request #{appt.id} from user ID {appt.user_id}")
    db.session.commit()

    return jsonify({
        "message": "Appointment request accepted successfully",
        "appointment": appt.to_dict()
    }), 200


@cases_bp.route('/appointments/<int:appt_id>/reject', methods=['POST'])
@jwt_required()
def reject_appointment(appt_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'lawyer':
        return jsonify({"error": "Unauthorized. Only lawyers can reject appointments"}), 403

    appt = db.session.get(AppointmentRequest, appt_id)
    if not appt:
        return jsonify({"error": "Appointment request not found"}), 404

    # Record rejection so it is hidden from this lawyer
    rejection = AppointmentRejection(
        appointment_request_id=appt_id,
        lawyer_id=user_id
    )
    db.session.add(rejection)
    db.session.commit()

    log_user_activity(user_id, f"Rejected appointment request #{appt_id}")
    return jsonify({"message": "Appointment request hidden/rejected"}), 200


# ──────────────────────────────────────────────────────────────────────────────
# ACTIVITY ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@cases_bp.route('/activities', methods=['GET'])
@jwt_required()
def list_activities():
    user_id = int(get_jwt_identity())
    acts = Activity.query.filter_by(user_id=user_id).order_by(Activity.created_at.desc()).limit(50).all()
    return jsonify({"activities": [a.to_dict() for a in acts]})


# ──────────────────────────────────────────────────────────────────────────────
# SECURE CASE DOCUMENT DOWNLOAD
# ──────────────────────────────────────────────────────────────────────────────
from flask import send_from_directory

@cases_bp.route('/cases/<int:case_id>/documents/<filename>/download', methods=['GET'])
@jwt_required()
def download_case_document(case_id, filename):
    user_id = int(get_jwt_identity())
    case, err_res, status = get_member_or_error(user_id, case_id)
    if err_res:
        return err_res, status

    cases_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cases', str(case_id))
    return send_from_directory(cases_upload_dir, filename, as_attachment=True)

