'use client';

import React, { useState, useEffect } from 'react';
import { 
  Wallet, TrendingUp, TrendingDown, Plus, CreditCard, 
  Sparkles, DollarSign, Calendar, AlertTriangle, ArrowUpRight 
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { FinanceAnalytics, TransactionItem, SubscriptionItem, ExpenseCategory } from '@/types';

export const FinanceView: React.FC = () => {
  const [analytics, setAnalytics] = useState<FinanceAnalytics | null>(null);
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Quick expense form
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [categoryName, setCategoryName] = useState('Food & Dining');

  const loadFinanceData = async () => {
    try {
      setLoading(true);
      const [analyticsData, subsData] = await Promise.all([
        ApiService.getFinanceAnalytics(),
        ApiService.getSubscriptions(),
      ]);
      setAnalytics(analyticsData);
      setSubscriptions(subsData || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFinanceData();
  }, []);

  const handleCreateExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !amount.trim()) return;

    try {
      await ApiService.createTransaction({
        title,
        amount: parseFloat(amount),
        category_name: categoryName,
        type: 'EXPENSE',
      });
      setTitle('');
      setAmount('');
      setShowAddExpense(false);
      await loadFinanceData();
    } catch (err: any) {
      alert(`Could not log expense: ${err.message}`);
    }
  };

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
            Intelligent cash flow tracking, burn rate projections, subscription auditing, and budget forecasting.
          </p>
        </div>

        <button
          onClick={() => setShowAddExpense(!showAddExpense)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Record Expense</span>
        </button>
      </div>

      {/* Add Expense Form */}
      {showAddExpense && (
        <form
          onSubmit={handleCreateExpense}
          className="p-5 rounded-2xl glass-panel-glow border border-emerald-500/30 space-y-4 animate-in fade-in slide-in-from-top-2"
        >
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <CreditCard className="w-4 h-4 text-emerald-400" />
            <span>Log New Transaction</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input
              type="text"
              placeholder="Title (e.g. Campus Cafeteria Lunch)"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
              required
            />
            <input
              type="number"
              step="0.01"
              placeholder="Amount (₹)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
              required
            />
            <select
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="Food & Dining">Food & Dining</option>
              <option value="College & Books">College & Books</option>
              <option value="Travel & Transit">Travel & Transit</option>
              <option value="Bills & Utilities">Bills & Utilities</option>
              <option value="Subscriptions">Subscriptions</option>
              <option value="Shopping & Leisure">Shopping & Leisure</option>
            </select>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddExpense(false)}
              className="px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold cursor-pointer"
            >
              Save Transaction
            </button>
          </div>
        </form>
      )}

      {/* 1. Monthly Budget Overview Matrix */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Monthly Limit */}
          <div className="p-5 rounded-2xl glass-panel">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
              Monthly Budget Target
            </span>
            <div className="text-2xl font-black text-white">
              ₹{analytics.monthly_budget_target.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-gray-500 mt-1 block">Configured spending cap</span>
          </div>

          {/* Spent Amount */}
          <div className="p-5 rounded-2xl glass-panel">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
              Total Spent This Month
            </span>
            <div className="text-2xl font-black text-rose-400">
              ₹{analytics.total_expenses.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-rose-300 font-semibold mt-1 block">
              {analytics.budget_used_percentage}% utilized
            </span>
          </div>

          {/* Remaining Budget */}
          <div className="p-5 rounded-2xl glass-panel">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
              Remaining Safe Balance
            </span>
            <div className="text-2xl font-black text-emerald-400">
              ₹{analytics.remaining_budget.toLocaleString('en-IN')}
            </div>
            <span className="text-[11px] text-emerald-300 font-semibold mt-1 block">
              {analytics.is_over_budget ? 'Budget Exceeded' : 'Within Safe Range'}
            </span>
          </div>

          {/* Burn Rate */}
          <div className="p-5 rounded-2xl glass-panel">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
              Average Daily Burn Rate
            </span>
            <div className="text-2xl font-black text-cyan-400">
              ₹{analytics.burn_rate_per_day.toLocaleString('en-IN')}
              <span className="text-xs text-gray-400 font-normal"> / day</span>
            </div>
            <span className="text-[11px] text-gray-400 mt-1 block">
              Projected end: ₹{analytics.projected_month_end_expense.toLocaleString('en-IN')}
            </span>
          </div>
        </div>
      )}

      {/* 2. Spending Categories & Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown */}
        <div className="p-5 rounded-2xl glass-panel">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>Category Spending Breakdown</span>
          </h3>

          <div className="space-y-4">
            {analytics?.top_categories?.map((cat, idx) => (
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
                    ₹{cat.amount.toLocaleString('en-IN')}{' '}
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
            {(!analytics?.top_categories || analytics.top_categories.length === 0) && (
              <p className="text-xs text-gray-500 text-center py-4">No categorized expenses.</p>
            )}
          </div>
        </div>

        {/* Recent Transactions Ledger */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-panel">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-cyan-400" />
              <span>Recent Transactions</span>
            </div>
            <span className="text-xs text-gray-400">
              {analytics?.recent_transactions?.length || 0} Records
            </span>
          </h3>

          <div className="space-y-2.5">
            {analytics?.recent_transactions?.map((tx) => (
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
                      {tx.category_name} • {tx.date} • {tx.payment_method}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className={`font-black text-xs ${
                      tx.type === 'INCOME' ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {tx.type === 'INCOME' ? '+' : '-'}₹{tx.amount.toLocaleString('en-IN')}
                  </span>
                </div>
              </div>
            ))}
            {(!analytics?.recent_transactions || analytics.recent_transactions.length === 0) && (
              <p className="text-xs text-gray-500 text-center py-6">
                No recent transactions recorded.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
