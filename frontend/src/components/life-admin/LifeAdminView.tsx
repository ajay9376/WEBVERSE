'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { 
  FolderKanban, FileText, Upload, Clock, AlertTriangle, 
  CheckCircle2, Plus, Sparkles, Tag, Calendar, ShieldAlert,
  ShieldCheck, Receipt, DollarSign, Download, Trash2, Search,
  Filter, Eye, Check, X, CreditCard, HeartPulse, Car, Home,
  Plane, Award, Scale, HelpCircle, Bell, RefreshCw, ChevronRight,
  Clock3, Shield, ArrowUpRight, Lock
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { 
  DocumentItem, 
  BillItem, 
  InsurancePolicyItem, 
  ImportantDateItem, 
  ReminderItem, 
  LifeAdminCategory, 
  LifeAdminDashboardData,
  DocumentCategory,
  BillStatus,
  PolicyType,
  PremiumFrequency,
  ImportantDateCategory,
  ReminderPriority
} from '@/types';

type LifeAdminTab = 'overview' | 'documents' | 'bills' | 'insurance' | 'dates' | 'reminders';

export const LifeAdminView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<LifeAdminTab>('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Core Data
  const [dashboardData, setDashboardData] = useState<LifeAdminDashboardData | null>(null);
  const [categories, setCategories] = useState<LifeAdminCategory[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [bills, setBills] = useState<BillItem[]>([]);
  const [policies, setPolicies] = useState<InsurancePolicyItem[]>([]);
  const [importantDates, setImportantDates] = useState<ImportantDateItem[]>([]);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);

  // Filter & Search states
  const [docSearch, setDocSearch] = useState('');
  const [docCategoryFilter, setDocCategoryFilter] = useState('ALL');
  const [docExpiryFilter, setDocExpiryFilter] = useState('');

  const [billStatusFilter, setBillStatusFilter] = useState('ALL');
  const [billSearch, setBillSearch] = useState('');

  const [policyTypeFilter, setPolicyTypeFilter] = useState('ALL');
  const [policySearch, setPolicySearch] = useState('');

  const [dateCategoryFilter, setDateCategoryFilter] = useState('ALL');

  // Modals state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showAddBillModal, setShowAddBillModal] = useState(false);
  const [showAddPolicyModal, setShowAddPolicyModal] = useState(false);
  const [showAddDateModal, setShowAddDateModal] = useState(false);
  const [showAddReminderModal, setShowAddReminderModal] = useState(false);

  // Selected document for details preview modal
  const [selectedDocPreview, setSelectedDocPreview] = useState<DocumentItem | null>(null);

  // Upload Form State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState<DocumentCategory>('OTHER');
  const [uploadIssuer, setUploadIssuer] = useState('');
  const [uploadRefNo, setUploadRefNo] = useState('');
  const [uploadDocDate, setUploadDocDate] = useState('');
  const [uploadExpiryDate, setUploadExpiryDate] = useState('');
  const [uploadTags, setUploadTags] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  // Add Bill Form State
  const [billTitle, setBillTitle] = useState('');
  const [billProvider, setBillProvider] = useState('');
  const [billCategory, setBillCategory] = useState('UTILITIES');
  const [billAmount, setBillAmount] = useState('');
  const [billDueDate, setBillDueDate] = useState('');
  const [billRecurring, setBillRecurring] = useState(false);
  const [billRecurrence, setBillRecurrence] = useState<'NONE' | 'MONTHLY' | 'QUARTERLY' | 'YEARLY'>('MONTHLY');
  const [billNotes, setBillNotes] = useState('');

  // Add Policy Form State
  const [polProvider, setPolProvider] = useState('');
  const [polName, setPolName] = useState('');
  const [polNumber, setPolNumber] = useState('');
  const [polType, setPolType] = useState<PolicyType>('HEALTH');
  const [polStartDate, setPolStartDate] = useState('');
  const [polExpiryDate, setPolExpiryDate] = useState('');
  const [polPremium, setPolPremium] = useState('');
  const [polFrequency, setPolFrequency] = useState<PremiumFrequency>('YEARLY');
  const [polCoverage, setPolCoverage] = useState('');
  const [polNotes, setPolNotes] = useState('');

  // Add Important Date Form State
  const [dateTitle, setDateTitle] = useState('');
  const [dateValue, setDateValue] = useState('');
  const [dateCategory, setDateCategory] = useState<ImportantDateCategory>('PASSPORT');
  const [dateRecurring, setDateRecurring] = useState(false);
  const [dateDescription, setDateDescription] = useState('');

  // Add Reminder Form State
  const [remTitle, setRemTitle] = useState('');
  const [remDueDate, setRemDueDate] = useState('');
  const [remPriority, setRemPriority] = useState<ReminderPriority>('MEDIUM');
  const [remDescription, setRemDescription] = useState('');

  // Fetch all Vault data
  const loadVaultData = useCallback(async () => {
    try {
      const [dash, cats, docs, bls, pols, dts, rems] = await Promise.all([
        ApiService.getLifeAdminDashboard(),
        ApiService.getLifeAdminCategories(),
        ApiService.getDocuments({ category: docCategoryFilter, search: docSearch, expiry_filter: docExpiryFilter }),
        ApiService.getBills({ status: billStatusFilter, search: billSearch }),
        ApiService.getPolicies({ policy_type: policyTypeFilter, search: policySearch }),
        ApiService.getImportantDates({ category: dateCategoryFilter }),
        ApiService.getReminders(),
      ]);

      setDashboardData(dash);
      setCategories(cats || []);
      setDocuments(docs || []);
      setBills(bls || []);
      setPolicies(pols || []);
      setImportantDates(dts || []);
      setReminders(rems || []);
    } catch (err) {
      console.error('Failed to load Life Admin Vault data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [docCategoryFilter, docSearch, docExpiryFilter, billStatusFilter, billSearch, policyTypeFilter, policySearch, dateCategoryFilter]);

  useEffect(() => {
    loadVaultData();
  }, [loadVaultData]);

  // Handlers
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      if (uploadTitle.trim()) formData.append('title', uploadTitle.trim());
      formData.append('category', uploadCategory);
      if (uploadIssuer.trim()) formData.append('issuer', uploadIssuer.trim());
      if (uploadRefNo.trim()) formData.append('reference_number', uploadRefNo.trim());
      if (uploadDocDate) formData.append('document_date', new Date(uploadDocDate).toISOString());
      if (uploadExpiryDate) formData.append('expiry_date', new Date(uploadExpiryDate).toISOString());
      if (uploadTags.trim()) formData.append('tags', uploadTags.trim());
      if (uploadDescription.trim()) formData.append('description', uploadDescription.trim());

      await ApiService.uploadDocument(formData);
      
      // Reset form
      setUploadFile(null);
      setUploadTitle('');
      setUploadIssuer('');
      setUploadRefNo('');
      setUploadDocDate('');
      setUploadExpiryDate('');
      setUploadTags('');
      setUploadDescription('');
      setShowUploadModal(false);

      await loadVaultData();
    } catch (err: any) {
      alert(`Document upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadDocument = async (doc: DocumentItem) => {
    try {
      await ApiService.downloadDocument(doc.id, doc.filename);
    } catch (err: any) {
      alert(`Download failed: ${err.message}`);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document from your vault?')) return;
    try {
      await ApiService.deleteDocument(id);
      await loadVaultData();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleCreateBill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!billTitle.trim() || !billProvider.trim() || !billAmount || !billDueDate) return;

    try {
      await ApiService.createBill({
        title: billTitle.trim(),
        provider: billProvider.trim(),
        category: billCategory,
        amount: parseFloat(billAmount),
        due_date: new Date(billDueDate).toISOString(),
        recurring: billRecurring,
        recurrence: billRecurring ? billRecurrence : 'NONE',
        notes: billNotes.trim() || undefined,
      });

      setBillTitle('');
      setBillProvider('');
      setBillAmount('');
      setBillDueDate('');
      setBillNotes('');
      setShowAddBillModal(false);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to save bill: ${err.message}`);
    }
  };

  const handlePayBill = async (bill: BillItem) => {
    const ref = prompt(`Enter payment reference / transaction ID for ${bill.title}:`, 'UPI-PAID-' + Date.now().toString().slice(-6));
    if (ref === null) return;
    try {
      await ApiService.payBill(bill.id, ref);
      await loadVaultData();
    } catch (err: any) {
      alert(`Could not mark bill as paid: ${err.message}`);
    }
  };

  const handleDeleteBill = async (id: string) => {
    if (!confirm('Delete this bill record?')) return;
    try {
      await ApiService.deleteBill(id);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to delete bill: ${err.message}`);
    }
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!polProvider.trim() || !polName.trim() || !polNumber.trim() || !polExpiryDate || !polPremium) return;

    try {
      await ApiService.createPolicy({
        provider: polProvider.trim(),
        policy_name: polName.trim(),
        policy_number: polNumber.trim(),
        policy_type: polType,
        start_date: polStartDate ? new Date(polStartDate).toISOString() : undefined,
        expiry_date: new Date(polExpiryDate).toISOString(),
        premium_amount: parseFloat(polPremium),
        premium_frequency: polFrequency,
        coverage_amount: polCoverage ? parseFloat(polCoverage) : undefined,
        notes: polNotes.trim() || undefined,
      });

      setPolProvider('');
      setPolName('');
      setPolNumber('');
      setPolStartDate('');
      setPolExpiryDate('');
      setPolPremium('');
      setPolCoverage('');
      setPolNotes('');
      setShowAddPolicyModal(false);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to create insurance policy: ${err.message}`);
    }
  };

  const handleDeletePolicy = async (id: string) => {
    if (!confirm('Delete this insurance policy record?')) return;
    try {
      await ApiService.deletePolicy(id);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to delete policy: ${err.message}`);
    }
  };

  const handleCreateImportantDate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dateTitle.trim() || !dateValue) return;

    try {
      await ApiService.createImportantDate({
        title: dateTitle.trim(),
        date: new Date(dateValue).toISOString(),
        category: dateCategory,
        recurring: dateRecurring,
        recurrence: dateRecurring ? 'YEARLY' : 'NONE',
        description: dateDescription.trim() || undefined,
      });

      setDateTitle('');
      setDateValue('');
      setDateDescription('');
      setShowAddDateModal(false);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to add milestone: ${err.message}`);
    }
  };

  const handleDeleteImportantDate = async (id: string) => {
    if (!confirm('Remove this milestone from your calendar?')) return;
    try {
      await ApiService.deleteImportantDate(id);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to remove date: ${err.message}`);
    }
  };

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!remTitle.trim() || !remDueDate) return;

    try {
      await ApiService.createReminder({
        title: remTitle.trim(),
        due_at: new Date(remDueDate).toISOString(),
        priority: remPriority,
        description: remDescription.trim() || undefined,
        linked_module: 'LIFE_ADMIN',
      });

      setRemTitle('');
      setRemDueDate('');
      setRemDescription('');
      setShowAddReminderModal(false);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to create reminder: ${err.message}`);
    }
  };

  const handleToggleReminder = async (id: string) => {
    try {
      await ApiService.toggleReminder(id);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to toggle reminder: ${err.message}`);
    }
  };

  const handleDeleteReminder = async (id: string) => {
    try {
      await ApiService.deleteReminder(id);
      await loadVaultData();
    } catch (err: any) {
      alert(`Failed to delete reminder: ${err.message}`);
    }
  };

  // Helper icons
  const getCategoryIcon = (cat: string) => {
    switch (cat.toUpperCase()) {
      case 'IDENTITY': return <Lock className="w-4 h-4 text-cyan-400" />;
      case 'EDUCATION': return <Award className="w-4 h-4 text-purple-400" />;
      case 'INSURANCE': return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      case 'FINANCE': return <DollarSign className="w-4 h-4 text-amber-400" />;
      case 'BILLS': return <Receipt className="w-4 h-4 text-pink-400" />;
      case 'MEDICAL': return <HeartPulse className="w-4 h-4 text-rose-400" />;
      case 'TRAVEL': return <Plane className="w-4 h-4 text-blue-400" />;
      case 'CERTIFICATES': return <Award className="w-4 h-4 text-violet-400" />;
      case 'LEGAL': return <Scale className="w-4 h-4 text-indigo-400" />;
      default: return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-sm font-mono text-cyan-300 tracking-wider">CONNECTING TO SECURE VAULT...</p>
      </div>
    );
  }

  const billsSummary = dashboardData?.bills_summary || {
    pending_count: 0,
    overdue_count: 0,
    paid_count: 0,
    total_pending_amount: 0,
    total_overdue_amount: 0,
    upcoming_bills: [],
  };

  const policiesSummary = dashboardData?.policies_summary || {
    total_policies: 0,
    expiring_soon_count: 0,
    total_annual_premiums: 0,
    expiring_policies: [],
  };

  const totalVaultDocs = dashboardData?.total_documents || documents.length;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Dimension Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <FolderKanban className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Life Admin Vault
                <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  DIMENSION: VAULT
                </span>
              </h1>
              <p className="text-sm text-slate-400">
                Encrypted repository for documents, bills, policies, deadlines, and renewals.
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold tracking-wide transition-all shadow-[0_0_15px_rgba(6,182,212,0.15)]"
          >
            <Upload className="w-4 h-4" />
            Upload Document
          </button>
          <button
            onClick={() => setShowAddBillModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-pink-500/20 hover:bg-pink-500/30 text-pink-300 border border-pink-500/40 text-xs font-semibold tracking-wide transition-all"
          >
            <Receipt className="w-4 h-4" />
            Add Bill
          </button>
          <button
            onClick={() => setShowAddPolicyModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold tracking-wide transition-all"
          >
            <Shield className="w-4 h-4" />
            Add Policy
          </button>
          <button
            onClick={() => setShowAddReminderModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-xs font-semibold tracking-wide transition-all"
          >
            <Bell className="w-4 h-4" />
            Add Reminder
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800/80 scrollbar-none">
        {[
          { id: 'overview', label: 'Vault Overview', icon: FolderKanban },
          { id: 'documents', label: `Documents (${totalVaultDocs})`, icon: FileText },
          { id: 'bills', label: `Bills & Invoices (${bills.length})`, icon: Receipt },
          { id: 'insurance', label: `Insurance & Policies (${policies.length})`, icon: ShieldCheck },
          { id: 'dates', label: `Important Dates (${importantDates.length})`, icon: Calendar },
          { id: 'reminders', label: `Reminders (${reminders.filter(r => !r.is_completed).length})`, icon: Bell },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as LifeAdminTab)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-medium tracking-wide whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(6,182,212,0.15)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB 1: VAULT OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Urgent Alerts Cockpit (Overdue Bills or Expiring Policies) */}
          {(billsSummary.overdue_count > 0 || policiesSummary.expiring_soon_count > 0) && (
            <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-500/40 backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-[0_0_20px_rgba(244,63,94,0.15)]">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-400">
                  <ShieldAlert className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-rose-300">Action Required: Deadlines & Expiries</h4>
                  <p className="text-xs text-rose-200/80">
                    {billsSummary.overdue_count > 0 && `${billsSummary.overdue_count} overdue bill(s) totaling ₹${billsSummary.total_overdue_amount.toLocaleString()}. `}
                    {policiesSummary.expiring_soon_count > 0 && `${policiesSummary.expiring_soon_count} insurance policy renewal(s) due within 30 days.`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {billsSummary.overdue_count > 0 && (
                  <button
                    onClick={() => setActiveTab('bills')}
                    className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-mono font-medium transition-all"
                  >
                    Resolve Bills &rarr;
                  </button>
                )}
                {policiesSummary.expiring_soon_count > 0 && (
                  <button
                    onClick={() => setActiveTab('insurance')}
                    className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-xs font-mono font-medium transition-all"
                  >
                    View Policies &rarr;
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Metric Overview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-mono tracking-wider">DOCUMENTS STORED</span>
                <FileText className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">{totalVaultDocs}</div>
              <div className="text-xs text-cyan-400/80 mt-1 flex items-center gap-1">
                <Lock className="w-3 h-3" /> Encrypted & isolated
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-mono tracking-wider">PENDING BILLS</span>
                <Receipt className="w-4 h-4 text-pink-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                ₹{billsSummary.total_pending_amount.toLocaleString()}
              </div>
              <div className="text-xs text-pink-400/80 mt-1">
                {billsSummary.pending_count} pending / {billsSummary.overdue_count} overdue
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-mono tracking-wider">ACTIVE POLICIES</span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {policiesSummary.total_policies}
              </div>
              <div className="text-xs text-emerald-400/80 mt-1">
                ₹{policiesSummary.total_annual_premiums.toLocaleString()} annual premium
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs font-mono tracking-wider">PENDING REMINDERS</span>
                <Bell className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-white tracking-tight">
                {reminders.filter(r => !r.is_completed).length}
              </div>
              <div className="text-xs text-purple-400/80 mt-1">
                {importantDates.length} upcoming milestones
              </div>
            </div>
          </div>

          {/* Two Columns: Recent Documents & Upcoming Milestones */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Documents */}
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  Recent Documents
                </h3>
                <button
                  onClick={() => setActiveTab('documents')}
                  className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono transition-colors"
                >
                  View All &rarr;
                </button>
              </div>

              {documents.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  No documents in your vault yet. Upload your first document to secure it.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {documents.slice(0, 4).map((doc) => (
                    <div
                      key={doc.id}
                      className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80 hover:border-cyan-500/40 flex items-center justify-between gap-3 transition-all"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2 rounded-lg bg-slate-800 text-cyan-400 shrink-0">
                          {getCategoryIcon(doc.category)}
                        </div>
                        <div className="min-w-0">
                          <h5 className="text-xs font-semibold text-slate-200 truncate">{doc.title}</h5>
                          <p className="text-[11px] text-slate-400 truncate">
                            {doc.category} &bull; {doc.file_size} KB &bull; {new Date(doc.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDownloadDocument(doc)}
                        className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-cyan-500/20 text-slate-300 hover:text-cyan-300 border border-slate-700/60 transition-colors"
                        title="Download"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Upcoming Deadlines & Bills */}
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Clock className="w-4 h-4 text-pink-400" />
                  Upcoming Bills & Deadlines
                </h3>
                <button
                  onClick={() => setActiveTab('bills')}
                  className="text-xs text-pink-400 hover:text-pink-300 flex items-center gap-1 font-mono transition-colors"
                >
                  View All &rarr;
                </button>
              </div>

              {bills.length === 0 && importantDates.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  No upcoming bills or milestone deadlines scheduled.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {bills.slice(0, 3).map((b) => (
                    <div
                      key={b.id}
                      className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className={`p-2 rounded-lg shrink-0 ${b.is_overdue ? 'bg-rose-500/20 text-rose-400' : 'bg-pink-500/10 text-pink-400'}`}>
                          <Receipt className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <h5 className="text-xs font-semibold text-slate-200 truncate">{b.title}</h5>
                          <p className="text-[11px] text-slate-400 truncate">
                            {b.provider} &bull; Due: {new Date(b.due_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-xs font-bold font-mono text-white">₹{b.amount.toLocaleString()}</div>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${b.is_overdue ? 'bg-rose-500/20 text-rose-300' : b.status === 'PAID' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>
                          {b.is_overdue ? 'OVERDUE' : b.status}
                        </span>
                      </div>
                    </div>
                  ))}

                  {importantDates.slice(0, 2).map((d) => (
                    <div
                      key={d.id}
                      className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 shrink-0">
                          <Calendar className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <h5 className="text-xs font-semibold text-slate-200 truncate">{d.title}</h5>
                          <p className="text-[11px] text-slate-400 truncate">
                            {d.category} &bull; {new Date(d.date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-xs font-mono font-semibold text-purple-300 px-2 py-0.5 rounded bg-purple-500/15 border border-purple-500/30">
                          {d.days_remaining >= 0 ? `in ${d.days_remaining}d` : 'Passed'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: DOCUMENT VAULT */}
      {activeTab === 'documents' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
            {/* Search Input */}
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search documents, tags, issuer..."
                value={docSearch}
                onChange={(e) => setDocSearch(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
              />
            </div>

            {/* Category Filter */}
            <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
              {['ALL', 'IDENTITY', 'EDUCATION', 'INSURANCE', 'BILLS', 'MEDICAL', 'CERTIFICATES', 'LEGAL', 'OTHER'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setDocCategoryFilter(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono tracking-wider transition-all whitespace-nowrap ${
                    docCategoryFilter === cat
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                      : 'text-slate-400 hover:text-slate-200 bg-slate-800/40 hover:bg-slate-800'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Document Grid */}
          {documents.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
              <FileText className="w-10 h-10 text-slate-600 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No documents found in vault</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Upload your ID proofs, insurance papers, certificates, or receipts for safe, user-isolated storage.
              </p>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition-all mt-2"
              >
                <Upload className="w-4 h-4" />
                Upload First Document
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 transition-all flex flex-col justify-between group relative backdrop-blur-md shadow-lg"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                        {getCategoryIcon(doc.category)}
                      </div>
                      <div className="flex items-center gap-1">
                        {doc.days_until_expiry !== null && doc.days_until_expiry !== undefined && (
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                            doc.is_expired
                              ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                              : doc.days_until_expiry <= 30
                              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          }`}>
                            {doc.is_expired ? 'EXPIRED' : `Exp: ${doc.days_until_expiry}d`}
                          </span>
                        )}
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                          {doc.category}
                        </span>
                      </div>
                    </div>

                    <h4 className="text-sm font-semibold text-white line-clamp-1 mb-1">{doc.title}</h4>
                    <p className="text-xs text-slate-400 font-mono line-clamp-1 mb-2">
                      {doc.filename} &bull; {doc.file_size} KB
                    </p>

                    {(doc.issuer || doc.reference_number) && (
                      <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] space-y-1 mb-3">
                        {doc.issuer && (
                          <div className="text-slate-300">
                            <span className="text-slate-500 font-mono">Issuer:</span> {doc.issuer}
                          </div>
                        )}
                        {doc.reference_number && (
                          <div className="text-slate-300 font-mono">
                            <span className="text-slate-500">Ref:</span> {doc.reference_number}
                          </div>
                        )}
                      </div>
                    )}

                    {doc.tags && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {doc.tags.split(',').map((t, idx) => (
                          <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-800/80 text-cyan-300/80 font-mono">
                            #{t.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                    <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => setSelectedDocPreview(doc)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDownloadDocument(doc)}
                        className="p-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 transition-colors"
                        title="Download"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: BILLS & INVOICES */}
      {activeTab === 'bills' && (
        <div className="space-y-6">
          {/* Top Summary Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs font-mono text-slate-400 mb-1">TOTAL PENDING BILLS</div>
              <div className="text-xl font-bold font-mono text-pink-400">
                ₹{billsSummary.total_pending_amount.toLocaleString()}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">{billsSummary.pending_count} bills awaiting payment</div>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs font-mono text-slate-400 mb-1">OVERDUE AMOUNT</div>
              <div className="text-xl font-bold font-mono text-rose-400">
                ₹{billsSummary.total_overdue_amount.toLocaleString()}
              </div>
              <div className="text-[11px] text-rose-400/80 mt-1">{billsSummary.overdue_count} overdue invoices</div>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="text-xs font-mono text-slate-400 mb-1">PAID INVOICES</div>
              <div className="text-xl font-bold font-mono text-emerald-400">
                {billsSummary.paid_count}
              </div>
              <div className="text-[11px] text-emerald-400/80 mt-1">Settled records</div>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search provider, bill title..."
                value={billSearch}
                onChange={(e) => setBillSearch(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pink-500/60"
              />
            </div>
            <div className="flex items-center gap-2">
              {['ALL', 'PENDING', 'OVERDUE', 'PAID'].map((st) => (
                <button
                  key={st}
                  onClick={() => setBillStatusFilter(st)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                    billStatusFilter === st
                      ? 'bg-pink-500/20 text-pink-300 border border-pink-500/40'
                      : 'text-slate-400 hover:text-slate-200 bg-slate-800/40 hover:bg-slate-800'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>

          {/* Bills List */}
          {bills.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
              <Receipt className="w-10 h-10 text-slate-600 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No bills added yet</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Track your mess fees, internet, electricity, tuition, and recurring invoices.
              </p>
              <button
                onClick={() => setShowAddBillModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-pink-500/20 hover:bg-pink-500/30 text-pink-300 border border-pink-500/40 text-xs font-semibold transition-all mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Bill Record
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {bills.map((bill) => (
                <div
                  key={bill.id}
                  className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-pink-500/40 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`p-3 rounded-xl border shrink-0 ${
                      bill.is_overdue
                        ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                        : bill.status === 'PAID'
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : 'bg-pink-500/10 border-pink-500/30 text-pink-400'
                    }`}>
                      <Receipt className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-white truncate">{bill.title}</h4>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                          bill.is_overdue
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                            : bill.status === 'PAID'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        }`}>
                          {bill.is_overdue ? `OVERDUE (${bill.days_overdue}d)` : bill.status}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 font-mono mt-0.5">
                        Provider: {bill.provider} &bull; Category: {bill.category} &bull; Due: {new Date(bill.due_date).toLocaleDateString()}
                      </p>
                      {bill.payment_reference && (
                        <p className="text-[11px] text-emerald-400/80 font-mono mt-0.5">
                          Ref: {bill.payment_reference}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-4 w-full sm:w-auto border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-800">
                    <div className="text-right">
                      <div className="text-base font-bold font-mono text-white">₹{bill.amount.toLocaleString()}</div>
                      {bill.recurring && (
                        <span className="text-[10px] text-pink-400/80 font-mono">Recurring ({bill.recurrence})</span>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {bill.status !== 'PAID' && (
                        <button
                          onClick={() => handlePayBill(bill)}
                          className="px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center gap-1 transition-all"
                        >
                          <Check className="w-3.5 h-3.5" />
                          Mark Paid
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteBill(bill.id)}
                        className="p-2 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: INSURANCE & POLICIES */}
      {activeTab === 'insurance' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search provider, policy name..."
                value={policySearch}
                onChange={(e) => setPolicySearch(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/60"
              />
            </div>
            <div className="flex items-center gap-2 overflow-x-auto">
              {['ALL', 'HEALTH', 'VEHICLE', 'LIFE', 'TRAVEL', 'HOME', 'OTHER'].map((t) => (
                <button
                  key={t}
                  onClick={() => setPolicyTypeFilter(t)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all whitespace-nowrap ${
                    policyTypeFilter === t
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      : 'text-slate-400 hover:text-slate-200 bg-slate-800/40 hover:bg-slate-800'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {policies.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
              <ShieldCheck className="w-10 h-10 text-slate-600 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No insurance policies added yet</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Store policy numbers, coverage details, and get automated alerts ahead of renewal deadlines.
              </p>
              <button
                onClick={() => setShowAddPolicyModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition-all mt-2"
              >
                <Plus className="w-4 h-4" />
                Add Insurance Policy
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {policies.map((pol) => (
                <div
                  key={pol.id}
                  className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-emerald-500/40 transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                        <ShieldCheck className="w-5 h-5" />
                      </div>
                      <span className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${
                        pol.is_expired
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                          : pol.is_expiring_soon
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse'
                          : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      }`}>
                        {pol.is_expired ? 'EXPIRED' : `Renewal: in ${pol.days_until_expiry}d`}
                      </span>
                    </div>

                    <h4 className="text-base font-semibold text-white mb-1">{pol.policy_name}</h4>
                    <p className="text-xs text-slate-400 font-mono mb-3">
                      Provider: <span className="text-slate-200">{pol.provider}</span> &bull; Type: <span className="text-slate-200">{pol.policy_type}</span>
                    </p>

                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 grid grid-cols-2 gap-3 text-xs mb-4">
                      <div>
                        <span className="text-slate-500 text-[10px] font-mono block">POLICY NUMBER</span>
                        <span className="text-slate-200 font-mono font-semibold">{pol.policy_number}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 text-[10px] font-mono block">PREMIUM</span>
                        <span className="text-emerald-400 font-mono font-bold">
                          ₹{pol.premium_amount.toLocaleString()} / {pol.premium_frequency.toLowerCase()}
                        </span>
                      </div>
                      {pol.coverage_amount && (
                        <div>
                          <span className="text-slate-500 text-[10px] font-mono block">SUM INSURED</span>
                          <span className="text-cyan-400 font-mono font-semibold">₹{pol.coverage_amount.toLocaleString()}</span>
                        </div>
                      )}
                      <div>
                        <span className="text-slate-500 text-[10px] font-mono block">EXPIRY DATE</span>
                        <span className="text-slate-200 font-mono">{new Date(pol.expiry_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                    <span className="truncate max-w-[200px]">{pol.notes || 'No remarks attached'}</span>
                    <button
                      onClick={() => handleDeletePolicy(pol.id)}
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: IMPORTANT DATES */}
      {activeTab === 'dates' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-purple-400" />
              Administrative Milestone Timeline
            </h3>
            <button
              onClick={() => setShowAddDateModal(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-xs font-semibold transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Milestone
            </button>
          </div>

          {importantDates.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
              <Calendar className="w-10 h-10 text-slate-600 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No milestones registered</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Track passport renewals, college submission cutoffs, warranty expiries, and licenses.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {importantDates.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 shrink-0">
                      <Calendar className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-white truncate">{item.title}</h4>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 font-mono mt-0.5">
                        Date: {new Date(item.date).toLocaleDateString()} {item.description ? `\u2022 ${item.description}` : ''}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className={`text-xs font-mono font-semibold px-2.5 py-1 rounded-xl border ${
                      item.days_remaining < 0
                        ? 'bg-slate-800 text-slate-500 border-slate-700'
                        : item.days_remaining <= 14
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                        : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                    }`}>
                      {item.days_remaining < 0 ? 'Passed' : `${item.days_remaining} days left`}
                    </span>
                    <button
                      onClick={() => handleDeleteImportantDate(item.id)}
                      className="p-2 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 6: REMINDERS */}
      {activeTab === 'reminders' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Bell className="w-4 h-4 text-cyan-400" />
              Administrative Checklist & Notifications
            </h3>
            <button
              onClick={() => setShowAddReminderModal(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Reminder
            </button>
          </div>

          {reminders.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
              <Bell className="w-10 h-10 text-slate-600 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No pending reminders</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                All administrative tasks and alerts are currently resolved.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {reminders.map((rem) => (
                <div
                  key={rem.id}
                  className={`p-4 rounded-2xl border transition-all flex items-center justify-between gap-4 ${
                    rem.is_completed
                      ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                      : 'bg-slate-900/60 border-slate-800 hover:border-cyan-500/40'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <button
                      onClick={() => handleToggleReminder(rem.id)}
                      className={`w-6 h-6 rounded-lg border flex items-center justify-center transition-all ${
                        rem.is_completed
                          ? 'bg-emerald-500 border-emerald-400 text-slate-950'
                          : 'border-slate-700 hover:border-cyan-400 bg-slate-950'
                      }`}
                    >
                      {rem.is_completed && <Check className="w-4 h-4" />}
                    </button>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className={`text-sm font-medium ${rem.is_completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                          {rem.title}
                        </h4>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                          rem.priority === 'CRITICAL' || rem.priority === 'HIGH'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                            : 'bg-slate-800 text-slate-400'
                        }`}>
                          {rem.priority}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">
                        Due: {new Date(rem.due_at).toLocaleDateString()} {rem.description ? `\u2022 ${rem.description}` : ''}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleDeleteReminder(rem.id)}
                    className="p-2 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors shrink-0"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MODAL 1: UPLOAD DOCUMENT */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-cyan-500/40 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-[0_0_50px_rgba(6,182,212,0.2)] max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Upload className="w-4 h-4 text-cyan-400" />
                Upload Document to Vault
              </h3>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">FILE SELECTION *</label>
                <input
                  type="file"
                  required
                  accept=".pdf,.png,.jpg,.jpeg,.docx,.txt,.csv"
                  onChange={(e) => {
                    const f = e.target.files?.[0] || null;
                    setUploadFile(f);
                    if (f && !uploadTitle) setUploadTitle(f.name.replace(/\.[^/.]+$/, ''));
                  }}
                  className="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cyan-500/20 file:text-cyan-300 hover:file:bg-cyan-500/30 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">DOCUMENT TITLE</label>
                <input
                  type="text"
                  placeholder="e.g. Passport 2026, Semester 6 Grade Card"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">CATEGORY</label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value as DocumentCategory)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                  >
                    <option value="IDENTITY">IDENTITY</option>
                    <option value="EDUCATION">EDUCATION</option>
                    <option value="INSURANCE">INSURANCE</option>
                    <option value="FINANCE">FINANCE</option>
                    <option value="BILLS">BILLS</option>
                    <option value="MEDICAL">MEDICAL</option>
                    <option value="TRAVEL">TRAVEL</option>
                    <option value="CERTIFICATES">CERTIFICATES</option>
                    <option value="LEGAL">LEGAL</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">ISSUING AUTHORITY</label>
                  <input
                    type="text"
                    placeholder="e.g. RTO, College, Star Health"
                    value={uploadIssuer}
                    onChange={(e) => setUploadIssuer(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">REFERENCE / ID NUMBER</label>
                  <input
                    type="text"
                    placeholder="e.g. DL-9021-X, Policy #892"
                    value={uploadRefNo}
                    onChange={(e) => setUploadRefNo(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">EXPIRY DATE (OPTIONAL)</label>
                  <input
                    type="date"
                    value={uploadExpiryDate}
                    onChange={(e) => setUploadExpiryDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">TAGS (COMMA-SEPARATED)</label>
                <input
                  type="text"
                  placeholder="e.g. passport, urgent, visa"
                  value={uploadTags}
                  onChange={(e) => setUploadTags(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">DESCRIPTION / REMARKS</label>
                <textarea
                  rows={2}
                  placeholder="Additional notes..."
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading || !uploadFile}
                  className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold tracking-wide transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  {isUploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {isUploading ? 'Securing Document...' : 'Upload & Encrypt'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: ADD BILL */}
      {showAddBillModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-pink-500/40 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-[0_0_50px_rgba(236,72,153,0.2)]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Receipt className="w-4 h-4 text-pink-400" />
                Add Bill / Invoice Record
              </h3>
              <button onClick={() => setShowAddBillModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateBill} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">BILL TITLE *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Airtel Fiber, College Mess, Electricity"
                  value={billTitle}
                  onChange={(e) => setBillTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-pink-500/60"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">PROVIDER / VENDOR *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. BESCOM, Airtel, Campus Hostel"
                    value={billProvider}
                    onChange={(e) => setBillProvider(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-pink-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">AMOUNT (₹) *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    placeholder="e.g. 1450.00"
                    value={billAmount}
                    onChange={(e) => setBillAmount(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-pink-500/60"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">DUE DATE *</label>
                  <input
                    type="date"
                    required
                    value={billDueDate}
                    onChange={(e) => setBillDueDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-pink-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">CATEGORY</label>
                  <input
                    type="text"
                    placeholder="e.g. UTILITIES, INTERNET, RENT"
                    value={billCategory}
                    onChange={(e) => setBillCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-pink-500/60"
                  />
                </div>
              </div>

              <div className="flex items-center gap-4 pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={billRecurring}
                    onChange={(e) => setBillRecurring(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-800 text-pink-500 focus:ring-0"
                  />
                  <span>Recurring Bill</span>
                </label>

                {billRecurring && (
                  <select
                    value={billRecurrence}
                    onChange={(e) => setBillRecurrence(e.target.value as any)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-slate-200"
                  >
                    <option value="MONTHLY">Monthly</option>
                    <option value="QUARTERLY">Quarterly</option>
                    <option value="YEARLY">Yearly</option>
                  </select>
                )}
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddBillModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-pink-500 hover:bg-pink-400 text-slate-950 font-bold tracking-wide transition-all"
                >
                  Save Bill Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: ADD INSURANCE POLICY */}
      {showAddPolicyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-[0_0_50px_rgba(16,185,129,0.2)]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Add Insurance Policy
              </h3>
              <button onClick={() => setShowAddPolicyModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreatePolicy} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">INSURANCE PROVIDER *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Star Health, Acko, HDFC Ergo"
                    value={polProvider}
                    onChange={(e) => setPolProvider(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">POLICY TYPE</label>
                  <select
                    value={polType}
                    onChange={(e) => setPolType(e.target.value as PolicyType)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                  >
                    <option value="HEALTH">HEALTH</option>
                    <option value="VEHICLE">VEHICLE</option>
                    <option value="LIFE">LIFE</option>
                    <option value="TRAVEL">TRAVEL</option>
                    <option value="HOME">HOME</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">POLICY NAME *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Comprehensive Family Health Shield"
                  value={polName}
                  onChange={(e) => setPolName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">POLICY NUMBER *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. POL-890123-X"
                    value={polNumber}
                    onChange={(e) => setPolNumber(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">EXPIRY / RENEWAL DATE *</label>
                  <input
                    type="date"
                    required
                    value={polExpiryDate}
                    onChange={(e) => setPolExpiryDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">PREMIUM AMOUNT (₹) *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    placeholder="e.g. 12500"
                    value={polPremium}
                    onChange={(e) => setPolPremium(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">PREMIUM FREQUENCY</label>
                  <select
                    value={polFrequency}
                    onChange={(e) => setPolFrequency(e.target.value as PremiumFrequency)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                  >
                    <option value="YEARLY">Yearly</option>
                    <option value="MONTHLY">Monthly</option>
                    <option value="QUARTERLY">Quarterly</option>
                    <option value="ONE_TIME">One-Time</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">SUM INSURED / COVERAGE (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="e.g. 500000"
                  value={polCoverage}
                  onChange={(e) => setPolCoverage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500/60"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddPolicyModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold tracking-wide transition-all"
                >
                  Register Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 4: ADD IMPORTANT DATE */}
      {showAddDateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-purple-500/40 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-[0_0_50px_rgba(168,85,247,0.2)]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-400" />
                Add Milestone / Renewal Date
              </h3>
              <button onClick={() => setShowAddDateModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateImportantDate} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">EVENT / MILESTONE TITLE *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Passport Expiry, Driving License Renewal, Laptop Warranty"
                  value={dateTitle}
                  onChange={(e) => setDateTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500/60"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">DATE *</label>
                  <input
                    type="date"
                    required
                    value={dateValue}
                    onChange={(e) => setDateValue(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">CATEGORY</label>
                  <select
                    value={dateCategory}
                    onChange={(e) => setDateCategory(e.target.value as ImportantDateCategory)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500/60"
                  >
                    <option value="PASSPORT">PASSPORT</option>
                    <option value="LICENSE">LICENSE</option>
                    <option value="WARRANTY">WARRANTY</option>
                    <option value="COLLEGE">COLLEGE</option>
                    <option value="RENEWAL">RENEWAL</option>
                    <option value="ANNIVERSARY">ANNIVERSARY</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">DESCRIPTION</label>
                <textarea
                  rows={2}
                  placeholder="Notes or requirements..."
                  value={dateDescription}
                  onChange={(e) => setDateDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500/60"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddDateModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-500 hover:bg-purple-400 text-slate-950 font-bold tracking-wide transition-all"
                >
                  Save Milestone
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 5: ADD REMINDER */}
      {showAddReminderModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-cyan-500/40 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-[0_0_50px_rgba(6,182,212,0.2)]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Bell className="w-4 h-4 text-cyan-400" />
                Add Administrative Reminder
              </h3>
              <button onClick={() => setShowAddReminderModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateReminder} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">REMINDER TITLE *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Submit Medical Reimbursement Form"
                  value={remTitle}
                  onChange={(e) => setRemTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">DUE DATE *</label>
                  <input
                    type="date"
                    required
                    value={remDueDate}
                    onChange={(e) => setRemDueDate(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1 font-mono">PRIORITY</label>
                  <select
                    value={remPriority}
                    onChange={(e) => setRemPriority(e.target.value as ReminderPriority)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">DESCRIPTION</label>
                <textarea
                  rows={2}
                  placeholder="Instructions or attached requirements..."
                  value={remDescription}
                  onChange={(e) => setRemDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500/60"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddReminderModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold tracking-wide transition-all"
                >
                  Save Reminder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 6: DOCUMENT DETAILS PREVIEW */}
      {selectedDocPreview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-cyan-500/40 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-[0_0_50px_rgba(6,182,212,0.2)]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                Document Metadata & Security
              </h3>
              <button onClick={() => setSelectedDocPreview(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500 font-mono block">TITLE</span>
                <span className="text-sm font-semibold text-white">{selectedDocPreview.title}</span>
              </div>

              <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-950 border border-slate-800/80">
                <div>
                  <span className="text-slate-500 font-mono block">CATEGORY</span>
                  <span className="text-cyan-400 font-semibold">{selectedDocPreview.category}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-mono block">FILE SIZE</span>
                  <span className="text-slate-300 font-mono">{selectedDocPreview.file_size} KB</span>
                </div>
                <div>
                  <span className="text-slate-500 font-mono block">ISSUER</span>
                  <span className="text-slate-300">{selectedDocPreview.issuer || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-mono block">REFERENCE #</span>
                  <span className="text-slate-300 font-mono">{selectedDocPreview.reference_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-mono block">STORED FILENAME</span>
                  <span className="text-slate-400 font-mono truncate block">{selectedDocPreview.filename}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-mono block">EXPIRY DATE</span>
                  <span className="text-slate-300 font-mono">
                    {selectedDocPreview.expiry_date ? new Date(selectedDocPreview.expiry_date).toLocaleDateString() : 'None'}
                  </span>
                </div>
              </div>

              {selectedDocPreview.extracted_text_preview && (
                <div>
                  <span className="text-slate-500 font-mono block mb-1">EXTRACTED TEXT PREVIEW</span>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] text-slate-400 font-mono max-h-32 overflow-y-auto">
                    {selectedDocPreview.extracted_text_preview}
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <button
                onClick={() => handleDeleteDocument(selectedDocPreview.id)}
                className="px-3 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs transition-colors"
              >
                Delete Document
              </button>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedDocPreview(null)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs"
                >
                  Close
                </button>
                <button
                  onClick={() => handleDownloadDocument(selectedDocPreview)}
                  className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
