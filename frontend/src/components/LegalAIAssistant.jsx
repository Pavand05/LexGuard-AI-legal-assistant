import React, { useState, useRef, useEffect } from 'react';
import {
  Upload, FileText, MessageCircle, AlertTriangle, Search, Download,
  Eye, CheckCircle, XCircle, Clock, Shield, Scale, Brain, BookOpen,
  ChevronDown, ChevronUp, Loader2, LogOut, User, FolderOpen,
  Plus, Send, Activity, Briefcase, PlusCircle, Users, Link, Check, X, Calendar, FilePlus
} from 'lucide-react';
import DocumentLibrary from './DocumentLibrary';

const API = 'http://localhost:5000';

const LegalAIAssistant = ({ user, token, onLogout }) => {
  // Main sidebar tab state
  // Users: 'analyzer' | 'cases' | 'book_appointment' | 'activity'
  // Lawyers: 'analyzer' | 'cases_dealt' | 'appointments' | 'library' | 'activity'
  const [sidebarTab, setSidebarTab] = useState(user?.role === 'admin' ? 'admin_approvals' : 'analyzer');
  const [pendingLawyers, setPendingLawyers] = useState([]);
  const [pendingLawyersLoading, setPendingLawyersLoading] = useState(false);


  // Sub-tabs for the Document Analyzer
  const [analyzerTab, setAnalyzerTab] = useState('upload');
  
  // Document Analyzer Core State (reused from original)
  const [uploadedFile, setUploadedFile] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [extractedText, setExtractedText] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [documentSummary, setDocumentSummary] = useState('');
  const [analyzerError, setAnalyzerError] = useState(null);
  const [expandedClauses, setExpandedClauses] = useState({});
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  // Compare Docs State (reused from original)
  const [cmpDoc1, setCmpDoc1] = useState(null);
  const [cmpDoc2, setCmpDoc2] = useState(null);
  const [cmpLoading1, setCmpLoading1] = useState(false);
  const [cmpLoading2, setCmpLoading2] = useState(false);
  const [cmpError1, setCmpError1] = useState(null);
  const [cmpError2, setCmpError2] = useState(null);
  const [cmpResult, setCmpResult] = useState(null);
  const cmpFile1Ref = useRef(null);
  const cmpFile2Ref = useRef(null);

  // --- NEW STATES FOR CASES, APPOINTMENTS, AND ACTIVITIES ---
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseMessages, setCaseMessages] = useState([]);
  const [caseDocuments, setCaseDocuments] = useState([]);
  const [caseChatInput, setCaseChatInput] = useState('');
  const [caseLoading, setCaseLoading] = useState(false);

  // Case Modals/Form States
  const [showCreateCase, setShowCreateCase] = useState(false);
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [newCaseDesc, setNewCaseDesc] = useState('');
  const [newCaseRole, setNewCaseRole] = useState('Creator');
  
  const [showJoinCase, setShowJoinCase] = useState(false);
  const [joinCaseCode, setJoinCaseCode] = useState('');
  const [joinCaseRole, setJoinCaseRole] = useState('Participant');

  // Case Document Upload State
  const [caseDocFile, setCaseDocFile] = useState(null);
  const [caseDocUploading, setCaseDocUploading] = useState(false);
  const caseDocInputRef = useRef(null);

  // Appointment State
  const [myAppointments, setMyAppointments] = useState([]);
  const [pendingAppointments, setPendingAppointments] = useState([]);
  const [apptCaseId, setApptCaseId] = useState('');
  const [apptDesc, setApptDesc] = useState('');
  const [apptLoading, setApptLoading] = useState(false);

  // Activity Log State
  const [activities, setActivities] = useState([]);
  const [activityLoading, setActivityLoading] = useState(false);

  // Global Info/Error Toast
  const [toast, setToast] = useState(null);

  // Chat scroll helpers
  const caseChatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  useEffect(() => {
    caseChatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [caseMessages]);

  // Toast Helper
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // ------------------------------------------------------------------
  // EFFECT: Fetch context data based on selected sidebarTab
  // ------------------------------------------------------------------
  useEffect(() => {
    if (sidebarTab === 'cases' || sidebarTab === 'cases_dealt') {
      fetchCases();
      setSelectedCase(null);
    } else if (sidebarTab === 'appointments') {
      fetchPendingAppointments();
      fetchMyAppointments();
    } else if (sidebarTab === 'book_appointment') {
      fetchCases();
      fetchMyAppointments();
    } else if (sidebarTab === 'activity') {
      fetchActivities();
    } else if (sidebarTab === 'admin_approvals') {
      fetchPendingLawyers();
    }
  }, [sidebarTab]);

  // Polling for active case details (chat and documents)
  useEffect(() => {
    let intervalId = null;
    if (selectedCase && (sidebarTab === 'cases' || sidebarTab === 'cases_dealt')) {
      // First fetch
      fetchCaseChatAndDocs(selectedCase.id);
      
      // Setup 3s polling
      intervalId = setInterval(() => {
        pollCaseChatAndDocs(selectedCase.id);
      }, 3000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [selectedCase, sidebarTab]);

  // ------------------------------------------------------------------
  // BACKEND API SERVICE FUNCTIONS
  // ------------------------------------------------------------------
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };

  // -- ADMIN APPROVALS API --
  const fetchPendingLawyers = async () => {
    try {
      setPendingLawyersLoading(true);
      const res = await fetch(`${API}/auth/admin/pending-lawyers`, { headers });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch pending lawyers');
      setPendingLawyers(data.pending_lawyers || []);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setPendingLawyersLoading(false);
    }
  };

  const handleApproveLawyer = async (lawyerId) => {
    if (!window.confirm("Are you sure you want to approve and activate this lawyer?")) return;
    try {
      const res = await fetch(`${API}/auth/admin/approve-lawyer/${lawyerId}`, {
        method: 'POST',
        headers
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to approve lawyer');
      showToast(data.message || 'Lawyer approved successfully!');
      fetchPendingLawyers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleRejectLawyer = async (lawyerId) => {
    if (!window.confirm("Are you sure you want to reject this lawyer's registration?")) return;
    try {
      const res = await fetch(`${API}/auth/admin/reject-lawyer/${lawyerId}`, {
        method: 'POST',
        headers
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to reject lawyer');
      showToast(data.message || 'Lawyer registration rejected.');
      fetchPendingLawyers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // -- CASES API --
  const fetchCases = async () => {
    try {
      setCaseLoading(true);
      const res = await fetch(`${API}/cases`, { headers });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch cases');
      setCases(data.cases);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setCaseLoading(false);
    }
  };

  const handleCreateCase = async (e) => {
    e.preventDefault();
    if (!newCaseTitle.trim()) return;
    try {
      setCaseLoading(true);
      const res = await fetch(`${API}/cases`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          title: newCaseTitle,
          description: newCaseDesc,
          role: newCaseRole
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to create case');
      showToast('Case created successfully!');
      setShowCreateCase(false);
      setNewCaseTitle('');
      setNewCaseDesc('');
      setNewCaseRole('Creator');
      fetchCases();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setCaseLoading(false);
    }
  };

  const handleJoinCase = async (e) => {
    e.preventDefault();
    if (!joinCaseCode.trim()) return;
    try {
      setCaseLoading(true);
      const res = await fetch(`${API}/cases/join`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          code: joinCaseCode,
          role: joinCaseRole
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to join case');
      showToast('Successfully joined the case!');
      setShowJoinCase(false);
      setJoinCaseCode('');
      setJoinCaseRole('Participant');
      fetchCases();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setCaseLoading(false);
    }
  };

  const fetchCaseChatAndDocs = async (caseId) => {
    try {
      const [msgRes, docRes] = await Promise.all([
        fetch(`${API}/cases/${caseId}/messages`, { headers }),
        fetch(`${API}/cases/${caseId}/documents`, { headers })
      ]);
      const msgData = await msgRes.json();
      const docData = await docRes.json();
      
      if (msgRes.ok) setCaseMessages(msgData.messages);
      if (docRes.ok) setCaseDocuments(docData.documents);
    } catch (err) {
      console.error("Error fetching details", err);
    }
  };

  const pollCaseChatAndDocs = async (caseId) => {
    try {
      const msgRes = await fetch(`${API}/cases/${caseId}/messages`, { headers });
      const msgData = await msgRes.json();
      if (msgRes.ok) {
        // Simple comparison to prevent layout shifts if nothing changed
        setCaseMessages(prev => {
          if (JSON.stringify(prev) !== JSON.stringify(msgData.messages)) {
            return msgData.messages;
          }
          return prev;
        });
      }
      
      const docRes = await fetch(`${API}/cases/${caseId}/documents`, { headers });
      const docData = await docRes.json();
      if (docRes.ok) {
        setCaseDocuments(prev => {
          if (JSON.stringify(prev) !== JSON.stringify(docData.documents)) {
            return docData.documents;
          }
          return prev;
        });
      }
    } catch (err) {
      console.error("Polling error", err);
    }
  };

  const handleSendCaseMessage = async (e) => {
    e.preventDefault();
    if (!caseChatInput.trim() || !selectedCase) return;
    const txt = caseChatInput;
    setCaseChatInput('');
    try {
      const res = await fetch(`${API}/cases/${selectedCase.id}/messages`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message: txt })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setCaseMessages(prev => [...prev, data.chat_message]);
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleCaseDocUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !selectedCase) return;
    
    setCaseDocUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/cases/${selectedCase.id}/documents`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }, // No JSON content type
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to upload case document');
      showToast('Document uploaded successfully to case!');
      fetchCaseChatAndDocs(selectedCase.id);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setCaseDocUploading(false);
      if (caseDocInputRef.current) caseDocInputRef.current.value = '';
    }
  };

  // -- APPOINTMENTS API --
  const fetchMyAppointments = async () => {
    try {
      const res = await fetch(`${API}/appointments/mine`, { headers });
      const data = await res.json();
      if (res.ok) setMyAppointments(data.appointments);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPendingAppointments = async () => {
    try {
      const res = await fetch(`${API}/appointments/pending`, { headers });
      const data = await res.json();
      if (res.ok) setPendingAppointments(data.appointments);
    } catch (err) {
      console.error(err);
    }
  };

  const handleBookAppointment = async (e) => {
    e.preventDefault();
    if (!apptDesc.trim()) return;
    try {
      setApptLoading(true);
      const res = await fetch(`${API}/appointments`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          case_id: apptCaseId === 'no_case' || apptCaseId === '' ? null : parseInt(apptCaseId),
          description: apptDesc
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to book appointment');
      showToast('Appointment request sent to all lawyers!');
      setApptDesc('');
      setApptCaseId('');
      fetchMyAppointments();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setApptLoading(false);
    }
  };

  const handleAcceptAppointment = async (apptId) => {
    try {
      const res = await fetch(`${API}/appointments/${apptId}/accept`, {
        method: 'POST',
        headers
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to accept appointment');
      showToast('Appointment accepted! You are added to the case chat.');
      fetchPendingAppointments();
      fetchMyAppointments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  const handleRejectAppointment = async (apptId) => {
    if (!window.confirm("Are you sure you want to hide/reject this request?")) return;
    try {
      const res = await fetch(`${API}/appointments/${apptId}/reject`, {
        method: 'POST',
        headers
      });
      if (!res.ok) throw new Error('Failed to reject');
      showToast('Appointment request hidden.');
      fetchPendingAppointments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // -- ACTIVITIES API --
  const fetchActivities = async () => {
    try {
      setActivityLoading(true);
      const res = await fetch(`${API}/activities`, { headers });
      const data = await res.json();
      if (res.ok) setActivities(data.activities);
    } catch (err) {
      console.error(err);
    } finally {
      setActivityLoading(false);
    }
  };


  // ------------------------------------------------------------------
  // DOCUMENT ANALYZER LOGIC (REUSED FROM ORIGINAL)
  // ------------------------------------------------------------------
  const toggleClauseExpansion = (index) => {
    setExpandedClauses(prev => ({ ...prev, [index]: !prev[index] }));
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    setIsProcessing(true);
    setAnalyzerError(null);

    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type)) {
      setAnalyzerError('Invalid file type. Please upload a PDF, DOCX, or TXT file.');
      setIsProcessing(false);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setAnalyzerError('File size exceeds 10MB limit.');
      setIsProcessing(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API}/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();

      setAnalysisResults({
        clauses: data.analysis.clauses,
        risks: data.analysis.risks,
        processed: true,
        filename: data.analysis.filename
      });
      setDocumentSummary(data.analysis.summary);
      setExtractedText(data.analysis.text);
      setAnalyzerTab("analysis");
      showToast('Document processed successfully!');
    } catch (err) {
      console.error("Upload failed", err);
      setAnalyzerError('Failed to process document. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !extractedText) return;

    const userMessage = { type: 'user', content: inputMessage };
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsProcessing(true);
    
    try {
      const response = await fetch(`${API}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          question: inputMessage,
          document_text: extractedText,
          use_chroma: false
        }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setChatMessages(prev => [...prev, { type: 'ai', content: data.response }]);
    } catch (err) {
      console.error("Chat failed", err);
      setChatMessages(prev => [...prev, { 
        type: 'ai', 
        content: "I'm having trouble processing your question. Please try again." 
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const uploadDocForCompare = async (file, setDoc, setLoading, setErr) => {
    if (!file) return;
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type)) {
      setErr('Invalid file type. Please upload a PDF, DOCX, or TXT file.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErr('File size exceeds 10 MB limit.');
      return;
    }
    setLoading(true);
    setErr(null);
    setCmpResult(null);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const res = await fetch(`${API}/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDoc({ file, analysis: data.analysis, summary: data.analysis.summary });
      showToast(`Uploaded ${file.name}`);
    } catch (e) {
      setErr('Failed to process document: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const buildComparison = () => {
    if (!cmpDoc1 || !cmpDoc2) return;
    const c1 = cmpDoc1.analysis.clauses || [];
    const c2 = cmpDoc2.analysis.clauses || [];
    const types1 = new Set(c1.map(c => c.type));
    const types2 = new Set(c2.map(c => c.type));
    const allTypes = new Set([...types1, ...types2]);

    const rows = [];
    allTypes.forEach(type => {
      const inDoc1 = types1.has(type);
      const inDoc2 = types2.has(type);
      const clause1 = c1.find(c => c.type === type);
      const clause2 = c2.find(c => c.type === type);
      rows.push({
        type,
        inDoc1,
        inDoc2,
        risk1: clause1?.risk || null,
        risk2: clause2?.risk || null,
        content1: clause1?.content || null,
        content2: clause2?.content || null,
        status: inDoc1 && inDoc2 ? 'shared' : inDoc1 ? 'only1' : 'only2'
      });
    });

    const shared = rows.filter(r => r.status === 'shared').length;
    const only1  = rows.filter(r => r.status === 'only1').length;
    const only2  = rows.filter(r => r.status === 'only2').length;
    setCmpResult({ rows, shared, only1, only2 });
  };

  const exportComparison = () => {
    if (!cmpResult || !cmpDoc1 || !cmpDoc2) return;
    const payload = {
      generatedAt: new Date().toISOString(),
      document1: { filename: cmpDoc1.file.name, summary: cmpDoc1.summary, risks: cmpDoc1.analysis.risks },
      document2: { filename: cmpDoc2.file.name, summary: cmpDoc2.summary, risks: cmpDoc2.analysis.risks },
      comparison: cmpResult
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `comparison-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
  };

  const handleExport = () => {
    if (!analysisResults) return;
    const exportData = {
      summary: documentSummary,
      clauses: analysisResults.clauses,
      risks: analysisResults.risks,
      filename: uploadedFile?.name || 'unknown',
      timestamp: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `legal-analysis-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  const getRiskBadgeColor = (risk) => {
    switch (risk) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskIcon = (risk) => {
    switch (risk) {
      case 'high': return <XCircle className="w-4 h-4" />;
      case 'medium': return <AlertTriangle className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const handleLoadFromLibrary = (doc) => {
    setAnalysisResults({
      id:       doc.id,
      clauses:  doc.clauses,
      risks:    doc.risks,
      processed: true,
      filename: doc.original_name,
    });
    setDocumentSummary(doc.summary || '');
    setExtractedText(doc.text || '');
    setUploadedFile({ name: doc.original_name, type: '', size: 0 });
    setChatMessages([]);
    setSidebarTab('analyzer');
    setAnalyzerTab('analysis');
  };

  const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); };
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      const event = { target: { files: [file] } };
      handleFileUpload(event);
    }
  };

  // Helper date formatter
  const formatDate = (isoStr) => {
    if (!isoStr) return '';
    return new Date(isoStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* ── TOAST MESSAGES ── */}
      {toast && (
        <div 
          className={`fixed top-4 right-4 z-50 flex items-center space-x-2 px-4 py-3 rounded-xl shadow-2xl border text-sm font-medium animate-bounce ${
            toast.type === 'error' 
              ? 'bg-red-950/80 border-red-800 text-red-200' 
              : 'bg-emerald-950/80 border-emerald-800 text-emerald-200'
          }`}
          style={{ backdropFilter: 'blur(10px)' }}
        >
          {toast.type === 'error' ? <AlertTriangle className="w-4 h-4 text-red-400" /> : <CheckCircle className="w-4 h-4 text-emerald-400" />}
          <span>{toast.message}</span>
        </div>
      )}

      {/* ── SIDEBAR PANEL ── */}
      <aside 
        className="w-80 flex flex-col justify-between p-6 border-r border-slate-800 flex-shrink-0"
        style={{ background: 'linear-gradient(180deg, #090911 0%, #111124 100%)' }}
      >
        <div className="space-y-8">
          {/* Brand Header */}
          <div className="flex items-center space-x-3">
            <div style={{ background: 'linear-gradient(135deg, #8b5cf6, #6366f1)', borderRadius: '10px', padding: '8px' }}>
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-lg leading-tight">LexGuard</h2>
              <span className="text-xs text-purple-400 font-semibold uppercase tracking-wider">{user?.role} MODE</span>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="space-y-1">
            {/* ADMIN ONLY: Pending Approvals */}
            {user?.role === 'admin' && (
              <button
                onClick={() => setSidebarTab('admin_approvals')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'admin_approvals'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <Shield className="w-5 h-5" />
                <span>Pending Approvals</span>
              </button>
            )}

            {/* COMMON: Document Analyzer (Non-admin) */}
            {user?.role !== 'admin' && (
              <button
                onClick={() => setSidebarTab('analyzer')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'analyzer'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <Brain className="w-5 h-5" />
                <span>Legal Document Analyzer</span>
              </button>
            )}

            {/* USER ONLY: Cases List & Action */}
            {user?.role === 'user' && (
              <button
                onClick={() => setSidebarTab('cases')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'cases'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <Briefcase className="w-5 h-5" />
                <span>My Cases</span>
              </button>
            )}

            {/* LAWYER ONLY: Cases Dealt */}
            {user?.role === 'lawyer' && (
              <button
                onClick={() => setSidebarTab('cases_dealt')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'cases_dealt'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <Briefcase className="w-5 h-5" />
                <span>Cases Dealt</span>
              </button>
            )}

            {/* USER ONLY: Book Appointment */}
            {user?.role === 'user' && (
              <button
                onClick={() => setSidebarTab('book_appointment')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'book_appointment'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <Calendar className="w-5 h-5" />
                <span>Book Appointment</span>
              </button>
            )}

            {/* LAWYER ONLY: Appointments Review */}
            {user?.role === 'lawyer' && (
              <button
                onClick={() => setSidebarTab('appointments')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'appointments'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <Calendar className="w-5 h-5" />
                <span>Appointments</span>
              </button>
            )}

            {/* LAWYER ONLY: Separate Store Documents */}
            {user?.role === 'lawyer' && (
              <button
                onClick={() => setSidebarTab('library')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  sidebarTab === 'library'
                    ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`}
              >
                <FolderOpen className="w-5 h-5" />
                <span>Store Documents</span>
              </button>
            )}

            {/* COMMON: Activity Logs */}
            <button
              onClick={() => setSidebarTab('activity')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                sidebarTab === 'activity'
                  ? 'bg-purple-600/25 border-l-4 border-purple-500 text-white'
                  : 'text-slate-400 hover:bg-slate-900 hover:text-white'
              }`}
            >
              <Activity className="w-5 h-5" />
              <span>Activity Log</span>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer (User info & Logout) */}
        <div className="space-y-4 pt-6 border-t border-slate-800">
          <div className="flex items-center space-x-3 bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <div className="bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full p-2 flex-shrink-0">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-white truncate">{user?.name}</p>
              <p className="text-xs text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>

          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl text-sm font-medium bg-red-950/20 hover:bg-red-950/40 text-red-400 hover:text-red-300 border border-red-900/30 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* ── MAIN CONTENT WORKSPACE ── */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-900/40 overflow-y-auto">
        
        {/* Top Navbar */}
        <header className="px-8 py-5 border-b border-slate-800 bg-slate-950/20 flex justify-between items-center backdrop-blur-md sticky top-0 z-30">
          <h2 className="text-xl font-bold text-white tracking-wide">
            {sidebarTab === 'admin_approvals' && "Lawyer Verification Approvals"}
            {sidebarTab === 'analyzer' && "Legal Document Analyzer"}
            {(sidebarTab === 'cases' || sidebarTab === 'cases_dealt') && "Case Management Collaboration"}
            {sidebarTab === 'book_appointment' && "Book Legal Consultations"}
            {sidebarTab === 'appointments' && "Appointment Requests"}
            {sidebarTab === 'library' && "Document Library Storage"}
            {sidebarTab === 'activity' && "User Operation Logs"}
          </h2>
          <div className="flex items-center space-x-4">
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700">Beta v1.1</span>
          </div>
        </header>

        {/* Workspace Inner Content Container */}
        <div className="p-8 flex-1">

          {/* ================================================================
              VIEW: ADMIN APPROVAL PANEL
              ================================================================ */}
          {sidebarTab === 'admin_approvals' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                <div className="pb-3 border-b border-slate-800 flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-white">Pending Lawyer Registrations</h3>
                    <p className="text-slate-400 text-xs mt-0.5">Verify lawyer credentials, Bar License Numbers, and review uploaded certificates before approval.</p>
                  </div>
                  <button 
                    onClick={fetchPendingLawyers} 
                    className="text-[10px] font-bold text-slate-400 hover:text-white bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
                  >
                    Refresh List
                  </button>
                </div>

                {pendingLawyersLoading ? (
                  <div className="flex justify-center py-16">
                    <Loader2 className="animate-spin h-8 w-8 text-purple-400" />
                  </div>
                ) : pendingLawyers.length === 0 ? (
                  <div className="text-center py-16 space-y-3">
                    <Shield className="mx-auto w-12 h-12 text-slate-700" />
                    <h4 className="font-bold text-white text-base">All caught up!</h4>
                    <p className="text-slate-500 text-xs max-w-xs mx-auto">No lawyers are currently awaiting verification.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                          <th className="py-3 px-4">Name</th>
                          <th className="py-3 px-4">Email</th>
                          <th className="py-3 px-4">Bar License</th>
                          <th className="py-3 px-4">Jurisdiction</th>
                          <th className="py-3 px-4">Document Proof</th>
                          <th className="py-3 px-4 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-850/60">
                        {pendingLawyers.map(lawyer => (
                          <tr key={lawyer.id} className="hover:bg-slate-850/20 transition-colors">
                            <td className="py-4 px-4 font-bold text-slate-200">{lawyer.name}</td>
                            <td className="py-4 px-4 text-slate-400 font-mono">{lawyer.email}</td>
                            <td className="py-4 px-4 text-purple-400 font-semibold">{lawyer.bar_license_number}</td>
                            <td className="py-4 px-4 text-slate-300">{lawyer.jurisdiction}</td>
                            <td className="py-4 px-4">
                              {lawyer.license_file_path ? (
                                <a
                                  href={`${API}/auth/admin/verification-docs/${lawyer.license_file_path}?token=${token}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 bg-indigo-950/40 border border-indigo-900/40 px-2.5 py-1 rounded-lg transition-colors font-medium"
                                >
                                  <Download className="w-3 h-3" />
                                  <span>View Certificate</span>
                                </a>
                              ) : (
                                <span className="text-slate-600 italic">No document</span>
                              )}
                            </td>
                            <td className="py-4 px-4 text-right space-x-2">
                              <button
                                onClick={() => handleRejectLawyer(lawyer.id)}
                                className="px-3 py-1.5 bg-red-950/40 hover:bg-red-900/20 text-red-400 hover:text-red-300 border border-red-900/30 rounded-lg transition-colors font-semibold"
                              >
                                Reject
                              </button>
                              <button
                                onClick={() => handleApproveLawyer(lawyer.id)}
                                className="px-3 py-1.5 bg-emerald-950/40 hover:bg-emerald-900/20 text-emerald-400 hover:text-emerald-300 border border-emerald-900/30 rounded-lg transition-colors font-bold shadow-md shadow-emerald-950/20"
                              >
                                Approve & Activate
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ================================================================
              VIEW: LEGAL DOCUMENT ANALYZER (REUSES OLD MAIN VIEW AS A VIEW TABS)
              ================================================================ */}
          {sidebarTab === 'analyzer' && (
            <div className="space-y-6">
              {/* Document Analyzer Sub-navigation */}
              <div className="flex border-b border-slate-800 overflow-x-auto gap-4 pb-0.5">
                {[
                  { id: 'upload',     label: 'Upload Document',   icon: Upload },
                  { id: 'analysis',   label: 'Risk Analysis Report',  icon: FileText },
                  { id: 'chat',       label: 'Chat with AI',           icon: MessageCircle },
                  { id: 'compare',    label: 'Compare Contracts',        icon: Eye },
                  { id: 'library',    label: 'Analyzer History',        icon: FolderOpen },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setAnalyzerTab(tab.id)}
                    className={`flex items-center space-x-2 py-3 px-4 border-b-2 font-medium text-sm whitespace-nowrap transition-all ${
                      analyzerTab === tab.id
                        ? 'border-purple-500 text-purple-400 bg-purple-500/5 rounded-t-lg'
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* Analyzer Tab: Upload */}
              {analyzerTab === 'upload' && (
                <div className="text-center space-y-6 max-w-xl mx-auto py-12">
                  <h3 className="text-2xl font-bold text-white">Extract & Analyze Clauses Instantly</h3>
                  <p className="text-slate-400 text-sm">Upload your legal documents (PDF, DOCX, TXT) and let LexGuard review clauses for severe, medium, and low risks.</p>
                  
                  {analyzerError && (
                    <div className="bg-red-950/40 border border-red-900 rounded-xl p-4 flex items-center space-x-3 text-red-200 text-sm">
                      <XCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                      <span>{analyzerError}</span>
                    </div>
                  )}
                  
                  <div
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 hover:border-purple-500 bg-slate-950/40 hover:bg-purple-950/5 rounded-2xl p-16 cursor-pointer transition-all flex flex-col items-center justify-center space-y-4"
                  >
                    <Upload className="h-12 w-12 text-slate-500 group-hover:text-purple-400" />
                    <h4 className="text-base font-semibold text-slate-200">
                      {uploadedFile ? uploadedFile.name : 'Click to select or drag and drop document'}
                    </h4>
                    <p className="text-slate-500 text-xs">PDF, DOCX, TXT formats up to 10MB supported</p>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </div>
                  
                  {isProcessing && (
                    <div className="flex flex-col items-center space-y-2 text-purple-400 justify-center">
                      <Loader2 className="animate-spin h-6 w-6" />
                      <span className="text-xs font-semibold uppercase tracking-wider">Reviewing contract with AI...</span>
                    </div>
                  )}
                  
                  {uploadedFile && !isProcessing && analysisResults && (
                    <button
                      onClick={() => setAnalyzerTab('analysis')}
                      className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-6 py-2.5 rounded-xl font-semibold text-sm transition-all"
                    >
                      View Risk Analysis Report
                    </button>
                  )}
                </div>
              )}

              {/* Analyzer Tab: Analysis Report */}
              {analyzerTab === 'analysis' && (
                <div className="space-y-6">
                  {analysisResults ? (
                    <>
                      {/* Document Summary */}
                      {documentSummary && (
                        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-3">
                          <div className="flex items-center space-x-2 text-purple-400">
                            <BookOpen className="w-5 h-5" />
                            <h3 className="font-bold text-lg text-white">AI Summary Overview</h3>
                          </div>
                          <p className="text-slate-300 text-sm leading-relaxed bg-slate-950/40 p-4 rounded-xl border border-slate-900">{documentSummary}</p>
                        </div>
                      )}

                      {/* Dashboard Counter Cards */}
                      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
                        <div className="flex justify-between items-center">
                          <h3 className="font-bold text-lg text-white">Risk Profiles Count</h3>
                          <div className="flex space-x-2">
                            <button 
                              onClick={() => setAnalyzerTab('chat')}
                              className="text-xs bg-purple-950/60 border border-purple-800 text-purple-200 px-4 py-2 rounded-xl hover:bg-purple-900 transition-colors flex items-center space-x-1 font-semibold"
                            >
                              <MessageCircle className="w-3.5 h-3.5" />
                              <span>Consult chatbot</span>
                            </button>
                            <button 
                              onClick={handleExport}
                              className="text-xs bg-emerald-950/60 border border-emerald-800 text-emerald-200 px-4 py-2 rounded-xl hover:bg-emerald-900 transition-colors flex items-center space-x-1 font-semibold"
                            >
                              <Download className="w-3.5 h-3.5" />
                              <span>Export Report (JSON)</span>
                            </button>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                          {[
                            { label: 'High Risk Issues', icon: <XCircle className="text-red-400" />, count: analysisResults.risks.high, bg: 'bg-red-950/20', border: 'border-red-900/40', text: 'text-red-200' },
                            { label: 'Medium Risk Issues', icon: <AlertTriangle className="text-amber-400" />, count: analysisResults.risks.medium, bg: 'bg-amber-950/20', border: 'border-amber-900/40', text: 'text-amber-200' },
                            { label: 'Low Risk items', icon: <CheckCircle className="text-emerald-400" />, count: analysisResults.risks.low, bg: 'bg-emerald-950/20', border: 'border-emerald-900/40', text: 'text-emerald-200' },
                            { label: 'Total Scanned Clauses', icon: <FileText className="text-purple-400" />, count: analysisResults.risks.total, bg: 'bg-purple-950/20', border: 'border-purple-900/40', text: 'text-purple-200' }
                          ].map((item, idx) => (
                            <div key={idx} className={`${item.bg} ${item.border} border rounded-xl p-4 flex flex-col justify-between`}>
                              <div className="flex items-center space-x-2 text-sm font-medium text-slate-300">
                                {item.icon}
                                <span>{item.label}</span>
                              </div>
                              <div className="text-3xl font-extrabold text-white mt-2">{item.count}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Detected Clauses List */}
                      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
                        <h3 className="font-bold text-lg text-white">Extracted Clauses & Classifications</h3>
                        {analysisResults.clauses.length > 0 ? (
                          <div className="space-y-4">
                            {analysisResults.clauses.map((clause, idx) => (
                              <div key={idx} className="border border-slate-800 bg-slate-950/20 rounded-xl p-4 hover:border-slate-700 transition-colors">
                                <div className="flex justify-between items-start mb-2">
                                  <div className="flex items-center space-x-2">
                                    <span className="font-semibold text-slate-100 text-sm">{clause.type}</span>
                                    <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getRiskBadgeColor(clause.risk)}`}>
                                      {getRiskIcon(clause.risk)}
                                      <span className="uppercase tracking-wider ml-1">{clause.risk}</span>
                                    </span>
                                  </div>
                                  <div className="flex items-center space-x-2 text-xs text-slate-500 font-semibold">
                                    <span>Page {clause.page}</span>
                                    <button 
                                      onClick={() => toggleClauseExpansion(idx)}
                                      className="text-slate-400 hover:text-white"
                                    >
                                      {expandedClauses[idx] ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                    </button>
                                  </div>
                                </div>
                                <p className="text-slate-400 text-xs leading-relaxed">{clause.description}</p>
                                {expandedClauses[idx] && (
                                  <div className="mt-3 bg-slate-950 p-4 rounded-lg border border-slate-800">
                                    <p className="text-xs text-slate-300 font-mono whitespace-pre-wrap">{clause.content}</p>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center text-slate-500 py-12">
                            <Brain className="mx-auto w-12 h-12 text-slate-600 mb-3" />
                            <p className="text-sm">No specific clauses identified in this document.</p>
                          </div>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="text-center text-slate-500 py-16">
                      <FileText className="mx-auto w-12 h-12 text-slate-600 mb-3" />
                      <p className="text-sm">No analysis history selected. Upload a file or review analyzer history.</p>
                      <button
                        onClick={() => setAnalyzerTab('upload')}
                        className="mt-4 text-xs bg-purple-600 hover:bg-purple-500 px-4 py-2 rounded-xl text-white font-semibold transition-colors"
                      >
                        Upload Document
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Analyzer Tab: Chat with Document */}
              {analyzerTab === 'chat' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex flex-col h-[550px]">
                    <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                      <div>
                        <h4 className="font-bold text-white text-sm">RAG AI Q&A Chatroom</h4>
                        <p className="text-slate-500 text-xs mt-0.5">
                          {extractedText ? `Document Context: ${uploadedFile?.name}` : "Upload a contract to enable Q&A context"}
                        </p>
                      </div>
                    </div>
                    
                    {/* Chat Messages */}
                    <div className="flex-1 p-4 overflow-y-auto space-y-4">
                      {chatMessages.length === 0 ? (
                        <div className="h-full flex flex-col justify-center items-center text-slate-500 text-center px-6">
                          <MessageCircle className="w-10 h-10 text-slate-700 mb-3" />
                          <p className="text-sm font-semibold">Start discussing the contract</p>
                          <p className="text-xs text-slate-600 max-w-xs mt-1">Ask questions like "What are the termination conditions?" or "Is there a non-compete clause?"</p>
                        </div>
                      ) : (
                        chatMessages.map((msg, idx) => (
                          <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl text-xs leading-relaxed ${
                              msg.type === 'user' 
                                ? 'bg-purple-600 text-white rounded-br-none' 
                                : 'bg-slate-850 text-slate-200 border border-slate-800 rounded-bl-none'
                            }`}>
                              {msg.content}
                            </div>
                          </div>
                        ))
                      )}
                      {isProcessing && (
                        <div className="flex justify-start">
                          <div className="bg-slate-850 border border-slate-800 text-slate-300 px-4 py-3 rounded-2xl rounded-bl-none text-xs flex items-center space-x-2">
                            <Loader2 className="animate-spin h-3.5 w-3.5 text-purple-400" />
                            <span>AI is searching document context...</span>
                          </div>
                        </div>
                      )}
                      <div ref={chatEndRef} />
                    </div>
                    
                    {/* Chat Input */}
                    <div className="p-4 border-t border-slate-800">
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={inputMessage}
                          onChange={e => setInputMessage(e.target.value)}
                          onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                          disabled={!extractedText || isProcessing}
                          placeholder={extractedText ? "Ask anything about the contract..." : "Please upload a document to enable chat"}
                          className="flex-1 bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-purple-600 disabled:opacity-50"
                        />
                        <button
                          onClick={handleSendMessage}
                          disabled={!inputMessage.trim() || isProcessing}
                          className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-850 text-white p-2.5 rounded-xl transition-all"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Right panel: Extracted text preview */}
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-4 flex flex-col h-[550px]">
                    <h4 className="font-bold text-white text-sm mb-2 flex items-center space-x-1.5">
                      <FileText className="w-4 h-4 text-purple-400" />
                      <span>Extracted Context Material</span>
                    </h4>
                    {extractedText ? (
                      <div className="flex-1 bg-slate-955 p-3 rounded-xl border border-slate-850 overflow-y-auto text-xs text-slate-400 leading-relaxed font-mono whitespace-pre-wrap">
                        {extractedText}
                      </div>
                    ) : (
                      <div className="flex-1 flex flex-col items-center justify-center text-slate-600 text-center px-4">
                        <Scale className="w-8 h-8 text-slate-800 mb-2" />
                        <p className="text-xs">No contract context loaded. Complete upload process first.</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Analyzer Tab: Compare Contracts */}
              {analyzerTab === 'compare' && (
                <div className="space-y-6">
                  {/* File Upload Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Document 1 Selector */}
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">📄 Contract Document 1</span>
                        {cmpDoc1 && <span className="text-xs text-purple-400 font-medium">Loaded</span>}
                      </div>
                      
                      {cmpDoc1 ? (
                        <div className="bg-slate-950 p-3 rounded-xl border border-slate-850 flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-200 truncate max-w-xs">{cmpDoc1.file.name}</span>
                          <button onClick={() => setCmpDoc1(null)} className="text-red-400 hover:text-red-300"><X className="w-4 h-4" /></button>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <button 
                            onClick={() => cmpFile1Ref.current?.click()} 
                            disabled={cmpLoading1}
                            className="w-full py-4 border border-dashed border-slate-700 hover:border-purple-500 bg-slate-950/40 rounded-xl text-xs text-slate-400 font-semibold flex items-center justify-center space-x-2"
                          >
                            {cmpLoading1 ? <Loader2 className="animate-spin w-4 h-4" /> : <FilePlus className="w-4 h-4" />}
                            <span>Select Document 1</span>
                          </button>
                          <input ref={cmpFile1Ref} type="file" className="hidden" onChange={e => uploadDocForCompare(e.target.files[0], setCmpDoc1, setCmpLoading1, setCmpError1)} />
                        </div>
                      )}
                      {cmpError1 && <p className="text-xs text-red-400">{cmpError1}</p>}
                    </div>

                    {/* Document 2 Selector */}
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">📄 Contract Document 2</span>
                        {cmpDoc2 && <span className="text-xs text-purple-400 font-medium">Loaded</span>}
                      </div>
                      
                      {cmpDoc2 ? (
                        <div className="bg-slate-950 p-3 rounded-xl border border-slate-850 flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-200 truncate max-w-xs">{cmpDoc2.file.name}</span>
                          <button onClick={() => setCmpDoc2(null)} className="text-red-400 hover:text-red-300"><X className="w-4 h-4" /></button>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <button 
                            onClick={() => cmpFile2Ref.current?.click()} 
                            disabled={cmpLoading2}
                            className="w-full py-4 border border-dashed border-slate-700 hover:border-purple-500 bg-slate-950/40 rounded-xl text-xs text-slate-400 font-semibold flex items-center justify-center space-x-2"
                          >
                            {cmpLoading2 ? <Loader2 className="animate-spin w-4 h-4" /> : <FilePlus className="w-4 h-4" />}
                            <span>Select Document 2</span>
                          </button>
                          <input ref={cmpFile2Ref} type="file" className="hidden" onChange={e => uploadDocForCompare(e.target.files[0], setCmpDoc2, setCmpLoading2, setCmpError2)} />
                        </div>
                      )}
                      {cmpError2 && <p className="text-xs text-red-400">{cmpError2}</p>}
                    </div>
                  </div>

                  {cmpDoc1 && cmpDoc2 && !cmpResult && (
                    <div className="text-center">
                      <button
                        onClick={buildComparison}
                        className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-8 py-3 rounded-xl font-bold text-sm transition-all shadow-xl"
                      >
                        Compute Clause-by-Clause Comparison
                      </button>
                    </div>
                  )}

                  {/* Side by Side Comparison Results */}
                  {cmpResult && (
                    <div className="space-y-6">
                      {/* Shared / Distinct Stats */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {[
                          { label: 'Identical/Shared Clauses', val: cmpResult.shared, bg: 'bg-emerald-950/20', border: 'border-emerald-900/40', text: 'text-emerald-300', icon: <CheckCircle className="w-5 h-5 text-emerald-400" /> },
                          { label: `Exclusive to Doc 1`, val: cmpResult.only1,  bg: 'bg-purple-950/20',  border: 'border-purple-900/40',  text: 'text-purple-300',  icon: <FileText className="w-5 h-5 text-purple-400" /> },
                          { label: `Exclusive to Doc 2`, val: cmpResult.only2,  bg: 'bg-indigo-950/20', border: 'border-indigo-900/40', text: 'text-indigo-300', icon: <FileText className="w-5 h-5 text-indigo-400" /> },
                        ].map((stat, sIdx) => (
                          <div key={sIdx} className={`${stat.bg} border ${stat.border} rounded-xl p-4 flex items-center space-x-3 shadow-md`}>
                            {stat.icon}
                            <div>
                              <div className={`text-2xl font-extrabold ${stat.text}`}>{stat.val}</div>
                              <div className="text-xs text-slate-400 font-semibold">{stat.label}</div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Detail Clause Rows Table */}
                      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                        <div className="flex justify-between items-center">
                          <h4 className="font-bold text-white text-base">Clause Breakdown Matrix</h4>
                          <button
                            onClick={exportComparison}
                            className="text-xs bg-emerald-950 border border-emerald-800 text-emerald-300 px-4 py-2 rounded-xl hover:bg-emerald-900 transition-colors flex items-center space-x-1.5 font-semibold"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>Download Comparison Report</span>
                          </button>
                        </div>

                        <div className="space-y-4">
                          {cmpResult.rows.map((row, rIdx) => (
                            <div key={rIdx} className={`rounded-xl border p-4 bg-slate-950/40 ${
                              row.status === 'shared' ? 'border-emerald-900/40 bg-emerald-950/5'
                              : row.status === 'only1' ? 'border-purple-900/40 bg-purple-950/5'
                              : 'border-indigo-900/40 bg-indigo-950/5'
                            }`}>
                              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                                <div className="flex items-center space-x-2">
                                  <span className="font-semibold text-slate-200 text-sm">{row.type}</span>
                                  {row.status === 'shared' && (
                                    <span className="text-[10px] uppercase font-bold tracking-wider bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full flex items-center space-x-1">
                                      <CheckCircle className="w-2.5 h-2.5" /><span>In Both</span>
                                    </span>
                                  )}
                                  {row.status === 'only1' && (
                                    <span className="text-[10px] uppercase font-bold tracking-wider bg-purple-950 text-purple-300 border border-purple-800 px-2 py-0.5 rounded-full flex items-center space-x-1">
                                      <AlertTriangle className="w-2.5 h-2.5" /><span>Doc 1 Only</span>
                                    </span>
                                  )}
                                  {row.status === 'only2' && (
                                    <span className="text-[10px] uppercase font-bold tracking-wider bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded-full flex items-center space-x-1">
                                      <AlertTriangle className="w-2.5 h-2.5" /><span>Doc 2 Only</span>
                                    </span>
                                  )}
                                </div>
                                <div className="flex space-x-2">
                                  {row.risk1 && <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getRiskBadgeColor(row.risk1)}`}>Doc1: {row.risk1}</span>}
                                  {row.risk2 && <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getRiskBadgeColor(row.risk2)}`}>Doc2: {row.risk2}</span>}
                                </div>
                              </div>

                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
                                <div className="bg-slate-950 p-3 rounded-lg border border-slate-900">
                                  <p className="text-[10px] font-bold uppercase tracking-wider text-purple-400 mb-1">📄 Document 1</p>
                                  <p className="text-xs text-slate-400 leading-relaxed font-sans">
                                    {row.content1 ? row.content1 : <span className="italic text-slate-600">No matching clause in this file</span>}
                                  </p>
                                </div>
                                <div className="bg-slate-950 p-3 rounded-lg border border-slate-900">
                                  <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 mb-1">📄 Document 2</p>
                                  <p className="text-xs text-slate-400 leading-relaxed font-sans">
                                    {row.content2 ? row.content2 : <span className="italic text-slate-600">No matching clause in this file</span>}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {!cmpDoc1 && !cmpDoc2 && (
                    <div className="text-center py-12 text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-950/20">
                      <Eye className="mx-auto w-10 h-10 mb-2 opacity-30 text-slate-400" />
                      <p className="text-sm">Please select and load two files above to begin side-by-side comparison</p>
                    </div>
                  )}
                </div>
              )}

              {/* Analyzer Tab: History Library */}
              {analyzerTab === 'library' && (
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                  <DocumentLibrary token={token} onLoadDocument={handleLoadFromLibrary} />
                </div>
              )}
            </div>
          )}


          {/* ================================================================
              VIEW: CASES LIST & DETAILS (USER OR LAWYER ACTIVE CASES)
              ================================================================ */}
          {(sidebarTab === 'cases' || sidebarTab === 'cases_dealt') && (
            <div className="space-y-6">
              {/* Case Action Header (Only if list mode - no selected case) */}
              {!selectedCase && (
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                  <div>
                    <h3 className="text-lg font-bold text-white">Active Case Collaboration Folders</h3>
                    <p className="text-slate-400 text-xs mt-0.5">Secure, collaborative workspace with clients, lawyers, and shared case documentation.</p>
                  </div>
                  {user?.role === 'user' && (
                    <div className="flex space-x-3 w-full sm:w-auto">
                      <button
                        onClick={() => setShowJoinCase(true)}
                        className="flex-1 sm:flex-initial flex items-center justify-center space-x-1.5 px-4 py-2.5 rounded-xl border border-slate-700 bg-slate-950 text-slate-300 text-xs font-semibold hover:bg-slate-900 transition-colors"
                      >
                        <Link className="w-3.5 h-3.5" />
                        <span>Join Case with Code</span>
                      </button>
                      <button
                        onClick={() => setShowCreateCase(true)}
                        className="flex-1 sm:flex-initial flex items-center justify-center space-x-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold transition-all shadow-md"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Create New Case</span>
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* MODAL: CREATE CASE */}
              {showCreateCase && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
                    <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                      <h4 className="font-bold text-white text-base">Setup New Collaborative Case</h4>
                      <button onClick={() => setShowCreateCase(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
                    </div>
                    <form onSubmit={handleCreateCase} className="space-y-4 text-sm">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-300">Case Folder Title</label>
                        <input
                          type="text"
                          required
                          value={newCaseTitle}
                          onChange={e => setNewCaseTitle(e.target.value)}
                          placeholder="e.g., Rental Agreement Dispute - Apt 4B"
                          className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-300">Issue Description</label>
                        <textarea
                          rows="3"
                          value={newCaseDesc}
                          onChange={e => setNewCaseDesc(e.target.value)}
                          placeholder="Provide details about the issue or legal disagreement..."
                          className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-300">Your Role in Case</label>
                        <select
                          value={newCaseRole}
                          onChange={e => setNewCaseRole(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                        >
                          <option value="House Owner">House Owner</option>
                          <option value="Tenant">Tenant</option>
                          <option value="Business Owner">Business Owner</option>
                          <option value="Business Partner">Business Partner</option>
                          <option value="Husband">Husband</option>
                          <option value="Wife">Wife</option>
                          <option value="Client">Client</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>
                      <button
                        type="submit"
                        disabled={caseLoading}
                        className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-xs transition-all flex items-center justify-center space-x-2"
                      >
                        {caseLoading && <Loader2 className="animate-spin w-4 h-4" />}
                        <span>Initialize Case Folder</span>
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* MODAL: JOIN CASE */}
              {showJoinCase && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
                    <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                      <h4 className="font-bold text-white text-base">Join Collaborative Case</h4>
                      <button onClick={() => setShowJoinCase(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
                    </div>
                    <form onSubmit={handleJoinCase} className="space-y-4 text-sm">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-300">6-character Invitation Code</label>
                        <input
                          type="text"
                          required
                          value={joinCaseCode}
                          onChange={e => setJoinCaseCode(e.target.value)}
                          placeholder="e.g., CASE-A1B2C3"
                          className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-300">Your Role in Joined Case</label>
                        <select
                          value={joinCaseRole}
                          onChange={e => setJoinCaseRole(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                        >
                          <option value="Tenant">Tenant</option>
                          <option value="House Owner">House Owner</option>
                          <option value="Business Owner">Business Owner</option>
                          <option value="Business Partner">Business Partner</option>
                          <option value="Husband">Husband</option>
                          <option value="Wife">Wife</option>
                          <option value="Co-Signer">Co-Signer</option>
                          <option value="Opposing Party">Opposing Party</option>
                          <option value="Participant">Participant</option>
                        </select>
                      </div>
                      <button
                        type="submit"
                        disabled={caseLoading}
                        className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-xs transition-all flex items-center justify-center space-x-2"
                      >
                        {caseLoading && <Loader2 className="animate-spin w-4 h-4" />}
                        <span>Join Collaborative Workspace</span>
                      </button>
                    </form>
                  </div>
                </div>
              )}

              {/* LIST MODE: Cases Grid */}
              {!selectedCase && (
                <>
                  {caseLoading && cases.length === 0 ? (
                    <div className="flex justify-center py-16">
                      <Loader2 className="animate-spin h-8 w-8 text-purple-400" />
                    </div>
                  ) : cases.length === 0 ? (
                    <div className="text-center py-16 bg-slate-900/50 border border-slate-800 rounded-2xl max-w-xl mx-auto space-y-4">
                      <Briefcase className="mx-auto w-12 h-12 text-slate-700" />
                      <h4 className="font-bold text-white text-base">No cases found</h4>
                      <p className="text-slate-400 text-xs max-w-xs mx-auto">
                        {user?.role === 'user' 
                          ? "Initialize a new collaborative case or input a join code from another party."
                          : "You have not accepted any consultation cases yet. Pending client appointments will appear under 'Appointments'."
                        }
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {cases.map(c => (
                        <div
                          key={c.id}
                          onClick={() => setSelectedCase(c)}
                          className="bg-slate-900 border border-slate-800 hover:border-purple-500 hover:shadow-purple-950/20 hover:shadow-lg rounded-2xl p-5 cursor-pointer transition-all flex flex-col justify-between h-48 group"
                        >
                          <div>
                            <div className="flex justify-between items-start">
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-800">{c.code}</span>
                              <span className="text-[10px] font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full border border-slate-750">{c.my_role}</span>
                            </div>
                            <h4 className="font-bold text-white text-sm mt-3 truncate group-hover:text-purple-400 transition-colors">{c.title}</h4>
                            <p className="text-slate-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">{c.description || 'No description provided'}</p>
                          </div>
                          <div className="flex justify-between items-center pt-3 border-t border-slate-800 text-[10px] text-slate-500 font-semibold mt-2">
                            <span className="flex items-center space-x-1"><Users className="w-3.5 h-3.5" /><span>{c.members_count} member{c.members_count !== 1 ? 's' : ''}</span></span>
                            <span className="flex items-center space-x-1"><FolderOpen className="w-3.5 h-3.5" /><span>{c.documents_count} file{c.documents_count !== 1 ? 's' : ''}</span></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}

              {/* DETAILS MODE: Selected Case View */}
              {selectedCase && (
                <div className="space-y-6">
                  {/* Detail Case Header */}
                  <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl">
                    <div className="space-y-1">
                      <button onClick={() => setSelectedCase(null)} className="text-xs text-slate-400 hover:text-purple-400 font-bold flex items-center space-x-1 mb-1">
                        <span>← Back to Cases</span>
                      </button>
                      <h3 className="font-extrabold text-lg text-white">{selectedCase.title}</h3>
                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className="bg-purple-950 text-purple-300 border border-purple-800 px-2.5 py-0.5 rounded-full font-bold">Code: {selectedCase.code}</span>
                        <span className="bg-slate-800 text-slate-400 border border-slate-700 px-2.5 py-0.5 rounded-full font-bold">My Role: {selectedCase.my_role}</span>
                      </div>
                    </div>
                  </div>

                  {/* Two-Column Collaboration Layout */}
                  <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                    {/* Left 2 Cols: Shared Case Documents */}
                    <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-[500px]">
                      <div className="flex justify-between items-center pb-3 border-b border-slate-800 mb-3">
                        <span className="font-bold text-white text-sm flex items-center space-x-1.5">
                          <FolderOpen className="w-4.5 h-4.5 text-purple-400" />
                          <span>Shared Case Documents</span>
                        </span>
                        
                        <button
                          onClick={() => caseDocInputRef.current?.click()}
                          disabled={caseDocUploading}
                          className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 text-white px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1"
                        >
                          {caseDocUploading ? <Loader2 className="animate-spin w-3.5 h-3.5" /> : <Upload className="w-3.5 h-3.5" />}
                          <span>Upload File</span>
                        </button>
                        <input
                          ref={caseDocInputRef}
                          type="file"
                          className="hidden"
                          onChange={handleCaseDocUpload}
                        />
                      </div>

                      {/* Documents List */}
                      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                        {caseDocuments.length === 0 ? (
                          <div className="h-full flex flex-col justify-center items-center text-slate-500 text-center px-4">
                            <FolderOpen className="w-8 h-8 text-slate-800 mb-2" />
                            <p className="text-xs">No documents uploaded to this case yet.</p>
                          </div>
                        ) : (
                          caseDocuments.map(doc => (
                            <div key={doc.id} className="bg-slate-950/60 border border-slate-850 rounded-xl p-3 flex justify-between items-center">
                              <div className="min-w-0 flex-1 mr-2">
                                <p className="text-xs font-bold text-slate-200 truncate">{doc.original_name}</p>
                                <p className="text-[10px] text-slate-500 font-semibold mt-0.5">Uploader: {doc.uploader_name} · {formatDate(doc.uploaded_at)}</p>
                              </div>
                              <a
                                href={`${API}/cases/${selectedCase.id}/documents/${doc.filename.split(/[\\/]/).pop()}/download?token=${token}`}
                                download
                                className="text-slate-400 hover:text-purple-400 p-1.5 bg-slate-900 border border-slate-800 rounded-lg"
                                title="Download case document"
                              >
                                <Download className="w-3.5 h-3.5" />
                              </a>
                            </div>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Right 3 Cols: Group Chat Room */}
                    <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex flex-col h-[500px]">
                      <div className="p-4 border-b border-slate-800 bg-slate-950/20 rounded-t-2xl">
                        <span className="font-bold text-white text-sm flex items-center space-x-1.5">
                          <MessageCircle className="w-4.5 h-4.5 text-purple-400" />
                          <span>Case Group Chatroom</span>
                        </span>
                      </div>

                      {/* Messages Logs */}
                      <div className="flex-1 p-4 overflow-y-auto space-y-4">
                        {caseMessages.length === 0 ? (
                          <div className="h-full flex flex-col justify-center items-center text-slate-500 text-center">
                            <MessageCircle className="w-8 h-8 text-slate-800 mb-2" />
                            <p className="text-xs">Start the discussion. Send a secure chat message to other members.</p>
                          </div>
                        ) : (
                          caseMessages.map(msg => {
                            const isMe = msg.user_id === user?.id;
                            return (
                              <div key={msg.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-xs lg:max-w-md ${isMe ? 'items-end' : 'items-start'} flex flex-col`}>
                                  {!isMe && (
                                    <span className="text-[9px] font-bold text-slate-500 mb-0.5 ml-1">
                                      {msg.sender_name} ({msg.sender_role})
                                    </span>
                                  )}
                                  <div className={`px-4 py-2.5 rounded-2xl text-xs leading-relaxed ${
                                    isMe 
                                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-br-none' 
                                      : 'bg-slate-950 text-slate-200 border border-slate-850 rounded-bl-none'
                                  }`}>
                                    {msg.message}
                                  </div>
                                </div>
                              </div>
                            );
                          })
                        )}
                        <div ref={caseChatEndRef} />
                      </div>

                      {/* Message Input Box */}
                      <form onSubmit={handleSendCaseMessage} className="p-4 border-t border-slate-800">
                        <div className="flex space-x-2">
                          <input
                            type="text"
                            value={caseChatInput}
                            onChange={e => setCaseChatInput(e.target.value)}
                            placeholder="Type secure case message..."
                            className="flex-1 bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-purple-600"
                          />
                          <button
                            type="submit"
                            disabled={!caseChatInput.trim()}
                            className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-850 text-white p-2.5 rounded-xl transition-all"
                          >
                            <Send className="w-4 h-4" />
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}


          {/* ================================================================
              VIEW: BOOK APPOINTMENT (USER ONLY)
              ================================================================ */}
          {sidebarTab === 'book_appointment' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Booking Form (Left 1 Col) */}
                <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
                  <h3 className="text-base font-bold text-white flex items-center space-x-1.5 pb-2 border-b border-slate-800">
                    <Calendar className="w-4.5 h-4.5 text-purple-400" />
                    <span>Send Appointment Request</span>
                  </h3>
                  
                  <form onSubmit={handleBookAppointment} className="space-y-4 text-xs">
                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-300">Choose Case Context</label>
                      <select
                        value={apptCaseId}
                        onChange={e => setApptCaseId(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                      >
                        <option value="">-- Choose Collaborative Case --</option>
                        {cases.map(c => (
                          <option key={c.id} value={c.id}>{c.title} ({c.code})</option>
                        ))}
                        <option value="no_case">No Case (Setup General Consultation)</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs font-semibold text-slate-300">Describe Request Details</label>
                      <textarea
                        rows="5"
                        required
                        value={apptDesc}
                        onChange={e => setApptDesc(e.target.value)}
                        placeholder="Explain the legal problem or consult terms. This will be sent to all registered lawyers..."
                        className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-purple-600"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={apptLoading}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold transition-all flex items-center justify-center space-x-2"
                    >
                      {apptLoading && <Loader2 className="animate-spin w-4 h-4" />}
                      <span>Broadcast to Registered Lawyers</span>
                    </button>
                  </form>
                </div>

                {/* Booking History (Right 2 Cols) */}
                <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-[450px]">
                  <h3 className="text-base font-bold text-white pb-2 border-b border-slate-800 mb-3 flex items-center space-x-1.5">
                    <Clock className="w-4.5 h-4.5 text-purple-400" />
                    <span>My Past Request Broadcasts</span>
                  </h3>
                  
                  <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                    {myAppointments.length === 0 ? (
                      <div className="h-full flex flex-col justify-center items-center text-slate-500 text-center">
                        <Calendar className="w-8 h-8 text-slate-800 mb-2" />
                        <p className="text-xs">No appointment requests created yet.</p>
                      </div>
                    ) : (
                      myAppointments.map(appt => (
                        <div key={appt.id} className="bg-slate-950/60 border border-slate-850 rounded-xl p-4 flex flex-col sm:flex-row justify-between sm:items-center gap-3">
                          <div className="space-y-1">
                            <h4 className="text-xs font-bold text-slate-200">{appt.case_title}</h4>
                            <p className="text-xs text-slate-400 leading-relaxed font-sans">{appt.description}</p>
                            <span className="text-[10px] text-slate-500 font-semibold block">{formatDate(appt.created_at)}</span>
                          </div>
                          
                          <div className="flex-shrink-0">
                            {appt.status === 'pending' ? (
                              <span className="inline-flex items-center space-x-1 bg-amber-950 text-amber-300 border border-amber-800 px-3 py-1 rounded-full text-[10px] font-bold">
                                <Clock className="w-3 h-3 animate-pulse" />
                                <span>PENDING MATCH</span>
                              </span>
                            ) : (
                              <div className="text-right space-y-0.5">
                                <span className="inline-flex items-center space-x-1 bg-emerald-950 text-emerald-300 border border-emerald-800 px-3 py-1 rounded-full text-[10px] font-bold">
                                  <CheckCircle className="w-3 h-3" />
                                  <span>ACCEPTED BY LAWYER</span>
                                </span>
                                <p className="text-[10px] text-slate-400 font-bold mr-1 mt-1">Lawyer: {appt.lawyer_name}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}


          {/* ================================================================
              VIEW: APPOINTMENTS REVIEW & DASHBOARD (LAWYER ONLY)
              ================================================================ */}
          {sidebarTab === 'appointments' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                
                {/* Incoming Requests List (Left 3 Cols) */}
                <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-[500px]">
                  <h3 className="text-base font-bold text-white pb-2 border-b border-slate-800 mb-3 flex items-center space-x-1.5">
                    <PlusCircle className="w-4.5 h-4.5 text-purple-400" />
                    <span>Incoming Client Requests</span>
                  </h3>
                  
                  <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                    {pendingAppointments.length === 0 ? (
                      <div className="h-full flex flex-col justify-center items-center text-slate-500 text-center">
                        <Calendar className="w-8 h-8 text-slate-800 mb-2" />
                        <p className="text-xs">No pending client consultation requests available.</p>
                      </div>
                    ) : (
                      pendingAppointments.map(appt => (
                        <div key={appt.id} className="bg-slate-950/60 border border-slate-850 rounded-xl p-4 space-y-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <span className="text-[10px] font-bold text-purple-400 bg-purple-950/50 border border-purple-800 px-2 py-0.5 rounded-full">{appt.case_title}</span>
                              <p className="text-xs text-slate-400 font-bold mt-1">Client: {appt.client_name}</p>
                            </div>
                            <span className="text-[10px] text-slate-500 font-semibold">{formatDate(appt.created_at)}</span>
                          </div>
                          
                          <p className="text-xs text-slate-300 leading-relaxed bg-slate-900 border border-slate-850 p-3 rounded-lg">{appt.description}</p>
                          
                          <div className="flex space-x-2 pt-1.5 justify-end">
                            <button
                              onClick={() => handleRejectAppointment(appt.id)}
                              className="px-3 py-1.5 border border-slate-750 hover:bg-slate-900 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all flex items-center space-x-1"
                            >
                              <X className="w-3.5 h-3.5" />
                              <span>Hide</span>
                            </button>
                            <button
                              onClick={() => handleAcceptAppointment(appt.id)}
                              className="px-4 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold transition-all flex items-center space-x-1 shadow-md shadow-purple-950/30"
                            >
                              <Check className="w-3.5 h-3.5" />
                              <span>Accept Request</span>
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Accepted Consultations List (Right 2 Cols) */}
                <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-[500px]">
                  <h3 className="text-base font-bold text-white pb-2 border-b border-slate-800 mb-3 flex items-center space-x-1.5">
                    <CheckCircle className="w-4.5 h-4.5 text-purple-400" />
                    <span>My Active Accepted cases</span>
                  </h3>
                  
                  <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                    {myAppointments.length === 0 ? (
                      <div className="h-full flex flex-col justify-center items-center text-slate-500 text-center">
                        <Briefcase className="w-8 h-8 text-slate-800 mb-2" />
                        <p className="text-xs">No consultations accepted yet.</p>
                      </div>
                    ) : (
                      myAppointments.map(appt => (
                        <div key={appt.id} className="bg-slate-950/60 border border-slate-850 rounded-xl p-3 flex justify-between items-center">
                          <div className="min-w-0 flex-1 mr-2">
                            <span className="text-[10px] font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">{appt.case_title}</span>
                            <p className="text-xs font-bold text-slate-200 mt-1 truncate">{appt.description}</p>
                            <p className="text-[10px] text-slate-500 font-semibold mt-0.5">Client: {appt.client_name} · Accepted on {formatDate(appt.created_at)}</p>
                          </div>
                          {appt.case_id && (
                            <button
                              onClick={() => {
                                setSelectedCase({ id: appt.case_id, title: appt.case_title, code: '', my_role: 'Lawyer' });
                                setSidebarTab('cases_dealt');
                              }}
                              className="text-[10px] font-bold bg-purple-600 hover:bg-purple-500 text-white px-2.5 py-1.5 rounded-lg whitespace-nowrap"
                            >
                              Open Folder
                            </button>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>

              </div>
            </div>
          )}


          {/* ================================================================
              VIEW: SEPARATE STORE DOCUMENTS LIBRARY (LAWYER ONLY)
              ================================================================ */}
          {sidebarTab === 'library' && (
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
              <DocumentLibrary token={token} onLoadDocument={handleLoadFromLibrary} />
            </div>
          )}


          {/* ================================================================
              VIEW: ACTIVITY LOG FEED
              ================================================================ */}
          {sidebarTab === 'activity' && (
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl max-w-xl mx-auto space-y-4">
              <div className="pb-3 border-b border-slate-800 flex justify-between items-center">
                <h3 className="text-base font-bold text-white flex items-center space-x-1.5">
                  <Activity className="w-4.5 h-4.5 text-purple-400" />
                  <span>Operation Audit logs</span>
                </h3>
                <button 
                  onClick={fetchActivities} 
                  className="text-[10px] font-bold text-slate-400 hover:text-white bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700"
                >
                  Reload
                </button>
              </div>

              {activityLoading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="animate-spin w-6 h-6 text-purple-400" />
                </div>
              ) : activities.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                  <Activity className="mx-auto w-8 h-8 opacity-30 mb-2" />
                  <p className="text-xs">No activity logged yet.</p>
                </div>
              ) : (
                <div className="space-y-4 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800">
                  {activities.map((act, idx) => (
                    <div key={act.id} className="flex items-start space-x-3 relative z-10">
                      <div className="w-7 h-7 bg-slate-800 border border-slate-750 rounded-full flex items-center justify-center flex-shrink-0 text-purple-400 font-bold text-xs shadow-md">
                        {idx + 1}
                      </div>
                      <div className="bg-slate-950/60 border border-slate-850 p-3 rounded-xl flex-1 flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                        <span className="text-xs text-slate-200 leading-normal">{act.action}</span>
                        <span className="text-[9px] text-slate-500 font-semibold flex-shrink-0">{formatDate(act.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>

        {/* Global Footer */}
        <footer className="py-6 px-8 border-t border-slate-800 bg-slate-950/10 text-center text-xs text-slate-500 flex justify-between items-center">
          <div className="flex items-center space-x-1">
            <Scale className="w-4 h-4 text-purple-500" />
            <span className="font-bold text-slate-400">LexGuard LegalTech</span>
          </div>
          <span>© {new Date().getFullYear()} LexGuard. All rights reserved.</span>
        </footer>

      </main>
    </div>
  );
};

export default LegalAIAssistant;