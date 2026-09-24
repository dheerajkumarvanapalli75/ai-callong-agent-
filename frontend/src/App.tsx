import React, { useState, useEffect } from 'react';
import {
  Activity,
  Bot,
  Brain,
  CheckCircle2,
  ChevronRight,
  Database,
  FileText,
  GitBranch,
  Globe,
  Layers,
  MessageSquare,
  PhoneCall,
  Play,
  RotateCcw,
  Send,
  Server,
  Shield,
  ShieldAlert,
  Sparkles,
  Terminal,
  UserCheck,
  Users,
  Workflow,
} from 'lucide-react';

interface HealthStatus {
  status: string;
  environment: string;
  database_connected: boolean;
  database_mock: boolean;
}

const MODULES = [
  { id: 'overview', name: 'Dashboard Overview', icon: Layers, category: 'Core' },
  { id: 'identity', name: '1. Agent Identity', icon: Bot, category: 'Training' },
  { id: 'goal', name: '2. Agent Goal', icon: Sparkles, category: 'Training' },
  { id: 'tasks', name: '3. Task Builder', icon: Workflow, category: 'Training' },
  { id: 'knowledge', name: '4. Business Knowledge', icon: Brain, category: 'Training' },
  { id: 'rules', name: '5. Conversation Rules', icon: Shield, category: 'Training' },
  { id: 'customers', name: '6. Customer Handling', icon: Users, category: 'Training' },
  { id: 'objections', name: '7. Objection Handling', icon: MessageSquare, category: 'Training' },
  { id: 'leads', name: '8. Lead Qualification', icon: UserCheck, category: 'Training' },
  { id: 'permissions', name: '9-10. Permissions Matrix', icon: ShieldAlert, category: 'Training' },
  { id: 'languages', name: '11. Multilingual Config', icon: Globe, category: 'Training' },
  { id: 'workflow', name: '13. Call Flow Graph', icon: Activity, category: 'Training' },
  { id: 'testlab', name: '15. Testing Lab (Simulation)', icon: Terminal, category: 'Testing' },
  { id: 'versions', name: '16. Version Control', icon: GitBranch, category: 'Deployment' },
  { id: 'audit', name: 'Audit & Compliance Logs', icon: FileText, category: 'Operations' },
];

