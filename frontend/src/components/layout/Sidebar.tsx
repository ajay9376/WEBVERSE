'use client';

import React from 'react';
import { LayoutDashboard, GraduationCap, Wallet, FolderKanban, MessageSquareCode, Sparkles } from 'lucide-react';

export type ActiveTab = 'dashboard' | 'academics' | 'finance' | 'life-admin' | 'chat';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems: Array<{
    id: ActiveTab;
    label: string;
    icon: React.ElementType;
    color: string;
    badge?: string;
  }> = [
    {
      id: 'dashboard',
      label: 'Matrix Overview',
      icon: LayoutDashboard,
      color: 'text-violet-400',
    },
    {
      id: 'academics',
      label: 'StudentOS',
      icon: GraduationCap,
      color: 'text-purple-400',
      badge: 'Academics',
    },
    {
      id: 'finance',
      label: 'Money Manager',
      icon: Wallet,
      color: 'text-emerald-400',
      badge: 'Finance',
    },
    {
      id: 'life-admin',
      label: 'Life Admin Vault',
      icon: FolderKanban,
      color: 'text-amber-400',
      badge: 'Vault',
    },
    {
      id: 'chat',
      label: 'Universal AI Nexus',
      icon: MessageSquareCode,
      color: 'text-cyan-400',
      badge: 'AI Core',
    },
  ];

  return (
    <aside className="w-64 shrink-0 border-r border-white/5 bg-[#07090F]/90 backdrop-blur-xl p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-65px)]">
      <div className="space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 px-3">
            Life Dimensions
          </span>
          <nav className="mt-2 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-violet-600/15 text-white border border-violet-500/30 shadow-lg shadow-violet-500/10'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded-lg ${isActive ? 'bg-violet-500/20' : 'bg-white/5'}`}>
                      <Icon className={`w-4 h-4 ${isActive ? 'text-violet-400' : item.color}`} />
                    </div>
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider ${
                        isActive
                          ? 'bg-violet-500/20 text-violet-300'
                          : 'bg-white/5 text-gray-500'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Dimension Matrix Nodes Widget */}
        <div className="p-3.5 rounded-2xl bg-gradient-to-br from-violet-950/40 via-indigo-950/20 to-transparent border border-violet-500/20">
          <div className="flex items-center gap-2 text-violet-300 text-xs font-bold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Interconnected Nodes</span>
          </div>
          <p className="text-[11px] text-gray-400 leading-relaxed">
            All 3 dimensions communicate simultaneously through the central Universal AI router.
          </p>
        </div>
      </div>

      {/* Footer Info */}
      <div className="px-3 py-2 text-[11px] text-gray-400 border-t border-white/5 flex items-center justify-between">
        <span>WEBVERSE Intelligence</span>
        <span className="text-emerald-400 font-semibold">Synced</span>
      </div>
    </aside>
  );
};
