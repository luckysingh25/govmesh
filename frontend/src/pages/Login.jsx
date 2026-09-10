import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export const Login = () => {
  const { user, login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  if (user) return <Navigate to="/" replace />;
  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setError('');
    try { await login(email, password); } catch (err) { setError(err.message); } finally { setLoading(false); }
  };
  return <div className="login-shell"><form className="login-card" onSubmit={submit}>
    <div className="logo login-logo">🏛️ GovMesh</div>
    <h1>Secure demo sign in</h1>
    <p className="text-muted">Use a fictional account created with the development-only CLI command.</p>
    <label className="form-label" htmlFor="email">Email</label>
    <input id="email" className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
    <label className="form-label" htmlFor="password">Password</label>
    <input id="password" className="form-input" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
    {error && <div className="error-text">{error}</div>}
    <button className="btn btn-primary w-full" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
    <small className="text-muted">No privileged account is created by authentication. Demo data is fictional.</small>
  </form></div>;
};