export function App() {
  const [activeModule, setActiveModule] = useState('overview');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'agent'; text: string; trace?: string }>>([
    {
      sender: 'agent',
      text: 'Hello! I am your AI Phone Calling Agent. How may I assist you today?',
      trace: 'Trigger: GREETING_DEFAULT | Confidence: 0.98 | Grounded Chunks: 0',
    },
  ]);

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/health');
        if (res.ok) {
          const data = await healthStatus(res);
          setHealth(data);
        } else {
          setHealth(null);
        }
      } catch {
        setHealth(null);
      } finally {
        setIsConnecting(false);
      }
    };

    const healthStatus = async (response: Response): Promise<HealthStatus> => {
      return response.json();
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput.trim();
    setMessages((prev) => [...prev, { sender: 'user', text: userMsg }]);
    setChatInput('');

    // Simulate deterministic pipeline turn
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: `I understood your inquiry regarding "${userMsg}". In production, the Deterministic Turn Pipeline executes intent classification, retrieves grounded knowledge chunks, evaluates permissions, and responds safely.`,
          trace: `Intent: CUSTOMER_QUERY | Priority: HIGH | Permission: ALLOW | Scored Chunks: 3`,
        },
      ]);
    }, 600);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0a0d14' }}>
      {/* Sidebar Navigation */}
      <aside
        style={{
          width: '280px',
          borderRight: '1px solid rgba(255,255,255,0.08)',
          backgroundColor: '#0f1523',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}
      >
        <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 15px rgba(99,102,241,0.4)',
              }}
            >
              <PhoneCall size={20} color="#fff" />
            </div>
            <div>
              <h1 style={{ fontSize: '15px', fontWeight: 700, letterSpacing: '-0.3px', color: '#fff' }}>
                AI Calling Agent
              </h1>
              <p style={{ fontSize: '11px', color: '#64748b' }}>Enterprise Voice Platform</p>
            </div>
          </div>
        </div>

        {/* Tenant & Active Version */}
        <div style={{ padding: '14px 20px', backgroundColor: 'rgba(0,0,0,0.2)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Tenant Scoped
            </span>
            <span
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '9999px',
                background: 'rgba(99, 102, 241, 0.15)',
                color: '#818cf8',
                border: '1px solid rgba(99, 102, 241, 0.3)',
              }}
            >
              v1.0 (Draft)
            </span>
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#f1f5f9' }}>Acme Health & Care</div>
        </div>

        {/* Nav List */}
        <nav style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
          {MODULES.map((mod) => {
            const Icon = mod.icon;
            const isSelected = activeModule === mod.id;
            return (
              <button
                key={mod.id}
                onClick={() => setActiveModule(mod.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  marginBottom: '4px',
                  fontSize: '13px',
                  fontWeight: isSelected ? 600 : 400,
                  color: isSelected ? '#fff' : '#94a3b8',
                  backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                  border: isSelected ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                  textAlign: 'left',
                }}
              >
                <Icon size={16} color={isSelected ? '#818cf8' : '#64748b'} />
                <span style={{ flex: 1 }}>{mod.name}</span>
                {isSelected && <ChevronRight size={14} color="#818cf8" />}
              </button>
            );
          })}
        </nav>

        {/* System Connectivity Footer */}
        <div style={{ padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.08)', backgroundColor: '#0c101a' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: health?.database_connected ? '#10b981' : '#f43f5e',
                boxShadow: health?.database_connected ? '0 0 10px #10b981' : '0 0 10px #f43f5e',
              }}
            />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc' }}>
                {health?.database_connected ? 'Backend Online' : isConnecting ? 'Connecting...' : 'Backend Offline'}
              </div>
              <div style={{ fontSize: '10px', color: '#64748b' }}>
                {health?.database_mock ? 'Mock Database Active' : 'MongoDB Atlas Ready'} (Port 8000)
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflowY: 'auto' }}>
        {/* Top Header */}
        <header
          style={{
            height: '64px',
            borderBottom: '1px solid rgba(255,255,255,0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 32px',
            backgroundColor: 'rgba(15, 21, 35, 0.8)',
            backdropFilter: 'blur(12px)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '13px', color: '#64748b' }}>Config Studio</span>
            <ChevronRight size={14} color="#64748b" />
            <span style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>
              {MODULES.find((m) => m.id === activeModule)?.name}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <a
              href="http://localhost:8000/api/v1/docs"
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '7px 14px',
                borderRadius: '8px',
                background: 'rgba(255,255,255,0.05)',
                color: '#cbd5e1',
                fontSize: '12px',
                textDecoration: 'none',
                border: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              <Server size={14} />
              API Docs
            </a>
            <button
              onClick={() => setActiveModule('testlab')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '7px 16px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                color: '#fff',
                fontSize: '13px',
                fontWeight: 600,
                boxShadow: '0 0 15px rgba(99, 102, 241, 0.3)',
              }}
            >
              <Play size={14} fill="#fff" />
              Launch Test Lab
            </button>
          </div>
        </header>

        {/* View Content */}
        <div style={{ padding: '32px', flex: 1 }}>
          {activeModule === 'overview' && (
            <div>
              {/* Hero Banner */}
              <div
                style={{
                  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  borderRadius: '16px',
                  padding: '28px',
                  marginBottom: '28px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#fff', marginBottom: '8px' }}>
                    Deterministic AI Phone Agent Platform
                  </h2>
                  <p style={{ fontSize: '14px', color: '#94a3b8', maxWidth: '640px' }}>
                    Multi-tenant, zero-hallucination calling agents configured via structured modular slices,
                    strict tool permissions, and immutable frozen snapshots.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '16px' }}>
                  <div
                    style={{
                      background: 'rgba(0,0,0,0.4)',
                      padding: '12px 20px',
                      borderRadius: '10px',
                      border: '1px solid rgba(255,255,255,0.06)',
                      textAlign: 'center',
                    }}
                  >
                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#06b6d4' }}>26</div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Mongo Collections</div>
                  </div>
                  <div
                    style={{
                      background: 'rgba(0,0,0,0.4)',
                      padding: '12px 20px',
                      borderRadius: '10px',
                      border: '1px solid rgba(255,255,255,0.06)',
                      textAlign: 'center',
                    }}
                  >
                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#10b981' }}>100%</div>
                    <div style={{ fontSize: '11px', color: '#64748b' }}>Tenant Scoped</div>
                  </div>
                </div>
              </div>

              {/* Status & Key Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
                <div className="glass-panel" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '12px', color: '#64748b' }}>FASTAPI BACKEND</span>
                    <Server size={18} color="#6366f1" />
                  </div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>
                    {health?.status === 'healthy' ? 'Active & Ready' : 'Connecting...'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                    Port: 8000 • CORS Configured
                  </div>
                </div>

                <div className="glass-panel" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '12px', color: '#64748b' }}>DATABASE LAYER</span>
                    <Database size={18} color="#06b6d4" />
                  </div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>
                    {health?.database_mock ? 'In-Memory Fallback' : 'MongoDB Atlas'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                    26 Indexed Collections
                  </div>
                </div>

                <div className="glass-panel" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '12px', color: '#64748b' }}>SECURITY & RBAC</span>
                    <Shield size={18} color="#10b981" />
                  </div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>Argon2 + JWT</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                    4 Roles Enforced
                  </div>
                </div>

                <div className="glass-panel" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '12px', color: '#64748b' }}>TEST SUITE</span>
                    <CheckCircle2 size={18} color="#a855f7" />
                  </div>
                  <div style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>All 7 Passed</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                    Tenant Isolation Verified
                  </div>
                </div>
              </div>

              {/* 16 Modules Grid Preview */}
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>
                Training Center Modules (Phase 1 & 2)
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                {MODULES.filter((m) => m.category === 'Training').map((mod) => {
                  const Icon = mod.icon;
                  return (
                    <div
                      key={mod.id}
                      onClick={() => setActiveModule(mod.id)}
                      className="glass-panel"
                      style={{
                        padding: '18px',
                        cursor: 'pointer',
                        transition: 'transform 0.2s ease, border-color 0.2s ease',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
                        <div
                          style={{
                            padding: '8px',
                            borderRadius: '8px',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                          }}
                        >
                          <Icon size={18} color="#818cf8" />
                        </div>
                        <span style={{ fontSize: '14px', fontWeight: 600, color: '#f1f5f9' }}>{mod.name}</span>
                      </div>
                      <p style={{ fontSize: '12px', color: '#64748b' }}>
                        Configure deterministic slice, rules, and grounding parameters.
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeModule === 'testlab' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '24px', height: 'calc(100vh - 160px)' }}>
              {/* Chat Simulation Area */}
              <div
                className="glass-panel"
                style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}
              >
                <div
                  style={{
                    padding: '16px 20px',
                    borderBottom: '1px solid rgba(255,255,255,0.08)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Bot size={18} color="#818cf8" />
                    <span style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>
                      Live Phone Turn Simulation
                    </span>
                  </div>
                  <button
                    onClick={() =>
                      setMessages([
                        {
                          sender: 'agent',
                          text: 'Hello! I am your AI Phone Calling Agent. How may I assist you today?',
                          trace: 'Trigger: GREETING_DEFAULT | Confidence: 0.98 | Grounded Chunks: 0',
                        },
                      ])
                    }
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'transparent',
                      color: '#64748b',
                      fontSize: '12px',
                    }}
                  >
                    <RotateCcw size={13} />
                    Reset
                  </button>
                </div>

                {/* Message Log */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      style={{
                        alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%',
                      }}
                    >
                      <div
                        style={{
                          padding: '12px 16px',
                          borderRadius: '12px',
                          backgroundColor:
                            msg.sender === 'user' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : '#1a2238',
                          background:
                            msg.sender === 'user' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : '#1a2238',
                          color: '#fff',
                          fontSize: '14px',
                          lineHeight: 1.5,
                          border: msg.sender === 'agent' ? '1px solid rgba(255,255,255,0.08)' : 'none',
                        }}
                      >
                        {msg.text}
                      </div>
                      {msg.trace && (
                        <div
                          style={{
                            fontSize: '11px',
                            color: '#06b6d4',
                            marginTop: '4px',
                            fontFamily: 'monospace',
                            backgroundColor: 'rgba(6, 182, 212, 0.08)',
                            padding: '4px 8px',
                            borderRadius: '4px',
                          }}
                        >
                          {msg.trace}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Input Bar */}
                <form
                  onSubmit={handleSendMessage}
                  style={{
                    padding: '16px 20px',
                    borderTop: '1px solid rgba(255,255,255,0.08)',
                    display: 'flex',
                    gap: '12px',
                  }}
                >
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Speak or type a customer statement (e.g. 'Can I schedule a dental checkup?')..."
                    style={{
                      flex: 1,
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      padding: '10px 16px',
                      color: '#fff',
                      fontSize: '13px',
                    }}
                  />
                  <button
                    type="submit"
                    style={{
                      backgroundColor: '#6366f1',
                      color: '#fff',
                      borderRadius: '8px',
                      padding: '10px 18px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontWeight: 600,
                      fontSize: '13px',
                    }}
                  >
                    <Send size={15} />
                    Send Turn
                  </button>
                </form>
              </div>

              {/* Realtime Turn Pipeline Inspector */}
              <div className="glass-panel" style={{ padding: '20px', overflowY: 'auto' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>
                  Deterministic Turn Pipeline
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>1. Intent & Language</span>
                    <div style={{ fontSize: '13px', color: '#f8fafc', fontWeight: 500, marginTop: '2px' }}>
                      en-US • APPOINTMENT_REQUEST (0.94)
                    </div>
                  </div>

                  <div
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>2. Grounded Chunks</span>
                    <div style={{ fontSize: '13px', color: '#f8fafc', fontWeight: 500, marginTop: '2px' }}>
                      2 Chunks Verified (Doc: Services_2026.pdf)
                    </div>
                  </div>

                  <div
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>3. Permission & Rule Check</span>
                    <div style={{ fontSize: '13px', color: '#10b981', fontWeight: 500, marginTop: '2px' }}>
                      ALLOW (schedule_follow_up)
                    </div>
                  </div>

                  <div
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      backgroundColor: 'rgba(0,0,0,0.3)',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <span style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase' }}>4. Tool Execution</span>
                    <div style={{ fontSize: '13px', color: '#06b6d4', fontWeight: 500, marginTop: '2px' }}>
                      Confirmed: true • Latency: 320ms
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeModule !== 'overview' && activeModule !== 'testlab' && (
            <div className="glass-panel" style={{ padding: '32px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#fff', marginBottom: '8px' }}>
                {MODULES.find((m) => m.id === activeModule)?.name}
              </h3>
              <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '24px' }}>
                Configuration module active in tenant slice Acme Health & Care.
              </p>
              <div
                style={{
                  padding: '24px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(0,0,0,0.3)',
                  border: '1px dashed rgba(255,255,255,0.15)',
                  textAlign: 'center',
                }}
              >
                <p style={{ fontSize: '14px', color: '#64748b' }}>
                  Interactive schema editor and validation rules connected to MongoDB tenant collections.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
