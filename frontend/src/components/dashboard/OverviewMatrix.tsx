'use client';

import React from 'react';
import { 
  GraduationCap, Wallet, FolderKanban, Sparkles, Clock, 
  AlertTriangle, CheckCircle2, TrendingUp, Calendar, ArrowRight, BookOpen, ShieldAlert
} from 'lucide-react';
import { DashboardGlance } from '@/types';
import { ActiveTab } from '../layout/Sidebar';

interface OverviewMatrixProps {
  data: DashboardGlance | null;
  onNavigate: (tab: ActiveTab) => void;
}

export const OverviewMatrix: React.FC<OverviewMatrixProps> = ({ data, onNavigate }) => {
  if (!data) {
    return (
      <div className="p-12 text-center text-gray-500 text-xs">
        Loading Webverse Matrix...
      </div>
    );
  }

  const isAttendanceSafe = data.overall_attendance_percent >= 75.0;
  const isBudgetSafe = data.budget_health_status === 'HEALTHY';

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Multiverse Greeting Hero */}
      <div className="relative p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-violet-950/40 via-[#0B0F1A]/80 to-cyan-950/40 border border-white/10 overflow-hidden shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-violet-400 text-xs font-bold tracking-wider uppercase">
              <Sparkles className="w-4 h-4 animate-pulse" />
              <span>Connected Life Intelligence</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              {data.greeting}
            </h1>
            <p className="text-xs sm:text-sm text-gray-300 max-w-xl leading-relaxed">
              Your academics, money, and life admin are unified under a single intelligence matrix.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate('chat')}
              className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:opacity-90 text-white font-extrabold text-xs shadow-xl shadow-violet-600/30 transition-all cursor-pointer"
            >
              <Sparkles className="w-4 h-4" />
              <span>Open AI Nexus</span>
            </button>
          </div>
        </div>

        {/* Ambient Glow in background */}
        <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-20 -top-20 w-80 h-80 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* The 3 Main Multiverse Dimension Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 1. ACADEMICS DIMENSION */}
        <div
          onClick={() => onNavigate('academics')}
          className="p-6 rounded-3xl glass-panel border border-purple-500/20 hover:border-purple-500/50 transition-all cursor-pointer group hover:scale-[1.01] flex flex-col justify-between"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-2xl bg-purple-500/10 text-purple-400">
                <GraduationCap className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded-full border border-purple-500/30">
                StudentOS
              </span>
            </div>

            <div>
              <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                Overall Attendance
              </span>
              <div className="text-3xl font-black text-white mt-1">
                {data.overall_attendance_percent}%
              </div>
              <span
                className={`text-[11px] font-semibold mt-1 block ${
                  isAttendanceSafe ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {isAttendanceSafe ? 'Safe Academic Standing' : `${data.subjects_at_risk_count} subjects below target`}
              </span>
            </div>

            {/* Upcoming Academic Highlight */}
            {data.upcoming_exams && data.upcoming_exams.length > 0 && (
              <div className="p-3 rounded-xl bg-white/5 border border-white/5 text-[11px] space-y-1">
                <div className="text-gray-400 text-[10px] uppercase font-bold flex items-center gap-1">
                  <Clock className="w-3 h-3 text-purple-400" />
                  <span>Next Exam</span>
                </div>
                <div className="font-bold text-white truncate">
                  {data.upcoming_exams[0].title}
                </div>
                <div className="text-purple-300 text-[10px]">
                  {new Date(data.upcoming_exams[0].exam_date).toLocaleDateString()}
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs font-bold text-purple-400 group-hover:text-purple-300">
            <span>Manage Subjects & Schedule</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </div>
        </div>

        {/* 2. FINANCE DIMENSION */}
        <div
          onClick={() => onNavigate('finance')}
          className="p-6 rounded-3xl glass-panel border border-emerald-500/20 hover:border-emerald-500/50 transition-all cursor-pointer group hover:scale-[1.01] flex flex-col justify-between"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400">
                <Wallet className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30">
                Money Manager
              </span>
            </div>

            <div>
              <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                Remaining Safe Budget
              </span>
              <div className="text-3xl font-black text-white mt-1">
                ₹{data.monthly_remaining_budget.toLocaleString('en-IN')}
              </div>
              <span
                className={`text-[11px] font-semibold mt-1 block ${
                  isBudgetSafe ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                ₹{data.monthly_total_spent.toLocaleString('en-IN')} spent of ₹{data.monthly_budget_target.toLocaleString('en-IN')} cap
              </span>
            </div>

            {/* Budget Gauge */}
            <div className="space-y-1.5">
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all bg-emerald-500"
                  style={{
                    width: `${Math.min(
                      100,
                      (data.monthly_total_spent / (data.monthly_budget_target || 1)) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs font-bold text-emerald-400 group-hover:text-emerald-300">
            <span>View Spend Analytics</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </div>
        </div>

        {/* 3. LIFE ADMIN DIMENSION */}
        <div
          onClick={() => onNavigate('life-admin')}
          className="p-6 rounded-3xl glass-panel border border-amber-500/20 hover:border-amber-500/50 transition-all cursor-pointer group hover:scale-[1.01] flex flex-col justify-between"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-400">
                <FolderKanban className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/30">
                Life Admin Vault
              </span>
            </div>

            <div>
              <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                Pending Action Items
              </span>
              <div className="text-3xl font-black text-white mt-1">
                {data.pending_reminders?.length || 0}
              </div>
              <span className="text-[11px] font-semibold text-amber-400 mt-1 block">
                {data.urgent_alerts_count} urgent items requiring attention
              </span>
            </div>

            {/* Top Reminder */}
            {data.pending_reminders && data.pending_reminders.length > 0 && (
              <div className="p-3 rounded-xl bg-white/5 border border-white/5 text-[11px] space-y-1">
                <div className="text-gray-400 text-[10px] uppercase font-bold flex items-center gap-1">
                  <Clock className="w-3 h-3 text-amber-400" />
                  <span>Next Reminder</span>
                </div>
                <div className="font-bold text-white truncate">
                  {data.pending_reminders[0].title}
                </div>
                <div className="text-amber-300 text-[10px]">
                  {new Date(data.pending_reminders[0].due_at).toLocaleDateString()}
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs font-bold text-amber-400 group-hover:text-amber-300">
            <span>Access Vault & Documents</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </div>
        </div>
      </div>
    </div>
  );
};
