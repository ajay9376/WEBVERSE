'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Sparkles, ShieldCheck, GraduationCap, Wallet, FolderKanban, 
  MessageSquareCode, User, LogOut, ArrowRight, CheckCircle2, Clock, 
  Layers, Lock, Database, Terminal, Cpu
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { CosmicBackground } from '@/components/visual/CosmicBackground';
import { AcademicsView } from '@/components/academics/AcademicsView';
import { FinanceView } from '@/components/finance/FinanceView';
import { LifeAdminView } from '@/components/life-admin/LifeAdminView';
import { ChatNexusView } from '@/components/chat/ChatNexusView';

export default function DashboardHome() {
  const router = useRouter();
  const [userProfile, setUserProfile] = useState<any | null>(null);
  const [stats, setStats] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [omnibarText, setOmnibarText] = useState('');

  const samplePrompts = [
    "What is my current DAA attendance?",
    "How much did I spend on food this month?",
    "When does my insurance policy expire?",
    "Can I afford to travel this weekend considering my upcoming exams?",
    "Create a personalized study plan for my mid-terms.",
  ];

  const fetchAuthAndStats = async () => {
    try {
      setLoading(true);
      const token = ApiService.getToken();
      if (!token) {
        // Auto-login default pioneer account or redirect to login
        try {
          const loginResp = await ApiService.login({
            email: 'student@webverse.ai',
            password: 'WebverseSecurePass2026!',
          });
          ApiService.setToken(loginResp.access_token);
        } catch (e) {
          try {
            const regResp = await ApiService.register({
              email: 'student@webverse.ai',
              password: 'WebverseSecurePass2026!',
              full_name: 'Ajay Sharma',
              college_name: 'Apex Institute of Technology',
              branch: 'Computer Science & AI',
              semester: '6th Semester',
            });
            ApiService.setToken(regResp.access_token);
          } catch (regErr) {
            router.push('/login');
            return;
          }
        }
      }

      const [profileData, statsData] = await Promise.all([
        ApiService.getMe(),
        ApiService.getDashboardStats(),
      ]);
      setUserProfile(profileData);
      setStats(statsData);
    } catch (err: any) {
      console.error(err);
      ApiService.clearToken();
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuthAndStats();
  }, []);

  const handleLogout = () => {
    ApiService.clearToken();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-[#06080E] text-[#F3F4F6] relative selection:bg-violet-500 selection:text-white flex flex-col">
      {/* Cosmic Background Canvas */}
      <CosmicBackground />

      {/* Top Navbar */}
      <header className="sticky top-0 z-40 w-full border-b border-white/5 bg-[#06080E]/80 backdrop-blur-xl px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-cyan-400 p-[1px] shadow-lg shadow-violet-500/20">
            <div className="w-full h-full bg-[#090D16] rounded-[11px] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-cyan-300 animate-pulse" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-wider text-white">WEBVERSE</span>
              <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-widest bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 rounded-full">
                Phase 6 · AI Core Live
              </span>
            </div>
            <p className="text-[11px] text-gray-400 font-medium hidden sm:block">
              Your Life. One Connected Intelligence.
            </p>
          </div>
        </div>

        {/* User Pill & Logout */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-gray-200 text-xs font-medium">
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold text-[11px]">
              {userProfile?.full_name?.[0]?.toUpperCase() || 'U'}
            </div>
            <span className="max-w-[120px] truncate hidden sm:inline">
              {userProfile?.full_name || 'Loading...'}
            </span>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-rose-500/15 hover:border-rose-500/30 text-gray-400 hover:text-rose-300 border border-white/5 text-xs font-semibold transition-all cursor-pointer"
            title="Sign Out"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Sign Out</span>
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex flex-col md:flex-row relative z-10">
        {/* Sidebar */}
        <aside className="w-64 shrink-0 border-r border-white/5 bg-[#07090F]/90 backdrop-blur-xl p-4 flex flex-col justify-between hidden md:flex">
          <div className="space-y-6">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-3">
                Navigation Nodes
              </span>
              <nav className="mt-2 space-y-1.5">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    activeTab === 'overview'
                      ? 'bg-violet-600/20 text-white border border-violet-500/30 shadow-lg shadow-violet-500/10'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Layers className="w-4 h-4 text-violet-400" />
                    <span>System Overview</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold uppercase">
                    Live
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('academics')}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    activeTab === 'academics'
                      ? 'bg-purple-600/20 text-white border border-purple-500/30 shadow-lg shadow-purple-500/10'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <GraduationCap className="w-4 h-4 text-purple-400" />
                    <span>StudentOS</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold uppercase">
                    Active
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('finance')}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    activeTab === 'finance'
                      ? 'bg-emerald-600/20 text-white border border-emerald-500/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Wallet className="w-4 h-4 text-emerald-400" />
                    <span>Money Manager</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold uppercase">
                    Active
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('life')}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    activeTab === 'life'
                      ? 'bg-amber-600/20 text-white border border-amber-500/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <FolderKanban className="w-4 h-4 text-amber-400" />
                    <span>Life Admin Vault</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold uppercase">
                    Active
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('ai')}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    activeTab === 'ai'
                      ? 'bg-cyan-600/20 text-white border border-cyan-500/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <MessageSquareCode className="w-4 h-4 text-cyan-400" />
                    <span>Universal AI Core</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold uppercase">
                    Active
                  </span>
                </button>
              </nav>
            </div>

            {/* Architecture Node Status */}
            <div className="p-4 rounded-2xl bg-gradient-to-br from-cyan-950/40 via-indigo-950/20 to-transparent border border-cyan-500/20 space-y-2">
              <div className="flex items-center gap-2 text-cyan-300 text-xs font-bold">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>Architecture Status</span>
              </div>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                Phase 6 complete: Universal AI Core, cross-module RAG retrieval, action execution, and life health scoring are all live.
              </p>
            </div>
          </div>

          <div className="px-3 py-2 text-[11px] text-gray-400 border-t border-white/5 flex items-center justify-between">
            <span>FastAPI + Next.js</span>
            <span className="text-emerald-400 font-bold">Online</span>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full space-y-8">
          {/* Dimension View Switcher */}
          {activeTab === 'academics' && <AcademicsView />}
          {activeTab === 'finance' && <FinanceView />}
          {activeTab === 'life' && <LifeAdminView />}
          {activeTab === 'ai' && <ChatNexusView />}

          {/* System Overview */}
          {activeTab === 'overview' && (
            <div className="space-y-8">
              {/* Universal AI Omnibar Placeholder */}
              <div className="w-full max-w-4xl mx-auto">
                <div className="relative rounded-2xl bg-gradient-to-b from-white/10 to-white/5 p-[1.5px] shadow-2xl shadow-violet-950/40">
                  <div className="bg-[#0A0E1A]/95 rounded-[15px] p-4 backdrop-blur-2xl space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-300">
                        <Sparkles className="w-5 h-5 animate-pulse" />
                      </div>
                      <input
                        type="text"
                        value={omnibarText}
                        onChange={(e) => setOmnibarText(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') setActiveTab('ai');
                        }}
                        placeholder="Ask WEBVERSE anything... (e.g., 'What is my DAA attendance?')"
                        className="w-full bg-transparent text-sm text-white placeholder-gray-400 focus:outline-none font-medium"
                      />
                      <button
                        onClick={() => setActiveTab('ai')}
                        className="px-3.5 py-1.5 rounded-xl bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/30 text-violet-300 text-[11px] font-bold uppercase tracking-wider hidden sm:block whitespace-nowrap cursor-pointer transition-all"
                      >
                        Ask AI Core
                      </button>
                    </div>

                    {/* Prompt Preview Chips */}
                    <div className="pt-3 border-t border-white/5 flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 shrink-0">
                        Try Asking:
                      </span>
                      {samplePrompts.map((p, idx) => (
                        <button
                          key={idx}
                          onClick={() => setActiveTab('ai')}
                          className="shrink-0 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-[11px] text-gray-300 transition-all cursor-pointer border border-white/5"
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Hero Card */}
              <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-purple-950/40 via-[#0B0F1A]/80 to-cyan-950/40 border border-white/10 relative overflow-hidden shadow-2xl">
                <div className="relative z-10 space-y-3">
                  <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold tracking-wider uppercase">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>All 6 Phases Complete · Universal AI Core Active</span>
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                    Welcome to WEBVERSE, {userProfile?.full_name || 'Student Pioneer'}
                  </h1>
                  <p className="text-xs sm:text-sm text-gray-300 max-w-2xl leading-relaxed">
                    Your life. One connected intelligence. All modules are live — StudentOS, Money Manager, Life Admin Vault, and the Universal AI Core with cross-module RAG synthesis and action execution.
                  </p>
                  <div className="pt-2 flex flex-wrap gap-2">
                    <button
                      onClick={() => setActiveTab('ai')}
                      className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-lg shadow-cyan-600/30 transition-all cursor-pointer"
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>Open AI Nexus</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setActiveTab('academics')}
                      className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 font-semibold text-xs transition-all cursor-pointer"
                    >
                      <GraduationCap className="w-4 h-4" />
                      <span>StudentOS</span>
                    </button>
                  </div>
                </div>

                <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
              </div>

              {/* Profile & Node Architecture Matrix */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Authenticated Identity Card */}
                <div className="p-6 rounded-3xl glass-panel border border-violet-500/20 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-violet-500/10 text-violet-400">
                      <User className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30">
                      Authenticated
                    </span>
                  </div>

                  <div>
                    <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                      Student Profile
                    </span>
                    <div className="text-lg font-bold text-white mt-1">
                      {userProfile?.full_name}
                    </div>
                    <span className="text-xs text-violet-300 block font-mono">
                      {userProfile?.email}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1 text-xs">
                    <div className="flex justify-between text-gray-300">
                      <span className="text-gray-500">Institution:</span>
                      <span className="font-semibold">{userProfile?.college_name || 'Apex Institute'}</span>
                    </div>
                    <div className="flex justify-between text-gray-300">
                      <span className="text-gray-500">Branch:</span>
                      <span className="font-semibold">{userProfile?.branch || 'Computer Science'}</span>
                    </div>
                    <div className="flex justify-between text-gray-300">
                      <span className="text-gray-500">Semester:</span>
                      <span className="font-semibold">{userProfile?.semester || '6th Semester'}</span>
                    </div>
                  </div>
                </div>

                {/* Verified Phase 1 & 2 Milestones */}
                <div className="p-6 rounded-3xl glass-panel border border-cyan-500/20 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-extrabold uppercase tracking-widest text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
                      Active Milestones
                    </span>
                  </div>

                  <div>
                    <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                      System Dimensions
                    </span>
                    <div className="text-lg font-bold text-white mt-1">
                      6 of 6 Phases Complete
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-gray-300">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Phase 1: Auth & Multi-Tenant Storage</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Phase 2: StudentOS — Attendance & Exams</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Phase 3: Money Manager — Finance & Budget</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Phase 4: Life Admin Vault — Docs & Bills</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Phase 5: Universal AI Router & RAG</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Phase 6: Cross-Module AI & Action Execution</span>
                    </div>
                  </div>
                </div>

                {/* Roadmap Progression */}
                <div className="p-6 rounded-3xl glass-panel border border-amber-500/20 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-400">
                      <Clock className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/30">
                      Roadmap Progression
                    </span>
                  </div>

                  <div>
                    <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                      Milestones
                    </span>
                    <div className="text-lg font-bold text-white mt-1">
                      Next Dimensions
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-gray-400">
                    <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-between">
                      <span className="text-purple-300 font-bold">Phase 2: StudentOS</span>
                      <span className="text-[10px] text-emerald-400 font-bold">COMPLETE</span>
                    </div>
                    <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
                      <span className="text-emerald-300 font-bold">Phase 3: Money Manager</span>
                      <span className="text-[10px] text-emerald-400 font-bold">COMPLETE</span>
                    </div>
                    <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between">
                      <span className="text-amber-300 font-bold">Phase 4: Life Admin Vault</span>
                      <span className="text-[10px] text-emerald-400 font-bold">COMPLETE</span>
                    </div>
                    <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-between">
                      <span className="text-cyan-300 font-bold">Phase 5 & 6: AI Core</span>
                      <span className="text-[10px] text-emerald-400 font-bold">COMPLETE</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
