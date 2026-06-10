import React, { useState, useEffect } from 'react';
import {
  FileText, Trash2, Loader2, RefreshCw, Calendar,
  AlertTriangle, CheckCircle, XCircle, ChevronRight, FolderOpen
} from 'lucide-react';

const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:5000'
  : '';

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

function RiskBadge({ level, count }) {
  const config = {
    high:   { bg: 'rgba(239, 68, 68, 0.08)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.2)', icon: XCircle },
    medium: { bg: 'rgba(245, 158, 11, 0.08)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.2)', icon: AlertTriangle },
    low:    { bg: 'rgba(16, 185, 129, 0.08)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.2)', icon: CheckCircle },
  };
  const { bg, color, border, icon: Icon } = config[level] || config.low;
  return (
    <span style={{
      background: bg, color, border, borderRadius: '999px',
      padding: '2px 10px', fontSize: '11px', fontWeight: 600,
      display: 'inline-flex', alignItems: 'center', gap: '4px',
      textTransform: 'uppercase', letterSpacing: '0.05em'
    }}>
      <Icon style={{ width: '11px', height: '11px' }} />
      {count} {level}
    </span>
  );
}

export default function DocumentLibrary({ token, onLoadDocument }) {
  const [docs, setDocs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [deleting, setDeleting] = useState(null);
  const [opening, setOpening] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchDocs = async () => {
    setLoading(true);
    setError('');
    try {
      const res  = await fetch(`${API}/documents`, { headers });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to load documents');
      setDocs(data.documents);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocs(); }, []);  // eslint-disable-line

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
    setDeleting(id);
    try {
      const res = await fetch(`${API}/documents/${id}`, { method: 'DELETE', headers });
      if (!res.ok) throw new Error('Delete failed');
      setDocs(prev => prev.filter(d => d.id !== id));
    } catch (e) {
      alert('Could not delete: ' + e.message);
    } finally {
      setDeleting(null);
    }
  };

  const handleOpen = async (doc) => {
    setOpening(doc.id);
    try {
      const res  = await fetch(`${API}/documents/${doc.id}`, { headers });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to load');
      onLoadDocument(data.document);
    } catch (e) {
      alert('Could not load document: ' + e.message);
    } finally {
      setOpening(null);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 0', gap: '12px' }}>
        <Loader2 style={{ width: '36px', height: '36px', color: '#8b5cf6', animation: 'spin 1s linear infinite' }} />
        <p style={{ color: '#94a3b8', fontSize: '14px' }}>Loading your documents…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <p style={{ color: '#f87171', marginBottom: '12px' }}>{error}</p>
        <button onClick={fetchDocs} style={{
          background: 'linear-gradient(135deg,#8b5cf6,#6366f1)', border: 'none',
          borderRadius: '10px', padding: '10px 24px', color: 'white', cursor: 'pointer', fontWeight: 700,
        }}>Retry</button>
      </div>
    );
  }

  if (docs.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 0', color: '#94a3b8' }}>
        <FolderOpen style={{ width: '56px', height: '56px', margin: '0 auto 16px', opacity: 0.3 }} />
        <p style={{ fontSize: '16px', fontWeight: 600, color: '#cbd5e1', marginBottom: '4px' }}>No documents yet</p>
        <p style={{ fontSize: '14px' }}>Upload a legal document to get started.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff', margin: 0 }}>My Documents</h2>
          <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '2px' }}>{docs.length} document{docs.length !== 1 ? 's' : ''} stored</p>
        </div>
        <button onClick={fetchDocs} style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px',
          padding: '8px 16px', cursor: 'pointer', color: '#cbd5e1', fontSize: '13px', fontWeight: 600,
          transition: 'all 0.2s'
        }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
          }}
        >
          <RefreshCw style={{ width: '13px', height: '13px' }} />
          Refresh
        </button>
      </div>

      {/* Document cards */}
      <div style={{ display: 'grid', gap: '16px' }}>
        {docs.map(doc => (
          <div key={doc.id} style={{
            background: 'rgba(15, 23, 42, 0.35)', borderRadius: '16px', padding: '20px 24px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
            display: 'flex', alignItems: 'center', gap: '16px',
            transition: 'all 0.3s ease',
          }}
            onMouseEnter={e => {
              e.currentTarget.style.boxShadow = '0 4px 25px rgba(139, 92, 246, 0.15)';
              e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.3)';
              e.currentTarget.style.background = 'rgba(15, 23, 42, 0.5)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.background = 'rgba(15, 23, 42, 0.35)';
            }}
          >
            {/* File icon */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.05))',
              border: '1px solid rgba(139, 92, 246, 0.25)',
              borderRadius: '12px', padding: '12px', flexShrink: 0,
            }}>
              <FileText style={{ width: '24px', height: '24px', color: '#a78bfa' }} />
            </div>

            {/* Info */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontWeight: 700, color: '#f8fafc', fontSize: '15px', marginBottom: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {doc.original_name}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#94a3b8', fontSize: '12px' }}>
                  <Calendar style={{ width: '11px', height: '11px' }} />
                  {formatDate(doc.uploaded_at)}
                </span>
                {doc.risks && (
                  <>
                    {doc.risks.high   > 0 && <RiskBadge level="high"   count={doc.risks.high} />}
                    {doc.risks.medium > 0 && <RiskBadge level="medium" count={doc.risks.medium} />}
                    {doc.risks.low    > 0 && <RiskBadge level="low"    count={doc.risks.low} />}
                  </>
                )}
              </div>
              {doc.summary && (
                <p style={{ color: '#94a3b8', fontSize: '12px', marginTop: '8px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {doc.summary}
                </p>
              )}
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
              <button
                id={`open-doc-${doc.id}`}
                onClick={() => handleOpen(doc)}
                disabled={!!opening}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                  border: 'none', borderRadius: '10px', padding: '8px 16px',
                  color: 'white', fontSize: '13px', fontWeight: 600, cursor: opening ? 'not-allowed' : 'pointer',
                  opacity: opening === doc.id ? 0.7 : 1,
                  transition: 'all 0.2s',
                  boxShadow: '0 2px 10px rgba(99, 102, 241, 0.15)'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.boxShadow = '0 4px 15px rgba(99, 102, 241, 0.35)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.boxShadow = '0 2px 10px rgba(99, 102, 241, 0.15)';
                }}
              >
                {opening === doc.id
                  ? <Loader2 style={{ width: '13px', height: '13px', animation: 'spin 1s linear infinite' }} />
                  : <ChevronRight style={{ width: '13px', height: '13px' }} />}
                Open
              </button>
              <button
                id={`delete-doc-${doc.id}`}
                onClick={() => handleDelete(doc.id, doc.original_name)}
                disabled={deleting === doc.id}
                style={{
                  display: 'flex', alignItems: 'center',
                  background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '10px',
                  padding: '8px 10px', color: '#f87171', cursor: deleting === doc.id ? 'not-allowed' : 'pointer',
                  opacity: deleting === doc.id ? 0.5 : 1,
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
                  e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'rgba(239, 68, 68, 0.05)';
                  e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.2)';
                }}
              >
                {deleting === doc.id
                  ? <Loader2 style={{ width: '14px', height: '14px', animation: 'spin 1s linear infinite' }} />
                  : <Trash2 style={{ width: '14px', height: '14px' }} />}
              </button>
            </div>
          </div>
        ))}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
