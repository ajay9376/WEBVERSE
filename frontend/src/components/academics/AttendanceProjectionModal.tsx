'use client';

import React, { useEffect, useState } from 'react';
import { X, TrendingUp, TrendingDown, CheckCircle2, AlertTriangle, ShieldCheck, Calculator } from 'lucide-react';
import { ApiService } from '@/lib/api';
import { AttendanceProjection } from '@/types';

interface AttendanceProjectionModalProps {
  subjectId: string;
  onClose: () => void;
}

export const AttendanceProjectionModal: React.FC<AttendanceProjectionModalProps> = ({ subjectId, onClose }) => {
  const [data, setData] = useState<AttendanceProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjection = async () => {
      try {
        setLoading(true);
        const res = await ApiService.getAttendanceProjection(subjectId);
        setData(res);
      } catch (e: any) {
        setError(e.message || 'Failed to calculate projections');
      } finally {
        setLoading(false);
      }
    };
    fetchProjection();
  }, [subjectId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg p-6 rounded-3xl glass-panel-glow border border-purple-500/40 shadow-2xl bg-slate-950/90 text-white space-y-6">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Calculator className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-black text-base text-white tracking-tight">Attendance Projections</h3>
              <p className="text-xs text-gray-400">Deterministic trajectory simulator</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-gray-400 text-xs">
            <div className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
            <span>Calculating deterministic projection scenarios...</span>
          </div>
        ) : error ? (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : data ? (
          <div className="space-y-5">
            {/* Subject Snapshot */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase text-purple-400 block tracking-wider">
                  {data.subject_code || 'COURSE'}
                </span>
                <h4 className="font-bold text-sm text-white">{data.subject_name}</h4>
                <div className="text-xs text-gray-400 mt-0.5">
                  <span className="font-bold text-white">{data.attended_classes}</span> / {data.total_classes} classes attended
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-black text-purple-300">{data.current_percentage}%</div>
                <div className="text-[10px] text-gray-400">Target: {data.target_percentage}%</div>
              </div>
            </div>

            {/* Target Criteria Status */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                <div>
                  <div className="text-[10px] text-gray-400 uppercase font-bold">Safe Bunks</div>
                  <div className="text-sm font-black text-emerald-300">
                    {data.classes_safe_to_bunk > 0 ? `${data.classes_safe_to_bunk} classes` : '0 (At target)'}
                  </div>
                </div>
              </div>
              <div className="p-3.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-cyan-400 shrink-0" />
                <div>
                  <div className="text-[10px] text-gray-400 uppercase font-bold">Needed for Target</div>
                  <div className="text-sm font-black text-cyan-300">
                    {data.classes_needed_for_target > 0 ? `${data.classes_needed_for_target} consecutive` : 'Target Achieved'}
                  </div>
                </div>
              </div>
            </div>

            {/* Projections Matrix */}
            <div>
              <div className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-2.5">
                Immediate What-If Scenarios
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                {/* Scenario 1: Next Class */}
                <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
                  <div className="text-[11px] font-bold text-gray-400">Next 1 Class</div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
                      <TrendingUp className="w-3.5 h-3.5" /> If Attend:
                    </span>
                    <span className="font-bold text-white">{data.if_attend_next_1}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1 text-rose-400 text-[11px]">
                      <TrendingDown className="w-3.5 h-3.5" /> If Miss:
                    </span>
                    <span className="font-bold text-white">{data.if_miss_next_1}%</span>
                  </div>
                </div>

                {/* Scenario 2: Next 3 Classes */}
                <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
                  <div className="text-[11px] font-bold text-gray-400">Next 3 Classes</div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
                      <TrendingUp className="w-3.5 h-3.5" /> If Attend:
                    </span>
                    <span className="font-bold text-white">{data.if_attend_next_3}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1 text-rose-400 text-[11px]">
                      <TrendingDown className="w-3.5 h-3.5" /> If Miss:
                    </span>
                    <span className="font-bold text-white">{data.if_miss_next_3}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        <div className="flex justify-end pt-2 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
          >
            Close Projection
          </button>
        </div>
      </div>
    </div>
  );
};
