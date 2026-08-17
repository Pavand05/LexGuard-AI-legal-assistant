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


# ==============================================================================
# MULTI-AGENT SYSTEM DATABASE EXTENSIONS (LEXGUARD-MA)
# ==============================================================================

class AgentRun(db.Model):
    __tablename__ = 'agent_runs'

    id            = db.Column(db.Integer, primary_key=True)
    run_id        = db.Column(db.String(64), unique=True, nullable=False, index=True)
    document_id   = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True, index=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workflow_type = db.Column(db.String(50), default='parallel')  # single | sequential | parallel | debate
    status        = db.Column(db.String(50), default='completed')
    latency_ms    = db.Column(db.Integer, default=0)
    health_score  = db.Column(db.Integer, default=100)
    summary_text  = db.Column(db.Text, default='')
    payload_json  = db.Column(db.Text, default='{}')
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    findings = db.relationship('AgentFinding', back_populates='run', cascade='all, delete-orphan')

    def __init__(self, run_id=None, document_id=None, user_id=None, workflow_type='parallel', status='completed', latency_ms=0, health_score=100, summary_text='', payload_json='{}', created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(run_id=run_id, document_id=document_id, user_id=user_id, workflow_type=workflow_type, status=status, latency_ms=latency_ms, health_score=health_score, summary_text=summary_text, payload_json=payload_json, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':            self.id,
            'run_id':        self.run_id,
            'document_id':   self.document_id,
            'user_id':       self.user_id,
            'workflow_type': self.workflow_type,
            'status':        self.status,
            'latency_ms':    self.latency_ms,
            'health_score':  self.health_score,
            'summary_text':  self.summary_text,
            'created_at':    self.created_at.isoformat() if self.created_at else None
        }


class AgentFinding(db.Model):
    __tablename__ = 'agent_findings'

    id              = db.Column(db.Integer, primary_key=True)
    run_id          = db.Column(db.String(64), db.ForeignKey('agent_runs.run_id'), nullable=False, index=True)
    document_id     = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    agent_name      = db.Column(db.String(100), nullable=False)
    dimension       = db.Column(db.String(50), default='Legal')
    risk_level      = db.Column(db.String(50), default='LOW')
    risk_score      = db.Column(db.Integer, default=20)
    clause_type     = db.Column(db.String(100), default='General')
    clause_text     = db.Column(db.Text, default='')
    page_number     = db.Column(db.Integer, default=1)
    reason          = db.Column(db.Text, default='')
    recommendation  = db.Column(db.Text, default='')
    citation_status = db.Column(db.String(50), default='UNVERIFIED')
    confidence      = db.Column(db.Float, default=0.85)

    run = db.relationship('AgentRun', back_populates='findings')

    def __init__(self, run_id=None, document_id=None, agent_name=None, dimension='Legal', risk_level='LOW', risk_score=20, clause_type='General', clause_text='', page_number=1, reason='', recommendation='', citation_status='UNVERIFIED', confidence=0.85, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(run_id=run_id, document_id=document_id, agent_name=agent_name, dimension=dimension, risk_level=risk_level, risk_score=risk_score, clause_type=clause_type, clause_text=clause_text, page_number=page_number, reason=reason, recommendation=recommendation, citation_status=citation_status, confidence=confidence, **kwargs)

    def to_dict(self):
        return {
            'id':              self.id,
            'run_id':          self.run_id,
            'agent_name':      self.agent_name,
            'dimension':       self.dimension,
            'risk_level':      self.risk_level,
            'risk_score':      self.risk_score,
            'clause_type':     self.clause_type,
            'clause_text':     self.clause_text,
            'page_number':     self.page_number,
            'reason':          self.reason,
            'recommendation':  self.recommendation,
            'citation_status': self.citation_status,
            'confidence':      self.confidence
        }


class ContractObligation(db.Model):
    __tablename__ = 'contract_obligations'

    id            = db.Column(db.Integer, primary_key=True)
    document_id   = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True, index=True)
    case_id       = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=True, index=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    party         = db.Column(db.String(150), nullable=False)
    obligation    = db.Column(db.Text, nullable=False)
    deadline      = db.Column(db.String(150), default='Ongoing')
    frequency     = db.Column(db.String(50), default='Event-based')
    trigger_event = db.Column(db.String(255), default='Contract Execution')
    consequence   = db.Column(db.String(255), default='Default & Breach')
    status        = db.Column(db.String(50), default='Upcoming') # Upcoming | Due Soon | Overdue | Completed
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, document_id=None, case_id=None, user_id=None, party=None, obligation=None, deadline='Ongoing', frequency='Event-based', trigger_event='Contract Execution', consequence='Default & Breach', status='Upcoming', created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(document_id=document_id, case_id=case_id, user_id=user_id, party=party, obligation=obligation, deadline=deadline, frequency=frequency, trigger_event=trigger_event, consequence=consequence, status=status, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':            self.id,
            'document_id':   self.document_id,
            'case_id':       self.case_id,
            'party':         self.party,
            'obligation':    self.obligation,
            'deadline':      self.deadline,
            'frequency':     self.frequency,
            'trigger_event': self.trigger_event,
            'consequence':   self.consequence,
            'status':        self.status,
            'created_at':    self.created_at.isoformat() if self.created_at else None
        }


class EvaluationRun(db.Model):
    __tablename__ = 'evaluation_runs'

    id                 = db.Column(db.Integer, primary_key=True)
    pipeline_type      = db.Column(db.String(50), nullable=False) # single | sequential | parallel | debate
    dataset_name       = db.Column(db.String(100), default='Synthetic Legal Benchmark Corpus')
    accuracy           = db.Column(db.Float, default=0.0)
    hallucination_rate = db.Column(db.Float, default=0.0)
    latency_ms         = db.Column(db.Integer, default=0)
    token_count        = db.Column(db.Integer, default=0)
    metrics_json       = db.Column(db.Text, default='{}')
    created_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, pipeline_type=None, dataset_name='Synthetic Legal Benchmark Corpus', accuracy=0.0, hallucination_rate=0.0, latency_ms=0, token_count=0, metrics_json='{}', created_at=None, **kwargs):
        # pyrefly: ignore [unexpected-keyword]
        super().__init__(pipeline_type=pipeline_type, dataset_name=dataset_name, accuracy=accuracy, hallucination_rate=hallucination_rate, latency_ms=latency_ms, token_count=token_count, metrics_json=metrics_json, created_at=created_at, **kwargs)

    def to_dict(self):
        return {
            'id':                 self.id,
            'pipeline_type':      self.pipeline_type,
            'dataset_name':       self.dataset_name,
            'accuracy':           self.accuracy,
            'hallucination_rate': self.hallucination_rate,
            'latency_ms':         self.latency_ms,
            'token_count':        self.token_count,
            'metrics':            json.loads(self.metrics_json) if self.metrics_json else {},
            'created_at':         self.created_at.isoformat() if self.created_at else None
        }
