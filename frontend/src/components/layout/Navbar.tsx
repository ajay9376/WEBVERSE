'use client';

import React from 'react';
import { Sparkles, Database, ShieldCheck, Zap, User as UserIcon, RefreshCw } from 'lucide-react';

interface NavbarProps {
  userName?: string;
  onOpenOmnibar?: () => void;
  onSeedDemo?: () => void;
  isSeeding?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  userName = 'Student Pioneer',
  onOpenOmnibar,
  onSeedDemo,
  isSeeding = false,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/5 bg-[#06080E]/80 backdrop-blur-xl px-6 py-3.5 flex items-center justify-between">
      {/* Brand Identity */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-cyan-400 p-[1px] shadow-lg shadow-violet-500/20">
          <div className="w-full h-full bg-[#090D16] rounded-[11px] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-cyan-300 animate-pulse" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-lg tracking-wider text-white">WEBVERSE</span>
            <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-widest bg-violet-500/10 border border-violet-500/30 text-violet-300 rounded-full">
              v1.0 OS
            </span>
          </div>
          <p className="text-[11px] text-gray-400 font-medium hidden sm:block">
            Your Life. One Connected Intelligence.
          </p>
        </div>
      </div>

      {/* Multiverse Quick Actions */}
      <div className="flex items-center gap-3">
        {/* Seed Demo Button */}
        {onSeedDemo && (
          <button
            onClick={onSeedDemo}
            disabled={isSeeding}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg bg-violet-500/10 hover:bg-violet-500/20 text-violet-300 border border-violet-500/30 transition-all cursor-pointer disabled:opacity-50"
            title="Seed rich realistic student data across Academics, Finance, and Life Admin"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSeeding ? 'animate-spin' : ''}`} />
            <span className="hidden md:inline">{isSeeding ? 'Connecting Matrix...' : 'Seed Multiverse Data'}</span>
          </button>
        )}

        {/* Global Status Pill */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>Core AI: Online</span>
        </div>

        {/* User Pill */}
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-gray-200 text-xs font-medium">
          <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold text-[11px]">
            {userName[0]?.toUpperCase() || 'U'}
          </div>
          <span className="max-w-[120px] truncate hidden sm:inline">{userName}</span>
        </div>
      </div>
    </header>
  );
};
