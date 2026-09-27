'use client';

import React, { useState, useEffect } from 'react';
import { CosmicBackground } from '@/components/visual/CosmicBackground';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar, ActiveTab } from '@/components/layout/Sidebar';
import { Omnibar } from '@/components/ai/Omnibar';
import { OverviewMatrix } from '@/components/dashboard/OverviewMatrix';
import { AcademicsView } from '@/components/academics/AcademicsView';
import { FinanceView } from '@/components/finance/FinanceView';
import { LifeAdminView } from '@/components/life-admin/LifeAdminView';
import { ChatNexusView } from '@/components/chat/ChatNexusView';
import { ApiService } from '@/lib/api';
import { DashboardGlance, UserProfile } from '@/types';

export default function WebverseHome() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  const [dashboardData, setDashboardData] = useState<DashboardGlance | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isSeeding, setIsSeeding] = useState(false);
  const [loading, setLoading] = useState(true);

  // Auto-authenticate default demo user or existing token
  const initializeAuthAndData = async () => {
    try {
      setLoading(true);
      try {
        const me = await ApiService.getMe();
        setUserProfile(me);
      } catch (authErr) {
        // Automatically login/register default demo account for instant out-of-the-box viva/showcase experience
        try {
          const loginResp = await ApiService.login({
            email: 'student@webverse.ai',
            password: 'WebverseSecurePass2026!',
          });
          ApiService.setToken(loginResp.access_token);
          const me = await ApiService.getMe();
          setUserProfile(me);
        } catch (loginErr) {
          // If user does not exist yet, register and seed automatically
          const regResp = await ApiService.register({
            email: 'student@webverse.ai',
            password: 'WebverseSecurePass2026!',
            full_name: 'Ajay Sharma',
            college_name: 'Apex Institute of Technology',
            semester: '6th Semester',
            branch: 'Computer Science & Engineering',
            monthly_budget_target: '10000',
          });
          ApiService.setToken(regResp.access_token);
          await ApiService.seedDemo();
          const me = await ApiService.getMe();
          setUserProfile(me);
        }
      }

      // Fetch dashboard glance
      const glance = await ApiService.getDashboardGlance();
      setDashboardData(glance);
    } catch (err: any) {
      console.error('Initialization error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initializeAuthAndData();
  }, []);

  const handleSeedDemo = async () => {
    setIsSeeding(true);
    try {
      await ApiService.seedDemo();
      const glance = await ApiService.getDashboardGlance();
      setDashboardData(glance);
      alert('🌟 Multiverse demo records successfully synchronized across all 3 dimensions!');
    } catch (err: any) {
      alert(`Seeding failed: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  const handleRefreshGlance = async () => {
    try {
      const glance = await ApiService.getDashboardGlance();
      setDashboardData(glance);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-[#06080E] text-[#F3F4F6] relative selection:bg-violet-500 selection:text-white">
      {/* Dynamic Cosmic Background */}
      <CosmicBackground />

      {/* Top Navigation */}
      <Navbar
        userName={userProfile?.full_name || 'Student Pioneer'}
        onSeedDemo={handleSeedDemo}
        isSeeding={isSeeding}
      />

      {/* Main App Layout with Sidebar and Content View */}
      <div className="relative z-10 flex flex-col md:flex-row">
        {/* Dimension Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Dynamic Main Workspace */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full min-h-[calc(100vh-65px)]">
          {/* Universal AI Omnibar (Persistent in Overview Matrix & accessible anytime) */}
          {activeTab === 'dashboard' && (
            <Omnibar onActionResult={handleRefreshGlance} />
          )}

          {/* Active Dimension View */}
          {activeTab === 'dashboard' && (
            <OverviewMatrix data={dashboardData} onNavigate={setActiveTab} />
          )}

          {activeTab === 'academics' && <AcademicsView />}

          {activeTab === 'finance' && <FinanceView />}

          {activeTab === 'life-admin' && <LifeAdminView />}

          {activeTab === 'chat' && <ChatNexusView />}
        </main>
      </div>
    </div>
  );
}
