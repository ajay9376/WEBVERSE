'use client';

import React, { useState } from 'react';
import { Sparkles, Send, CornerDownLeft, Loader2, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';
import { ApiService } from '@/lib/api';
import { ChatMessage, ActionProposal } from '@/types';

interface OmnibarProps {
  onActionResult?: () => void;
}

export const Omnibar: React.FC<OmnibarProps> = ({ onActionResult }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState<ChatMessage | null>(null);
  const [isExecutingAction, setIsExecutingAction] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const suggestedQueries = [
    "What is my current DAA attendance?",
    "How much did I spend on food this month?",
    "When does my insurance expire?",
    "Can I afford to spend ₹5,000 this month?",
    "I have exams next week. Make me a study plan.",
    "Add ₹350 for campus lunch to expenses",
  ];

  const handleSend = async (textToSend?: string) => {
    const prompt = textToSend || query;
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setActionSuccess(null);
    setResponseMessage(null);

    try {
      const resp = await ApiService.sendChatMessage({ message: prompt });
      setResponseMessage(resp);
      setQuery('');
    } catch (err: any) {
      console.error(err);
      setResponseMessage({
        id: 'err',
        session_id: 'err',
        role: 'assistant',
        content: `Connection error: ${err.message}. Ensure the backend is running.`,
        routed_modules: [],
        source_references: [],
        created_at: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExecuteAction = async (action: ActionProposal, messageId: string) => {
    setIsExecutingAction(true);
    try {
      const res = await ApiService.executeAIAction({
        action_type: action.action_type,
        params: action.params,
        message_id: messageId,
      });
      setActionSuccess(res.message || 'Action executed successfully!');
      if (onActionResult) {
        onActionResult();
      }
    } catch (err: any) {
      alert(`Action execution failed: ${err.message}`);
    } finally {
      setIsExecutingAction(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-6 px-4">
      {/* Omnibar Input Card */}
      <div className="relative rounded-2xl bg-gradient-to-b from-white/10 to-white/5 p-[1.5px] shadow-2xl shadow-violet-950/40">
        <div className="bg-[#0A0E1A]/95 rounded-[15px] p-3 backdrop-blur-2xl">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-3"
          >
            <div className="p-2.5 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-300">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask WEBVERSE anything... (e.g. 'DAA attendance', 'Food budget', 'Insurance expiry', 'Make study plan')"
              className="w-full bg-transparent text-sm text-white placeholder-gray-400 focus:outline-none font-medium"
              disabled={isLoading}
            />

            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs transition-all shadow-lg shadow-violet-600/30 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="hidden sm:inline">Synthesizing...</span>
                </>
              ) : (
                <>
                  <span>Ask AI</span>
                  <CornerDownLeft className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Suggested Quick Prompts */}
          <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 shrink-0">
              Try asking:
            </span>
            {suggestedQueries.map((suggestion, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(suggestion);
                  handleSend(suggestion);
                }}
                className="shrink-0 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-violet-500/15 hover:border-violet-500/30 border border-white/5 text-[11px] text-gray-300 transition-all cursor-pointer"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Live AI Synthesis Result Drawer */}
      {responseMessage && (
        <div className="mt-4 rounded-2xl glass-panel-glow p-5 transition-all animate-in fade-in slide-in-from-top-2">
          {/* Header & Routing Badges */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                WEBVERSE Intelligence Synthesis
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              {responseMessage.routed_modules?.map((mod, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-violet-500/20 text-violet-300 border border-violet-500/30"
                >
                  {mod}
                </span>
              ))}
            </div>
          </div>

          {/* Formatted Content */}
          <div className="prose prose-invert prose-sm max-w-none text-gray-200 text-xs leading-relaxed whitespace-pre-line">
            {responseMessage.content}
          </div>

          {/* Sources / Citations */}
          {responseMessage.source_references && responseMessage.source_references.length > 0 && (
            <div className="mt-4 pt-3 border-t border-white/5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-2">
                Ground Truth Verified Sources:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {responseMessage.source_references.map((src, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-white/5 border border-white/10 flex items-start gap-2.5 text-[11px]"
                  >
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-gray-200">{src.title}</div>
                      <div className="text-gray-400 text-[10px]">{src.detail}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Action Proposal Card (Verified Action Execution) */}
          {responseMessage.action_proposal && (
            <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-violet-950/50 via-indigo-950/40 to-cyan-950/50 border border-violet-500/30">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-violet-500/20 text-violet-300">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase tracking-wider font-bold text-violet-300 block">
                      AI Action Proposal
                    </span>
                    <span className="text-xs font-semibold text-white">
                      {responseMessage.action_proposal.summary_text}
                    </span>
                  </div>
                </div>

                {actionSuccess ? (
                  <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-bold px-3 py-1.5 bg-emerald-500/10 rounded-lg border border-emerald-500/30">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{actionSuccess}</span>
                  </div>
                ) : (
                  <button
                    onClick={() =>
                      handleExecuteAction(responseMessage.action_proposal!, responseMessage.id)
                    }
                    disabled={isExecutingAction}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all shadow-lg shadow-emerald-600/30 cursor-pointer disabled:opacity-50"
                  >
                    {isExecutingAction ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <>
                        <span>Confirm & Execute</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
