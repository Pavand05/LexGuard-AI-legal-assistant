import json
from datetime import datetime, timezone
from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String(120), nullable=False)
    email               = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash       = db.Column(db.String(255), nullable=False)
    role                = db.Column(db.String(50), default='user', nullable=False) # 'user', 'lawyer', 'admin'
    status              = db.Column(db.String(50), default='active', nullable=False) # 'active', 'pending_verification', 'rejected'
    bar_license_number  = db.Column(db.String(100), nullable=True)
    jurisdiction        = db.Column(db.String(100), nullable=True)
    license_file_path   = db.Column(db.String(255), nullable=True)
    created_at          = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    documents = db.relationship('Document', back_populates='owner',
                                cascade='all, delete-orphan', lazy='dynamic')

    def __init__(self, name=None, email=None, password_hash=None, role='user', status='active', bar_license_number=None, jurisdiction=None, license_file_path=None, created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(name=name, email=email, password_hash=password_hash, role=role, status=status, bar_license_number=bar_license_number, jurisdiction=jurisdiction, license_file_path=license_file_path, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':                  self.id,
            'name':                self.name,
            'email':               self.email,
            'role':                self.role,
            'status':              self.status,
            'bar_license_number':  self.bar_license_number,
            'jurisdiction':        self.jurisdiction,
            'license_file_path':   self.license_file_path,
            'created_at':          self.created_at.isoformat() if self.created_at else None
        }


class Document(db.Model):
    __tablename__ = 'documents'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename      = db.Column(db.String(255), nullable=False)   # stored file path name
    original_name = db.Column(db.String(255), nullable=False)   # user-facing filename
    summary       = db.Column(db.Text, default='')
    clauses_json  = db.Column(db.Text, default='[]')            # JSON-encoded list
    risks_json    = db.Column(db.Text, default='{}')            # JSON-encoded dict
    text          = db.Column(db.Text, default='')
    uploaded_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    owner = db.relationship('User', back_populates='documents')

    def __init__(self, user_id=None, filename=None, original_name=None, summary='', clauses_json='[]', risks_json='{}', text='', uploaded_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(user_id=user_id, filename=filename, original_name=original_name, summary=summary, clauses_json=clauses_json, risks_json=risks_json, text=text, uploaded_at=uploaded_at, **kwargs)

    def get_clauses(self):
        try:
            return json.loads(self.clauses_json)
        except Exception:
            return []

    def set_clauses(self, clauses):
        self.clauses_json = json.dumps(clauses)

    def get_risks(self):
        try:
            return json.loads(self.risks_json)
        except Exception:
            return {}

    def set_risks(self, risks):
        self.risks_json = json.dumps(risks)

    def to_dict(self, include_text=False):
        d = {
            'id':            self.id,
            'original_name': self.original_name,
            'summary':       self.summary,
            'clauses':       self.get_clauses(),
            'risks':         self.get_risks(),
            'uploaded_at':   self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
        if include_text:
            d['text'] = self.text
        return d


class Case(db.Model):
    __tablename__ = 'cases'

    id            = db.Column(db.Integer, primary_key=True)
    code          = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title         = db.Column(db.String(255), nullable=False)
    description   = db.Column(db.Text, default='')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lawyer_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    creator = db.relationship('User', foreign_keys=[created_by_id])
    lawyer  = db.relationship('User', foreign_keys=[lawyer_id])
    members = db.relationship('CaseMember', back_populates='case', cascade='all, delete-orphan')
    documents = db.relationship('CaseDocument', back_populates='case', cascade='all, delete-orphan')
    messages  = db.relationship('CaseMessage', back_populates='case', cascade='all, delete-orphan')

    def __init__(self, code=None, title=None, description='', created_by_id=None, lawyer_id=None, created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(code=code, title=title, description=description, created_by_id=created_by_id, lawyer_id=lawyer_id, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':            self.id,
            'code':          self.code,
            'title':         self.title,
            'description':   self.description,
            'created_by_id': self.created_by_id,
            'lawyer_id':     self.lawyer_id,
            'created_at':    self.created_at.isoformat() if self.created_at else None
        }


class CaseMember(db.Model):
    __tablename__ = 'case_members'

    id           = db.Column(db.Integer, primary_key=True)
    case_id      = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_in_case = db.Column(db.String(100), nullable=False) # e.g. 'tenant', 'landlord', 'lawyer'
    joined_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    case = db.relationship('Case', back_populates='members')
    user = db.relationship('User')

    def __init__(self, case_id=None, user_id=None, role_in_case=None, joined_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(case_id=case_id, user_id=user_id, role_in_case=role_in_case, joined_at=joined_at, **kwargs)

    def to_dict(self):
        return {
            'id':           self.id,
            'case_id':      self.case_id,
            'user_id':      self.user_id,
            'user_name':    self.user.name if self.user else 'Unknown',
            'user_email':   self.user.email if self.user else '',
            'role_in_case': self.role_in_case,
            'joined_at':    self.joined_at.isoformat() if self.joined_at else None
        }


class CaseDocument(db.Model):
    __tablename__ = 'case_documents'

    id            = db.Column(db.Integer, primary_key=True)
    case_id       = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename      = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    uploaded_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    case = db.relationship('Case', back_populates='documents')
    user = db.relationship('User')

    def __init__(self, case_id=None, user_id=None, filename=None, original_name=None, uploaded_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(case_id=case_id, user_id=user_id, filename=filename, original_name=original_name, uploaded_at=uploaded_at, **kwargs)

    def to_dict(self):
        return {
            'id':            self.id,
            'case_id':       self.case_id,
            'user_id':       self.user_id,
            'uploader_name': self.user.name if self.user else 'Unknown',
            'filename':      self.filename,
            'original_name': self.original_name,
            'uploaded_at':   self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class CaseMessage(db.Model):
    __tablename__ = 'case_messages'

    id         = db.Column(db.Integer, primary_key=True)
    case_id    = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    case = db.relationship('Case', back_populates='messages')
    user = db.relationship('User')

    def __init__(self, case_id=None, user_id=None, message=None, created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(case_id=case_id, user_id=user_id, message=message, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':          self.id,
            'case_id':     self.case_id,
            'user_id':     self.user_id,
            'sender_name': self.user.name if self.user else 'Unknown',
            'sender_role': self.user.role if self.user else 'user',
            'message':     self.message,
            'created_at':  self.created_at.isoformat() if self.created_at else None
        }


class AppointmentRequest(db.Model):
    __tablename__ = 'appointment_requests'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    case_id        = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=True)
    description    = db.Column(db.Text, nullable=False)
    status         = db.Column(db.String(50), default='pending', nullable=False) # 'pending' or 'accepted'
    accepted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    client   = db.relationship('User', foreign_keys=[user_id])
    lawyer   = db.relationship('User', foreign_keys=[accepted_by_id])
    case     = db.relationship('Case')

    def __init__(self, user_id=None, case_id=None, description=None, status='pending', accepted_by_id=None, created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(user_id=user_id, case_id=case_id, description=description, status=status, accepted_by_id=accepted_by_id, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':             self.id,
            'user_id':        self.user_id,
            'client_name':    self.client.name if self.client else 'Unknown',
            'case_id':        self.case_id,
            'case_title':     self.case.title if self.case else 'No Case Consultation',
            'description':    self.description,
            'status':         self.status,
            'accepted_by_id': self.accepted_by_id,
            'lawyer_name':    self.lawyer.name if self.lawyer else None,
            'created_at':     self.created_at.isoformat() if self.created_at else None
        }


class AppointmentRejection(db.Model):
    __tablename__ = 'appointment_rejections'

    id                     = db.Column(db.Integer, primary_key=True)
    appointment_request_id = db.Column(db.Integer, db.ForeignKey('appointment_requests.id'), nullable=False)
    lawyer_id              = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rejected_at            = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, appointment_request_id=None, lawyer_id=None, rejected_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(appointment_request_id=appointment_request_id, lawyer_id=lawyer_id, rejected_at=rejected_at, **kwargs)


class Activity(db.Model):
    __tablename__ = 'activities'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action     = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, user_id=None, action=None, created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(user_id=user_id, action=action, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':         self.id,
            'user_id':    self.user_id,
            'action':     self.action,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
