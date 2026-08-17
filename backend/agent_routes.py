"""
LexGuard-MA Multi-Agent REST API Blueprint
Endpoints:
  POST /agent/analyze                   - Run multi-agent workflow on document text
  GET  /agent/runs                      - List all user agent runs
  GET  /agent/runs/<run_id>             - Get specific agent run details & traces
  POST /agent/obligations               - Store or update contract obligations
  GET  /agent/obligations               - Get all active user/case obligations
  POST /agent/obligations/<id>/status   - Update obligation status
  POST /agent/redlines/<id>/review      - Accept / Reject / Edit redline suggestions
  GET  /agent/evaluation                - Get benchmark comparison metrics
  POST /agent/evaluation/run            - Run automated comparative evaluation benchmark
"""
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Document, AgentRun, AgentFinding, ContractObligation, EvaluationRun
from agents.orchestrator import orchestrator
from evaluation import run_comparative_benchmark


agent_bp = Blueprint('agent_api', __name__, url_prefix='/agent')


@agent_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_with_agents():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    document_text = data.get('text', '').strip()
    filename = data.get('filename', 'document.pdf')
    document_id = data.get('document_id')
    workflow_type = data.get('workflow_type', 'parallel')
    privacy_mode = bool(data.get('privacy_mode', False))
    page_texts = data.get('page_texts', None)

    # If document_id provided without text, fetch from database
    if not document_text and document_id:
        doc = db.session.get(Document, int(document_id))
        if doc and (doc.user_id == user_id or user.role in ['lawyer', 'admin']):
            document_text = doc.text
            filename = doc.original_name

    if not document_text:
        return jsonify({"error": "Document text or valid document_id is required"}), 400

    # Run Multi-Agent Orchestrator
    analysis_result = orchestrator.run_workflow(
        document_text=document_text,
        page_texts=page_texts,
        filename=filename,
        workflow_type=workflow_type,
        privacy_mode=privacy_mode,
        document_id=document_id
    )

    # Persist AgentRun and Findings to database
    try:
        run = AgentRun(
            run_id=analysis_result["run_id"],
            document_id=document_id,
            user_id=user_id,
            workflow_type=workflow_type,
            status="completed",
            latency_ms=analysis_result["total_duration_ms"],
            health_score=analysis_result["contract_health"]["score"],
            summary_text=f"Analyzed by LexGuard-MA ({workflow_type} workflow).",
            payload_json=json.dumps(analysis_result)
        )
        db.session.add(run)
        db.session.commit()

        # Persist structured findings
        for f in analysis_result.get("findings", []):
            finding = AgentFinding(
                run_id=run.run_id,
                document_id=document_id,
                agent_name=f.get("agent_name", "Orchestrator"),
                dimension=f.get("dimension", "Legal"),
                risk_level=f.get("risk_level", "LOW"),
                risk_score=f.get("risk_score", 20),
                clause_type=f.get("clause_type", "General"),
                clause_text=f.get("clause_text", ""),
                page_number=f.get("page_number", 1),
                reason=f.get("reason", ""),
                recommendation=f.get("recommendation", ""),
                citation_status=f.get("citation_status", "UNVERIFIED"),
                confidence=f.get("confidence", 0.85)
            )
            db.session.add(finding)

        # Persist extracted obligations
        for o in analysis_result.get("obligations", []):
            obl = ContractObligation(
                document_id=document_id,
                user_id=user_id,
                party=o.get("party", "Party"),
                obligation=o.get("obligation", ""),
                deadline=o.get("deadline", "Ongoing"),
                frequency=o.get("frequency", "Event-based"),
                trigger_event=o.get("trigger_event", "Contract Execution"),
                consequence=o.get("consequence", "Breach & Damages"),
                status="Upcoming"
            )
            db.session.add(obl)

        db.session.commit()
    except Exception as e:
        print(f"[Agent API] Failed to persist agent run: {e}")
        db.session.rollback()

    return jsonify({
        "message": "Multi-agent analysis completed successfully",
        "result": analysis_result
    }), 200


@agent_bp.route('/runs', methods=['GET'])
@jwt_required()
def list_agent_runs():
    user_id = int(get_jwt_identity())
    runs = AgentRun.query.filter_by(user_id=user_id).order_by(AgentRun.created_at.desc()).limit(20).all()
    return jsonify({"runs": [r.to_dict() for r in runs]}), 200


@agent_bp.route('/runs/<run_id>', methods=['GET'])
@jwt_required()
def get_agent_run(run_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    run = AgentRun.query.filter_by(run_id=run_id).first()
    if not run:
        return jsonify({"error": "Run not found"}), 404
    if run.user_id != user_id and user.role not in ['lawyer', 'admin']:
        return jsonify({"error": "Unauthorized access"}), 403

    payload = json.loads(run.payload_json) if run.payload_json else {}
    return jsonify({"run": run.to_dict(), "details": payload}), 200


@agent_bp.route('/obligations', methods=['GET'])
@jwt_required()
def get_obligations():
    user_id = int(get_jwt_identity())
    doc_id = request.args.get('document_id')
    case_id = request.args.get('case_id')
    
    query = ContractObligation.query.filter_by(user_id=user_id)
    if doc_id:
        query = query.filter_by(document_id=int(doc_id))
    if case_id:
        query = query.filter_by(case_id=int(case_id))
        
    obligations = query.order_by(ContractObligation.created_at.desc()).all()
    return jsonify({"obligations": [o.to_dict() for o in obligations]}), 200


@agent_bp.route('/obligations/<int:obl_id>/status', methods=['POST'])
@jwt_required()
def update_obligation_status(obl_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    new_status = data.get('status', 'Completed')
    
    obl = db.session.get(ContractObligation, obl_id)
    if not obl or obl.user_id != user_id:
        return jsonify({"error": "Obligation not found"}), 404
        
    obl.status = new_status
    db.session.commit()
    return jsonify({"message": "Status updated", "obligation": obl.to_dict()}), 200


@agent_bp.route('/evaluation', methods=['GET'])
def get_evaluation_metrics():
    """Returns comparative metrics comparing Single-Agent vs. Multi-Agent."""
    runs = EvaluationRun.query.order_by(EvaluationRun.created_at.desc()).limit(10).all()
    if not runs:
        # Generate initial benchmark if empty
        metrics = run_comparative_benchmark()
        return jsonify({"evaluations": metrics}), 200
        
    return jsonify({"evaluations": [r.to_dict() for r in runs]}), 200


@agent_bp.route('/evaluation/run', methods=['POST'])
@jwt_required()
def trigger_evaluation_run():
    metrics = run_comparative_benchmark()
    return jsonify({
        "message": "Comparative benchmark evaluation completed",
        "results": metrics
    }), 200
