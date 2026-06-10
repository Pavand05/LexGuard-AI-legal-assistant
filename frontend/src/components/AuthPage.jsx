import React, { useState } from 'react';
import { Scale, Mail, Lock, User, Eye, EyeOff, Loader2, Shield, FileText, Brain } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function AuthPage({ onAuth }) {
  const [mode, setMode]           = useState('login');   // 'login' | 'register'
  const [name, setName]           = useState('');
  const [email, setEmail]         = useState('');
  const [password, setPassword]   = useState('');
  const [showPw, setShowPw]       = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState('');
  const [role, setRole]           = useState('user');   // 'user' | 'lawyer'

  // Lawyer specific registration fields
  const [barLicense, setBarLicense]   = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [licenseFile, setLicenseFile]   = useState(null);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  const isLogin = mode === 'login';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (!isLogin && role === 'lawyer') {
        // Lawyer signup uses FormData
        if (!licenseFile) {
          setError('Please upload a proof of license document.');
          setLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);
        formData.append('password', password);
        formData.append('bar_license', barLicense);
        formData.append('jurisdiction', jurisdiction);
        formData.append('license_file', licenseFile);

        const res = await fetch(`${API}/auth/register/lawyer`, {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (!res.ok) {
          setError(data.error || 'Failed to register lawyer account.');
          return;
        }
        setRegistrationSuccess(true);
      } else {
        // Client signup or login (JSON)
        const endpoint = isLogin ? '/auth/login' : '/auth/register';
        const body     = isLogin
          ? { email, password }
          : { name, email, password };

        const res  = await fetch(`${API}${endpoint}`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) {
          setError(data.error || 'Something went wrong');
          return;
        }

        onAuth(data.user, data.token);
      }
    } catch {
      setError('Could not connect to server. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  if (registrationSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8" style={{ fontFamily: "'Inter', sans-serif", background: '#0f0f1a' }}>
        <div style={{
          width: '100%', maxWidth: '420px',
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '24px', padding: '40px',
          backdropFilter: 'blur(20px)',
          textAlign: 'center'
        }}>
          <div className="mx-auto w-16 h-16 bg-purple-900/30 border border-purple-500 rounded-full flex items-center justify-center mb-6">
            <Shield className="w-8 h-8 text-purple-400 animate-pulse" />
          </div>
          <h2 className="text-white text-2xl font-bold mb-3">Registration Submitted</h2>
          <p className="text-slate-400 text-sm leading-relaxed mb-8">
            Your lawyer account has been registered successfully. An administrator will review your professional credentials and verify your Bar License. You will be able to log in once your account is activated.
          </p>
          <button
            onClick={() => {
              setRegistrationSuccess(false);
              setMode('login');
              setName('');
              setEmail('');
              setPassword('');
              setBarLicense('');
              setJurisdiction('');
              setLicenseFile(null);
            }}
            style={{
              width: '100%', padding: '13px',
              background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
              border: 'none', borderRadius: '10px',
              color: 'white', fontWeight: 700, fontSize: '15px',
              cursor: 'pointer', transition: 'all 0.2s shadow'
            }}
          >
            Back to Sign In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* ── Left panel: branding ── */}
      <div
        className="hidden lg:flex flex-col justify-between w-1/2 p-12 relative overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 100%)',
        }}
      >
        {/* Decorative blobs */}
        <div style={{
          position: 'absolute', top: '-80px', right: '-80px',
          width: '320px', height: '320px', borderRadius: '50%',
          background: 'rgba(139,92,246,0.25)', filter: 'blur(60px)',
        }} />
        <div style={{
          position: 'absolute', bottom: '-100px', left: '-60px',
          width: '280px', height: '280px', borderRadius: '50%',
          background: 'rgba(99,102,241,0.3)', filter: 'blur(80px)',
        }} />

        {/* Logo */}
        <div className="flex items-center space-x-3 relative z-10">
          <div style={{
            background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
            borderRadius: '12px', padding: '10px',
          }}>
            <Scale className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-white text-2xl font-bold">LexGuard</h1>
            <p className="text-purple-300 text-sm">LexGuard LegalTech</p>
          </div>
        </div>

        {/* Features */}
        <div className="space-y-6 relative z-10">
          {[
            { icon: FileText, title: 'Smart Document Analysis', desc: 'Instantly extract clauses and assess risks from any legal document.' },
            { icon: Brain,    title: 'AI-Powered Q&A',          desc: 'Ask any question about your documents in plain language.' },
            { icon: Shield,   title: 'Secure & Private',        desc: 'Your documents are stored privately, accessible only to you.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex items-start space-x-4">
              <div style={{
                background: 'rgba(139,92,246,0.2)', borderRadius: '10px',
                padding: '8px', flexShrink: 0,
              }}>
                <Icon className="w-5 h-5 text-purple-300" />
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{title}</p>
                <p className="text-purple-300 text-xs mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer quote */}
        <p className="text-purple-400 text-xs relative z-10">
          "Legal clarity powered by artificial intelligence."
        </p>
      </div>

      {/* ── Right panel: form ── */}
      <div
        className="flex-1 flex items-center justify-center p-8"
        style={{ background: '#0f0f1a' }}
      >
        <div style={{
          width: '100%', maxWidth: '420px',
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '24px', padding: '40px',
          backdropFilter: 'blur(20px)',
        }}>
          {/* Header */}
          <div className="mb-8">
            {/* Mobile logo */}
            <div className="flex items-center space-x-2 mb-6 lg:hidden">
              <div style={{ background: 'linear-gradient(135deg,#8b5cf6,#6366f1)', borderRadius: '8px', padding: '6px' }}>
                <Scale className="w-5 h-5 text-white" />
              </div>
              <span className="text-white font-bold">LexGuard</span>
            </div>

            <h2 className="text-white text-3xl font-bold">
              {isLogin ? 'Welcome back' : 'Create account'}
            </h2>
            <p style={{ color: '#94a3b8', marginTop: '6px', fontSize: '14px' }}>
              {isLogin
                ? 'Sign in to access your document library'
                : 'Get started with your free account'}
            </p>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: '10px', padding: '12px 16px', marginBottom: '20px',
            }}>
              <p style={{ color: '#f87171', fontSize: '14px' }}>{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role (register only) */}
            {!isLogin && (
              <div style={{ marginBottom: '16px' }}>
                <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                  Select Your Role
                </label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button
                    type="button"
                    onClick={() => setRole('user')}
                    style={{
                      flex: 1,
                      padding: '12px',
                      borderRadius: '10px',
                      border: '2px solid',
                      borderColor: role === 'user' ? '#8b5cf6' : 'rgba(255,255,255,0.1)',
                      background: role === 'user' ? 'rgba(139,92,246,0.1)' : 'rgba(255,255,255,0.02)',
                      color: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <span style={{ fontSize: '14px', fontWeight: 600 }}>Client / User</span>
                    <span style={{ fontSize: '10px', color: '#94a3b8', textAlign: 'center' }}>Analyze docs & book appointments</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('lawyer')}
                    style={{
                      flex: 1,
                      padding: '12px',
                      borderRadius: '10px',
                      border: '2px solid',
                      borderColor: role === 'lawyer' ? '#8b5cf6' : 'rgba(255,255,255,0.1)',
                      background: role === 'lawyer' ? 'rgba(139,92,246,0.1)' : 'rgba(255,255,255,0.02)',
                      color: 'white',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <span style={{ fontSize: '14px', fontWeight: 600 }}>Lawyer</span>
                    <span style={{ fontSize: '10px', color: '#94a3b8', textAlign: 'center' }}>Accept cases & chat with clients</span>
                  </button>
                </div>
              </div>
            )}

            {/* Name (register only) */}
            {!isLogin && (
              <div>
                <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  Full Name
                </label>
                <div style={{ position: 'relative' }}>
                  <User style={{
                    position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                    color: '#64748b', width: '16px', height: '16px',
                  }} />
                  <input
                    id="auth-name"
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="John Smith"
                    required
                    style={{
                      width: '100%', paddingLeft: '42px', paddingRight: '16px',
                      paddingTop: '12px', paddingBottom: '12px',
                      background: 'rgba(255,255,255,0.06)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px', color: 'white', fontSize: '14px',
                      outline: 'none', boxSizing: 'border-box',
                    }}
                    onFocus={e => e.target.style.borderColor = '#8b5cf6'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div>
              <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail style={{
                  position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                  color: '#64748b', width: '16px', height: '16px',
                }} />
                <input
                  id="auth-email"
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  style={{
                    width: '100%', paddingLeft: '42px', paddingRight: '16px',
                    paddingTop: '12px', paddingBottom: '12px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '10px', color: 'white', fontSize: '14px',
                    outline: 'none', boxSizing: 'border-box',
                  }}
                  onFocus={e => e.target.style.borderColor = '#8b5cf6'}
                  onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock style={{
                  position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)',
                  color: '#64748b', width: '16px', height: '16px',
                }} />
                <input
                  id="auth-password"
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder={isLogin ? '••••••••' : 'Min 6 characters'}
                  required
                  style={{
                    width: '100%', paddingLeft: '42px', paddingRight: '48px',
                    paddingTop: '12px', paddingBottom: '12px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '10px', color: 'white', fontSize: '14px',
                    outline: 'none', boxSizing: 'border-box',
                  }}
                  onFocus={e => e.target.style.borderColor = '#8b5cf6'}
                  onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
                <button
                  type="button"
                  onClick={() => setShowPw(v => !v)}
                  style={{
                    position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer', color: '#64748b',
                    padding: 0,
                  }}
                >
                  {showPw ? <EyeOff style={{ width: '16px', height: '16px' }} /> : <Eye style={{ width: '16px', height: '16px' }} />}
                </button>
              </div>
            </div>

            {/* Lawyer-only registration fields */}
            {!isLogin && role === 'lawyer' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                <div>
                  <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    Bar License Number
                  </label>
                  <input
                    type="text"
                    value={barLicense}
                    onChange={e => setBarLicense(e.target.value)}
                    placeholder="e.g. BAR-123456"
                    required
                    style={{
                      width: '100%', paddingLeft: '16px', paddingRight: '16px',
                      paddingTop: '12px', paddingBottom: '12px',
                      background: 'rgba(255,255,255,0.06)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px', color: 'white', fontSize: '14px',
                      outline: 'none', boxSizing: 'border-box',
                    }}
                    onFocus={e => e.target.style.borderColor = '#8b5cf6'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
                <div>
                  <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    Jurisdiction / State
                  </label>
                  <input
                    type="text"
                    value={jurisdiction}
                    onChange={e => setJurisdiction(e.target.value)}
                    placeholder="e.g. California"
                    required
                    style={{
                      width: '100%', paddingLeft: '16px', paddingRight: '16px',
                      paddingTop: '12px', paddingBottom: '12px',
                      background: 'rgba(255,255,255,0.06)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '10px', color: 'white', fontSize: '14px',
                      outline: 'none', boxSizing: 'border-box',
                    }}
                    onFocus={e => e.target.style.borderColor = '#8b5cf6'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                  />
                </div>
                <div>
                  <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                    Proof of License (PDF/Image)
                  </label>
                  <div style={{
                    border: '2px dashed rgba(255,255,255,0.1)',
                    borderRadius: '10px',
                    padding: '16px',
                    textAlign: 'center',
                    background: 'rgba(255,255,255,0.02)',
                    cursor: 'pointer',
                    position: 'relative'
                  }}>
                    <input
                      type="file"
                      accept=".pdf,image/*"
                      required
                      onChange={e => setLicenseFile(e.target.files[0])}
                      style={{
                        position: 'absolute',
                        top: 0, left: 0, width: '100%', height: '100%',
                        opacity: 0, cursor: 'pointer'
                      }}
                    />
                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                      {licenseFile ? licenseFile.name : 'Click to upload Bar ID Card or Certificate'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Submit */}
            <button
              id="auth-submit"
              type="submit"
              disabled={loading}
              style={{
                width: '100%', padding: '13px',
                background: loading
                  ? 'rgba(139,92,246,0.5)'
                  : 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                border: 'none', borderRadius: '10px',
                color: 'white', fontWeight: 700, fontSize: '15px',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: '8px',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                transition: 'opacity 0.2s',
              }}
            >
              {loading && <Loader2 style={{ width: '16px', height: '16px', animation: 'spin 1s linear infinite' }} />}
              {loading ? 'Please wait…' : isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          {/* Toggle */}
          <p style={{ color: '#64748b', fontSize: '14px', textAlign: 'center', marginTop: '24px' }}>
            {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              id="auth-toggle"
              onClick={() => { setMode(isLogin ? 'register' : 'login'); setError(''); }}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#a78bfa', fontWeight: 600, fontSize: '14px',
              }}
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>

      {/* Spin keyframe */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
        input::placeholder { color: #475569; }
      `}</style>
    </div>
  );
}
