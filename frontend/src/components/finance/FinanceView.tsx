'use client';

import React, { useState, useEffect } from 'react';
import { 
  Wallet, TrendingUp, TrendingDown, Plus, CreditCard, 
  Sparkles, DollarSign, Calendar, AlertTriangle, ArrowUpRight,
  ArrowDownLeft, PieChart, BarChart3, Repeat, Search, Filter,
  Trash2, Edit2, CheckCircle2, PauseCircle, PlayCircle, Clock,
  ChevronRight, RefreshCw, X, ShieldAlert, Tag
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { 
  FinanceDashboardData, TransactionItem, SubscriptionItem, 
  ExpenseCategory, BudgetItem, BudgetUsageSummary, SpendingTrendsResponse,
  CategoryType, TransactionType, PaymentMethod, BillingCycle, SubscriptionStatus 
} from '@/types';

type FinanceTab = 'overview' | 'transactions' | 'budgets' | 'subscriptions' | 'analytics';

export const FinanceView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<FinanceTab>('overview');
  const [dashboard, setDashboard] = useState<FinanceDashboardData | null>(null);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [budgetSummary, setBudgetSummary] = useState<BudgetUsageSummary | null>(null);
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[]>([]);
  const [trends, setTrends] = useState<SpendingTrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters for Transactions tab
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('this_month');

  // Modals
  const [showTxModal, setShowTxModal] = useState(false);
  const [txModalType, setTxModalType] = useState<TransactionType>('EXPENSE');
  const [txTitle, setTxTitle] = useState('');
  const [txAmount, setTxAmount] = useState('');
  const [txMerchant, setTxMerchant] = useState('');
  const [txCategory, setTxCategory] = useState('');
  const [txDate, setTxDate] = useState(new Date().toISOString().split('T')[0]);
  const [txPaymentMethod, setTxPaymentMethod] = useState<PaymentMethod>('UPI');
  const [txNotes, setTxNotes] = useState('');

  // Budget Modal
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [budgetAmount, setBudgetAmount] = useState('');
  const [budgetCategory, setBudgetCategory] = useState<string>(''); // empty = overall

  // Category Modal
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [catName, setCatName] = useState('');
  const [catType, setCatType] = useState<CategoryType>('EXPENSE');
  const [catColor, setCatColor] = useState('#10B981');
  const [catBudgetLimit, setCatBudgetLimit] = useState('');

  // Subscription Modal
  const [showSubModal, setShowSubModal] = useState(false);
  const [subName, setSubName] = useState('');
  const [subAmount, setSubAmount] = useState('');
  const [subCycle, setSubCycle] = useState<BillingCycle>('MONTHLY');
  const [subNextDate, setSubNextDate] = useState('');
  const [subPaymentMethod, setSubPaymentMethod] = useState<PaymentMethod>('UPI');
  const [subCategory, setSubCategory] = useState('');

  const loadAllFinanceData = async () => {
    try {
      setLoading(true);
      const [dashData, txListData, catsData, bSummary, subsData, trendsData] = await Promise.all([
        ApiService.getFinanceDashboard(),
        ApiService.getTransactions({ time_range: selectedTimeRange, limit: 100 }),
        ApiService.getCategories(),
        ApiService.getBudgetSummary(),
        ApiService.getSubscriptions(),
        ApiService.getSpendingTrends(6),
      ]);
      setDashboard(dashData);
      setTransactions(txListData?.transactions || []);
      setCategories(catsData || []);
      setBudgetSummary(bSummary);
      setSubscriptions(subsData || []);
      setTrends(trendsData);
    } catch (e) {
      console.error("Failed to load financial data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllFinanceData();
  }, [selectedTimeRange]);

  const handleCreateTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txTitle.trim() || !txAmount.trim() || parseFloat(txAmount) <= 0) {
      alert('Please enter a valid title and positive amount');
      return;
    }

    try {
      await ApiService.createTransaction({
        title: txTitle.trim(),
        amount: parseFloat(txAmount),
        type: txModalType,
        transaction_type: txModalType,
        merchant: txMerchant.trim() || undefined,
        category_id: txCategory || undefined,
        date: txDate || new Date().toISOString().split('T')[0],
        payment_method: txPaymentMethod,
        notes: txNotes.trim() || undefined,
      });
      // Reset form
      setTxTitle('');
      setTxAmount('');
      setTxMerchant('');
      setTxNotes('');
      setShowTxModal(false);
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not log transaction: ${err.message}`);
    }
  };

  const handleDeleteTransaction = async (id: string) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await ApiService.deleteTransaction(id);
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not delete transaction: ${err.message}`);
    }
  };

  const handleSetBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!budgetAmount.trim() || parseFloat(budgetAmount) <= 0) return;

    try {
      const now = new Date();
      await ApiService.setBudget({
        amount: parseFloat(budgetAmount),
        category_id: budgetCategory || undefined,
        month: now.getMonth() + 1,
        year: now.getFullYear(),
      });
      setBudgetAmount('');
      setShowBudgetModal(false);
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not update budget: ${err.message}`);
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!catName.trim()) return;

    try {
      await ApiService.createCategory({
        name: catName.trim(),
        category_type: catType,
        color: catColor,
        budget_limit: catBudgetLimit ? parseFloat(catBudgetLimit) : undefined,
      });
      setCatName('');
      setCatBudgetLimit('');
      setShowCategoryModal(false);
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not create category: ${err.message}`);
    }
  };

  const handleCreateSubscription = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subName.trim() || !subAmount.trim() || !subNextDate) {
      alert('Please fill in subscription name, amount, and renewal date');
      return;
    }

    try {
      await ApiService.createSubscription({
        name: subName.trim(),
        amount: parseFloat(subAmount),
        billing_cycle: subCycle,
        next_billing_date: subNextDate,
        payment_method: subPaymentMethod,
        category_id: subCategory || undefined,
        status: 'ACTIVE',
      });
      setSubName('');
      setSubAmount('');
      setSubNextDate('');
      setShowSubModal(false);
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not add subscription: ${err.message}`);
    }
  };

  const handleToggleSubStatus = async (sub: SubscriptionItem) => {
    const nextStatus: SubscriptionStatus = sub.status === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
    try {
      await ApiService.updateSubscription(sub.id, { status: nextStatus });
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not update subscription: ${err.message}`);
    }
  };

  const handleDeleteSubscription = async (id: string) => {
    if (!confirm('Are you sure you want to remove this subscription?')) return;
    try {
      await ApiService.deleteSubscription(id);
      await loadAllFinanceData();
    } catch (err: any) {
      alert(`Could not delete subscription: ${err.message}`);
    }
  };

  // Filtered transactions for list view
  const filteredTransactions = transactions.filter(t => {
    const matchesSearch = !searchQuery || 
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (t.merchant && t.merchant.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.category_name && t.category_name.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesType = selectedType === 'ALL' || t.type === selectedType || t.transaction_type === selectedType;
    const matchesCat = selectedCategory === 'ALL' || t.category_id === selectedCategory;

    return matchesSearch && matchesType && matchesCat;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Dimension Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Wallet className="w-4 h-4" />
            <span>Dimension: AI Money Manager</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">Financial Intelligence</h2>
          <p className="text-xs text-gray-400">
            Authoritative cash flow tracking, deterministic burn rate analytics, budget governance, and recurring billing manager.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          <button
            onClick={() => {
              setTxModalType('INCOME');
              setShowTxModal(true);
            }}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-bold transition-all cursor-pointer"
          >
            <ArrowDownLeft className="w-4 h-4" />
            <span>+ Income</span>
          </button>
          <button
            onClick={() => {
              setTxModalType('EXPENSE');
              setShowTxModal(true);
            }}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs shadow-lg shadow-rose-600/30 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>+ Record Expense</span>
          </button>
        </div>
      </div>

      {/* Sub-Dimension Tabs */}
      <div className="flex items-center gap-2 p-1.5 rounded-2xl glass-panel border border-white/10 overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'overview'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Wallet className="w-3.5 h-3.5" />
          <span>Overview</span>
        </button>
        <button
          onClick={() => setActiveTab('transactions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'transactions'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <CreditCard className="w-3.5 h-3.5" />
          <span>Transactions ({transactions.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('budgets')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'budgets'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <PieChart className="w-3.5 h-3.5" />
          <span>Budgets & Categories</span>
        </button>
        <button
          onClick={() => setActiveTab('subscriptions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'subscriptions'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Repeat className="w-3.5 h-3.5" />
          <span>Subscriptions ({subscriptions.filter(s => s.is_active).length})</span>
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'analytics'
              ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
              : 'text-gray-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Trends & Analytics</span>
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* 1. Monthly Matrix Summary Cards */}
          {dashboard && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Monthly Income */}
              <div className="p-5 rounded-2xl glass-panel border border-emerald-500/20 bg-gradient-to-br from-emerald-950/20 to-transparent">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                    Total Inflow ({dashboard.period})
                  </span>
                  <ArrowDownLeft className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-2xl font-black text-emerald-400">
                  ₹{Number(dashboard.total_income).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <span className="text-[11px] text-gray-400 mt-1 block">
                  Savings rate: <strong className="text-emerald-300 font-bold">{dashboard.savings_percentage}%</strong>
                </span>
              </div>

              {/* Total Expenses */}
              <div className="p-5 rounded-2xl glass-panel border border-rose-500/20 bg-gradient-to-br from-rose-950/20 to-transparent">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                    Total Outflow
                  </span>
                  <TrendingDown className="w-4 h-4 text-rose-400" />
                </div>
                <div className="text-2xl font-black text-rose-400">
                  ₹{Number(dashboard.total_expenses).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <span className="text-[11px] text-rose-300 font-semibold mt-1 block">
                  {dashboard.budget_used_percentage}% of budget used
                </span>
              </div>

              {/* Budget Remaining */}
              <div className="p-5 rounded-2xl glass-panel border border-cyan-500/20 bg-gradient-to-br from-cyan-950/20 to-transparent">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                    Remaining Budget
                  </span>
                  {dashboard.is_over_budget ? (
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  )}
                </div>
                <div className={`text-2xl font-black ${dashboard.is_over_budget ? 'text-rose-400' : 'text-cyan-400'}`}>
                  ₹{Number(dashboard.remaining_budget).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <span className={`text-[11px] font-semibold mt-1 block ${dashboard.is_over_budget ? 'text-rose-400' : 'text-cyan-300'}`}>
                  {dashboard.is_over_budget ? 'Over Budget by Exceeded Cap' : 'Within Target Budget'}
                </span>
              </div>

              {/* Daily Burn Rate */}
              <div className="p-5 rounded-2xl glass-panel border border-amber-500/20 bg-gradient-to-br from-amber-950/20 to-transparent">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                    Daily Burn Rate
                  </span>
                  <Clock className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-2xl font-black text-amber-400">
                  ₹{Number(dashboard.burn_rate_per_day).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  <span className="text-xs text-gray-400 font-normal"> / day</span>
                </div>
                <span className="text-[11px] text-gray-400 mt-1 block">
                  Projected End: ₹{Number(dashboard.projected_month_end_expense).toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          )}

          {/* 2. Budget Governance Bar */}
          {dashboard && (
            <div className="p-5 rounded-2xl glass-panel border border-white/10 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white flex items-center gap-2">
                  <PieChart className="w-4 h-4 text-emerald-400" />
                  Monthly Spending Cap: ₹{Number(dashboard.monthly_budget_target).toLocaleString('en-IN')}
                </span>
                <span className={`font-bold ${dashboard.is_over_budget ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {dashboard.budget_used_percentage}% utilized
                </span>
              </div>
              <div className="w-full bg-white/5 h-2.5 rounded-full overflow-hidden p-0.5 border border-white/10">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    dashboard.is_over_budget ? 'bg-rose-500 shadow-md shadow-rose-500/50' : 'bg-emerald-500 shadow-md shadow-emerald-500/50'
                  }`}
                  style={{ width: `${Math.min(100, dashboard.budget_used_percentage)}%` }}
                />
              </div>
            </div>
          )}

          {/* 3. Category Breakdown & Recent Transactions */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Top Categories */}
            <div className="p-5 rounded-2xl glass-panel space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span>Category Outflow</span>
                </h3>
                <button
                  onClick={() => setActiveTab('budgets')}
                  className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold cursor-pointer"
                >
                  Manage
                </button>
              </div>

              <div className="space-y-3.5">
                {dashboard?.top_categories?.map((cat, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: cat.color }}
                        />
                        <span className="font-semibold text-gray-200">{cat.category_name}</span>
                      </div>
                      <div className="font-bold text-white">
                        ₹{Number(cat.amount).toLocaleString('en-IN')}{' '}
                        <span className="text-[10px] text-gray-400 font-normal">
                          ({cat.percentage}%)
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${cat.percentage}%`,
                          backgroundColor: cat.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
                {(!dashboard?.top_categories || dashboard.top_categories.length === 0) && (
                  <div className="text-center py-6 space-y-2">
                    <p className="text-xs text-gray-500">No expenses recorded this month.</p>
                    <button
                      onClick={() => {
                        setTxModalType('EXPENSE');
                        setShowTxModal(true);
                      }}
                      className="text-xs text-emerald-400 hover:underline font-semibold"
                    >
                      + Record your first expense
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Transactions List */}
            <div className="lg:col-span-2 p-5 rounded-2xl glass-panel space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <CreditCard className="w-4 h-4 text-cyan-400" />
                  <span>Recent Ledger Activity</span>
                </h3>
                <button
                  onClick={() => setActiveTab('transactions')}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold cursor-pointer"
                >
                  View All ({transactions.length})
                </button>
              </div>

              <div className="space-y-2.5">
                {dashboard?.recent_transactions?.map((tx) => (
                  <div
                    key={tx.id}
                    className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between hover:border-white/15 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold"
                        style={{ backgroundColor: `${tx.category_color}20`, color: tx.category_color }}
                      >
                        ₹
                      </div>
                      <div>
                        <h4 className="font-bold text-xs text-white">{tx.title}</h4>
                        <span className="text-[10px] text-gray-400">
                          {tx.category_name} {tx.merchant ? `• ${tx.merchant}` : ''} • {tx.date} • {tx.payment_method}
                        </span>
                      </div>
                    </div>

                    <div className="text-right">
                      <span
                        className={`font-black text-xs ${
                          tx.type === 'INCOME' || tx.transaction_type === 'INCOME' ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {tx.type === 'INCOME' || tx.transaction_type === 'INCOME' ? '+' : '-'}₹{Number(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>
                ))}
                {(!dashboard?.recent_transactions || dashboard.recent_transactions.length === 0) && (
                  <div className="text-center py-8 space-y-2">
                    <CreditCard className="w-8 h-8 text-gray-600 mx-auto" />
                    <p className="text-xs text-gray-400 font-semibold">No transactions yet.</p>
                    <p className="text-[11px] text-gray-500">Add your first expense or income to start tracking.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: TRANSACTIONS LEDGER */}
      {activeTab === 'transactions' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Controls & Filters */}
          <div className="p-4 rounded-2xl glass-panel space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              {/* Search */}
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search title, merchant, notes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              {/* Type Filter */}
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="ALL">All Types (Income & Expense)</option>
                <option value="INCOME">Income Only</option>
                <option value="EXPENSE">Expense Only</option>
              </select>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="ALL">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>

              {/* Time Range Filter */}
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="today">Today</option>
                <option value="this_week">This Week</option>
                <option value="this_month">This Month</option>
                <option value="last_month">Last Month</option>
              </select>
            </div>
          </div>

          {/* Transactions Table */}
          <div className="p-5 rounded-2xl glass-panel space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400 font-semibold">
                Showing {filteredTransactions.length} recorded entries
              </span>
              <button
                onClick={() => {
                  setTxModalType('EXPENSE');
                  setShowTxModal(true);
                }}
                className="text-xs text-emerald-400 hover:text-emerald-300 font-bold cursor-pointer"
              >
                + Add Transaction
              </button>
            </div>

            <div className="space-y-2">
              {filteredTransactions.map((tx) => (
                <div
                  key={tx.id}
                  className="p-3.5 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between hover:border-white/15 transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold shrink-0"
                      style={{ backgroundColor: `${tx.category_color || '#10B981'}20`, color: tx.category_color || '#10B981' }}
                    >
                      ₹
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-xs text-white">{tx.title}</h4>
                        {tx.merchant && (
                          <span className="px-2 py-0.5 rounded-md bg-white/5 text-[10px] text-gray-400 border border-white/5">
                            {tx.merchant}
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-gray-400 flex items-center gap-2 mt-0.5">
                        <span style={{ color: tx.category_color }}>{tx.category_name}</span>
                        <span>•</span>
                        <span>{tx.date}</span>
                        <span>•</span>
                        <span>{tx.payment_method}</span>
                        {tx.notes && <span>• {tx.notes}</span>}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`font-black text-sm ${
                        tx.type === 'INCOME' || tx.transaction_type === 'INCOME' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {tx.type === 'INCOME' || tx.transaction_type === 'INCOME' ? '+' : '-'}₹{Number(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                    <button
                      onClick={() => handleDeleteTransaction(tx.id)}
                      className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-all cursor-pointer"
                      title="Delete record"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}

              {filteredTransactions.length === 0 && (
                <div className="text-center py-12 space-y-3">
                  <CreditCard className="w-10 h-10 text-gray-600 mx-auto" />
                  <p className="text-sm text-gray-300 font-bold">No transactions found.</p>
                  <p className="text-xs text-gray-500">
                    Try adjusting your search query or date range filters, or record a new transaction.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: BUDGETS & CATEGORIES */}
      {activeTab === 'budgets' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Monthly Budget Governance</h3>
              <p className="text-xs text-gray-400">Configure category-specific limits and overall spending caps.</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowBudgetModal(true)}
                className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs cursor-pointer shadow-lg shadow-emerald-600/30"
              >
                + Set Monthly Budget
              </button>
              <button
                onClick={() => setShowCategoryModal(true)}
                className="px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 border border-white/10 font-bold text-xs cursor-pointer"
              >
                + New Category
              </button>
            </div>
          </div>

          {/* Category Budget Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((cat) => {
              const hasLimit = cat.budget_limit && cat.budget_limit > 0;
              const spent = cat.spent_amount || 0;
              const pct = hasLimit ? Math.round((spent / cat.budget_limit!) * 100) : 0;
              const isOver = hasLimit && spent > cat.budget_limit!;

              return (
                <div
                  key={cat.id}
                  className="p-4 rounded-2xl glass-panel border border-white/10 space-y-3 hover:border-white/20 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div
                        className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold"
                        style={{ backgroundColor: `${cat.color}20`, color: cat.color }}
                      >
                        <Tag className="w-3.5 h-3.5" />
                      </div>
                      <h4 className="font-bold text-xs text-white">{cat.name}</h4>
                    </div>
                    <span className="text-[10px] uppercase font-bold text-gray-400">
                      {cat.category_type}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Spent this month:</span>
                      <span className="font-bold text-white">₹{spent.toLocaleString('en-IN')}</span>
                    </div>
                    {hasLimit && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">Monthly Limit:</span>
                        <span className="font-bold text-gray-300">₹{cat.budget_limit?.toLocaleString('en-IN')}</span>
                      </div>
                    )}
                  </div>

                  {hasLimit && (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-[10px]">
                        <span className={isOver ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                          {isOver ? 'Limit Exceeded' : `${pct}% Used`}
                        </span>
                        <span className="text-gray-400">
                          {cat.budget_limit! - spent >= 0 ? `₹${(cat.budget_limit! - spent).toLocaleString('en-IN')} left` : `-₹${Math.abs(cat.budget_limit! - spent).toLocaleString('en-IN')} over`}
                        </span>
                      </div>
                      <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            isOver ? 'bg-rose-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(100, pct)}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 4: SUBSCRIPTIONS */}
      {activeTab === 'subscriptions' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Recurring Subscriptions Auditor</h3>
              <p className="text-xs text-gray-400">Track automatic renewals, monthly cost equivalents, and status.</p>
            </div>
            <button
              onClick={() => setShowSubModal(true)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Add Subscription</span>
            </button>
          </div>

          {/* Subscriptions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {subscriptions.map((sub) => (
              <div
                key={sub.id}
                className="p-5 rounded-2xl glass-panel border border-white/10 space-y-4 hover:border-white/20 transition-all group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-xs">
                      <Repeat className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-white">{sub.name}</h4>
                      <span className="text-[10px] text-gray-400">
                        {sub.billing_cycle} • {sub.payment_method}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      sub.is_active
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {sub.status}
                  </span>
                </div>

                <div className="space-y-1.5 pt-2 border-t border-white/5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Billed Amount:</span>
                    <span className="font-black text-white">₹{Number(sub.amount).toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Monthly Equivalent:</span>
                    <span className="font-bold text-cyan-400">₹{Number(sub.monthly_equivalent).toLocaleString('en-IN')}/mo</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Next Renewal:</span>
                    <span className="font-semibold text-gray-300">{sub.next_billing_date}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <button
                    onClick={() => handleToggleSubStatus(sub)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-white cursor-pointer"
                  >
                    {sub.is_active ? (
                      <>
                        <PauseCircle className="w-3.5 h-3.5 text-amber-400" />
                        <span>Pause</span>
                      </>
                    ) : (
                      <>
                        <PlayCircle className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Resume</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => handleDeleteSubscription(sub.id)}
                    className="p-1 rounded-lg text-gray-500 hover:text-rose-400 transition-colors cursor-pointer"
                    title="Delete subscription"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}

            {subscriptions.length === 0 && (
              <div className="col-span-full text-center py-12 space-y-3 glass-panel rounded-2xl">
                <Repeat className="w-10 h-10 text-gray-600 mx-auto" />
                <p className="text-sm text-gray-300 font-bold">No active subscriptions.</p>
                <p className="text-xs text-gray-500">
                  Track recurring services like Spotify, Netflix, or cloud subscriptions here.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: TRENDS & ANALYTICS */}
      {activeTab === 'analytics' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="p-6 rounded-2xl glass-panel space-y-6">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-400" />
              <span>Multi-Month Spending & Inflow Trends</span>
            </h3>

            {/* Historical Bar Chart Visualization */}
            <div className="space-y-4">
              <div className="grid grid-cols-6 gap-2 sm:gap-4 h-48 items-end pt-4 pb-2 border-b border-white/10">
                {trends?.trends?.map((t, idx) => {
                  const maxAmt = Math.max(...(trends.trends.map(x => Math.max(x.income, x.expenses))), 1000);
                  const incHeight = Math.max(5, (t.income / maxAmt) * 100);
                  const expHeight = Math.max(5, (t.expenses / maxAmt) * 100);

                  return (
                    <div key={idx} className="flex flex-col items-center gap-1.5 h-full justify-end group">
                      <div className="flex items-end gap-1 w-full justify-center h-full">
                        {/* Income bar */}
                        <div
                          className="w-2.5 sm:w-4 rounded-t-md bg-emerald-500 transition-all group-hover:brightness-125"
                          style={{ height: `${incHeight}%` }}
                          title={`Income: ₹${t.income.toLocaleString('en-IN')}`}
                        />
                        {/* Expense bar */}
                        <div
                          className="w-2.5 sm:w-4 rounded-t-md bg-rose-500 transition-all group-hover:brightness-125"
                          style={{ height: `${expHeight}%` }}
                          title={`Expenses: ₹${t.expenses.toLocaleString('en-IN')}`}
                        />
                      </div>
                      <span className="text-[10px] font-bold text-gray-400 truncate w-full text-center">
                        {t.month_label}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-center gap-6 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-md bg-emerald-500" />
                  <span className="text-gray-300">Income Inflow</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-md bg-rose-500" />
                  <span className="text-gray-300">Expenses Outflow</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Add Transaction */}
      {showTxModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="w-full max-w-lg p-6 rounded-2xl glass-panel-glow border border-emerald-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-emerald-400" />
                <span>Record {txModalType === 'INCOME' ? 'Income Inflow' : 'Expense Outflow'}</span>
              </h3>
              <button
                onClick={() => setShowTxModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateTransaction} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Title / Description *
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Hostel Cafeteria Lunch, Books, Stipend"
                    value={txTitle}
                    onChange={(e) => setTxTitle(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Amount (₹) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="250.00"
                    value={txAmount}
                    onChange={(e) => setTxAmount(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Category
                  </label>
                  <select
                    value={txCategory}
                    onChange={(e) => setTxCategory(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="">General / Uncategorized</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Merchant / Payee
                  </label>
                  <input
                    type="text"
                    placeholder="Campus Mess, Amazon, Metro"
                    value={txMerchant}
                    onChange={(e) => setTxMerchant(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Payment Method
                  </label>
                  <select
                    value={txPaymentMethod}
                    onChange={(e) => setTxPaymentMethod(e.target.value as PaymentMethod)}
                    className="w-full px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="UPI">UPI</option>
                    <option value="CARD">Debit / Credit Card</option>
                    <option value="CASH">Cash</option>
                    <option value="BANK_TRANSFER">Bank Transfer / Net Banking</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Date
                  </label>
                  <input
                    type="date"
                    value={txDate}
                    onChange={(e) => setTxDate(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Notes
                  </label>
                  <input
                    type="text"
                    placeholder="Optional memo..."
                    value={txNotes}
                    onChange={(e) => setTxNotes(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowTxModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 cursor-pointer"
                >
                  Save Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Set Budget */}
      {showBudgetModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="w-full max-w-md p-6 rounded-2xl glass-panel-glow border border-emerald-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <PieChart className="w-4 h-4 text-emerald-400" />
                <span>Configure Monthly Budget Cap</span>
              </h3>
              <button
                onClick={() => setShowBudgetModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSetBudget} className="space-y-4">
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                  Budget Target (₹) *
                </label>
                <input
                  type="number"
                  step="100"
                  placeholder="e.g. 15000"
                  value={budgetAmount}
                  onChange={(e) => setBudgetAmount(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                  Budget Scope
                </label>
                <select
                  value={budgetCategory}
                  onChange={(e) => setBudgetCategory(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="">Overall Monthly Budget Cap</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} Category Cap
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowBudgetModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold cursor-pointer"
                >
                  Apply Budget
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: New Category */}
      {showCategoryModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="w-full max-w-md p-6 rounded-2xl glass-panel-glow border border-emerald-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Tag className="w-4 h-4 text-emerald-400" />
                <span>Create Custom Category</span>
              </h3>
              <button
                onClick={() => setShowCategoryModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateCategory} className="space-y-4">
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                  Category Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Lab Equipment, Gym, Groceries"
                  value={catName}
                  onChange={(e) => setCatName(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Category Type
                  </label>
                  <select
                    value={catType}
                    onChange={(e) => setCatType(e.target.value as CategoryType)}
                    className="w-full px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="EXPENSE">Expense</option>
                    <option value="INCOME">Income</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Accent Color
                  </label>
                  <input
                    type="color"
                    value={catColor}
                    onChange={(e) => setCatColor(e.target.value)}
                    className="w-full h-9 rounded-xl bg-white/5 border border-white/10 cursor-pointer p-1"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                  Optional Monthly Cap (₹)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 3000"
                  value={catBudgetLimit}
                  onChange={(e) => setCatBudgetLimit(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowCategoryModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold cursor-pointer"
                >
                  Save Category
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Add Subscription */}
      {showSubModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="w-full max-w-md p-6 rounded-2xl glass-panel-glow border border-emerald-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Repeat className="w-4 h-4 text-emerald-400" />
                <span>Add Recurring Subscription</span>
              </h3>
              <button
                onClick={() => setShowSubModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateSubscription} className="space-y-4">
              <div>
                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                  Service / Provider Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Spotify, Netflix, GitHub Copilot"
                  value={subName}
                  onChange={(e) => setSubName(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Amount (₹) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="119.00"
                    value={subAmount}
                    onChange={(e) => setSubAmount(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Billing Cycle
                  </label>
                  <select
                    value={subCycle}
                    onChange={(e) => setSubCycle(e.target.value as BillingCycle)}
                    className="w-full px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="MONTHLY">Monthly</option>
                    <option value="YEARLY">Yearly</option>
                    <option value="QUARTERLY">Quarterly</option>
                    <option value="WEEKLY">Weekly</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Next Renewal Date *
                  </label>
                  <input
                    type="date"
                    value={subNextDate}
                    onChange={(e) => setSubNextDate(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
                    Payment Method
                  </label>
                  <select
                    value={subPaymentMethod}
                    onChange={(e) => setSubPaymentMethod(e.target.value as PaymentMethod)}
                    className="w-full px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="UPI">UPI Autopay</option>
                    <option value="CARD">Credit / Debit Card</option>
                    <option value="BANK_TRANSFER">Bank Mandate</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowSubModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold cursor-pointer"
                >
                  Save Subscription
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
