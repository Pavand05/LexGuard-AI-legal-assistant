import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models import User, Activity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ──────────────────────────────────────────────────────────────────────────────
# POST /auth/register (Client Only)
# Body: { "name": str, "email": str, "password": str }
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    name     = (data.get('name') or '').strip()
    email    = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '')

    if not name or not email or not password:
        return jsonify({'error': 'name, email and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with that email already exists'}), 409

    # Standard registration is always client role and status active
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user    = User(name=name, email=email, password_hash=pw_hash, role='user', status='active')
    db.session.add(user)
    db.session.commit()

    # Log registration activity
    activity = Activity(user_id=user.id, action="Registered account as a User")
    db.session.add(activity)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Account created successfully',
        'token':   token,
        'user':    user.to_dict()
    }), 201


# ──────────────────────────────────────────────────────────────────────────────
# POST /auth/register/lawyer (Multipart Form-Data)
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route('/register/lawyer', methods=['POST'])
def register_lawyer():
    name         = (request.form.get('name') or '').strip()
    email        = (request.form.get('email') or '').strip().lower()
    password     = (request.form.get('password') or '')
    bar_license  = (request.form.get('bar_license') or '').strip()
    jurisdiction = (request.form.get('jurisdiction') or '').strip()

    if not name or not email or not password or not bar_license or not jurisdiction:
        return jsonify({'error': 'name, email, password, bar license and jurisdiction are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with that email already exists'}), 409

    # Handle license file upload
    license_file = request.files.get('license_file')
    if not license_file or not license_file.filename:
        return jsonify({'error': 'Verification document proof file is required'}), 400

    # Ensure secure filename and path
    from werkzeug.utils import secure_filename
    filename = secure_filename(license_file.filename)
    docs_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'verification_docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    # Prepend timestamp to avoid naming collisions
    from datetime import datetime, timezone
    stored_name = f"{int(datetime.now(timezone.utc).timestamp())}_{filename}"
    file_path = os.path.join(docs_dir, stored_name)
    license_file.save(file_path)

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(
        name=name,
        email=email,
        password_hash=pw_hash,
        role='lawyer',
        status='pending_verification',
        bar_license_number=bar_license,
        jurisdiction=jurisdiction,
        license_file_path=stored_name
    )
    db.session.add(user)
    db.session.commit()

    # Log registration activity
    activity = Activity(user_id=user.id, action="Registered account as a Lawyer (Pending Verification)")
    db.session.add(activity)
    db.session.commit()

    # Return success message only; NO login token issued to prevent auto-login
    return jsonify({
        'message': 'Lawyer account registered successfully. It is pending verification by administration.'
    }), 201


# ──────────────────────────────────────────────────────────────────────────────
# POST /auth/login
# Body: { "email": str, "password": str }
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}

    email    = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '')

    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if user.status == 'pending_verification':
        return jsonify({'error': 'Your lawyer account is pending verification by administration.'}), 403
    elif user.status == 'rejected':
        return jsonify({'error': 'Your registration request was rejected by administration.'}), 403

    # Log login activity
    activity = Activity(user_id=user.id, action="Logged into the system")
    db.session.add(activity)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful',
        'token':   token,
        'user':    user.to_dict()
    })


# ──────────────────────────────────────────────────────────────────────────────
# GET /auth/me  (protected)
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})


# ──────────────────────────────────────────────────────────────────────────────
# ADMIN-ONLY ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@auth_bp.route('/admin/pending-lawyers', methods=['GET'])
@jwt_required()
def list_pending_lawyers():
    admin_id = int(get_jwt_identity())
    admin = db.session.get(User, admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'error': 'Unauthorized. Admin access only.'}), 403

    pending = User.query.filter_by(role='lawyer', status='pending_verification').all()
    return jsonify({'pending_lawyers': [u.to_dict() for u in pending]})


@auth_bp.route('/admin/approve-lawyer/<int:user_id>', methods=['POST'])
@jwt_required()
def approve_lawyer(user_id):
    admin_id = int(get_jwt_identity())
    admin = db.session.get(User, admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'error': 'Unauthorized. Admin access only.'}), 403

    lawyer = db.session.get(User, user_id)
    if not lawyer or lawyer.role != 'lawyer':
        return jsonify({'error': 'Lawyer not found'}), 404

    lawyer.status = 'active'
    db.session.commit()

    # Log approval activity
    activity = Activity(user_id=lawyer.id, action="Lawyer account approved and activated by Admin")
    db.session.add(activity)
    db.session.commit()

    return jsonify({'message': f'Lawyer {lawyer.name} has been approved and activated.'})


@auth_bp.route('/admin/reject-lawyer/<int:user_id>', methods=['POST'])
@jwt_required()
def reject_lawyer(user_id):
    admin_id = int(get_jwt_identity())
    admin = db.session.get(User, admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'error': 'Unauthorized. Admin access only.'}), 403

    lawyer = db.session.get(User, user_id)
    if not lawyer or lawyer.role != 'lawyer':
        return jsonify({'error': 'Lawyer not found'}), 404

    lawyer.status = 'rejected'
    db.session.commit()

    # Log rejection activity
    activity = Activity(user_id=lawyer.id, action="Lawyer account registration rejected by Admin")
    db.session.add(activity)
    db.session.commit()

    return jsonify({'message': f'Lawyer {lawyer.name} registration has been rejected.'})


@auth_bp.route('/admin/verification-docs/<filename>', methods=['GET'])
@jwt_required()
def serve_verification_doc(filename):
    admin_id = int(get_jwt_identity())
    admin = db.session.get(User, admin_id)
    if not admin or admin.role != 'admin':
        return jsonify({'error': 'Unauthorized. Admin access only.'}), 403

    docs_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'verification_docs')
    return send_from_directory(docs_dir, filename)
