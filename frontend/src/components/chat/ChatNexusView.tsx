'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, Send, CornerDownLeft, Loader2, Bot, User as UserIcon, 
  ShieldCheck, ArrowRight, CheckCircle2, MessageSquare, Plus, RefreshCw 
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { ChatMessage, ActionProposal } from '@/types';

export const ChatNexusView: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [actionSuccessMap, setActionSuccessMap] = useState<Record<string, string>>({});
  const [executingActionId, setExecutingActionId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initial welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          session_id: 'initial',
          role: 'assistant',
          content: `Welcome to the **WEBVERSE Universal Intelligence Nexus**.\n\nI connect your **StudentOS (Academics)**, **AI Money Manager (Finance)**, and **Life Admin Vault** into one unified mind. You can ask cross-dimensional questions or give direct commands:\n\n- *"What is my current DAA attendance and how many classes can I miss?"*\n- *"Can I afford to travel this weekend considering my food expenses and bills?"*\n- *"I have exams next week. Make me a study plan."*\n- *"Add ₹250 for lunch to my expenses."*`,
          routed_modules: ['UNIVERSAL'],
          source_references: [],
          created_at: new Date().toISOString(),
        },
      ]);
    }
  }, [messages.length]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      session_id: sessionId || 'temp',
      role: 'user',
      content: text,
      routed_modules: [],
      source_references: [],
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const resp = await ApiService.sendChatMessage({
        message: text,
        session_id: sessionId,
      });

      if (!sessionId && resp.session_id) {
        setSessionId(resp.session_id);
      }

      setMessages((prev) => [...prev, resp]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          session_id: sessionId || 'temp',
          role: 'assistant',
          content: `Error: ${err.message}. Please check backend connection.`,
          routed_modules: [],
          source_references: [],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteAction = async (action: ActionProposal, messageId: string) => {
    setExecutingActionId(messageId);
    try {
      const res = await ApiService.executeAIAction({
        action_type: action.action_type,
        params: action.params,
        message_id: messageId,
      });
      setActionSuccessMap((prev) => ({
        ...prev,
        [messageId]: res.message || 'Action executed successfully!',
      }));
    } catch (err: any) {
      alert(`Execution error: ${err.message}`);
    } finally {
      setExecutingActionId(null);
    }
  };

  const samplePrompts = [
    "What is my current DAA attendance?",
    "How much did I spend on food this month?",
    "When does my insurance expire?",
    "Can I afford to travel this weekend considering my upcoming expenses?",
    "I have exams next week. Make me a study plan.",
    "Add ₹250 for lunch to my expenses",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] rounded-2xl glass-panel border border-white/10 overflow-hidden animate-in fade-in">
      {/* Nexus Header */}
      <div className="p-4 border-b border-white/5 bg-[#090D18]/90 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-white flex items-center gap-2">
              <span>Universal Intelligence Workspace</span>
              <span className="px-2 py-0.5 rounded-full text-[9px] bg-cyan-500/15 text-cyan-300 font-extrabold uppercase">
                Active Reasoning
              </span>
            </h3>
            <p className="text-[11px] text-gray-400">
              Retrieval-augmented cross-module synthesis over your life data.
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            setSessionId(undefined);
            setMessages([]);
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Session</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={msg.id}
              className={`flex gap-3.5 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center text-xs font-bold ${
                  isUser
                    ? 'bg-gradient-to-tr from-violet-600 to-indigo-600 text-white'
                    : 'bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white'
                }`}
              >
                {isUser ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Bubble */}
              <div
                className={`rounded-2xl p-4 text-xs leading-relaxed space-y-3 ${
                  isUser
                    ? 'bg-violet-600/30 border border-violet-500/40 text-white'
                    : 'bg-[#0E1526]/90 border border-white/10 text-gray-200'
                }`}
              >
                {/* Routing tags */}
                {!isUser && msg.routed_modules && msg.routed_modules.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pb-2 border-b border-white/5">
                    {msg.routed_modules.map((mod, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-violet-500/20 text-violet-300 border border-violet-500/30"
                      >
                        {mod}
                      </span>
                    ))}
                  </div>
                )}

                {/* Content */}
                <div className="prose prose-invert prose-xs whitespace-pre-line">
                  {msg.content}
                </div>

                {/* Citations */}
                {!isUser && msg.source_references && msg.source_references.length > 0 && (
                  <div className="pt-2 border-t border-white/5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500 block mb-1.5">
                      Ground Truth Citations:
                    </span>
                    <div className="space-y-1.5">
                      {msg.source_references.map((c, i) => (
                        <div
                          key={i}
                          className="p-2 rounded-lg bg-black/40 border border-white/5 flex items-center gap-2 text-[10px]"
                        >
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                          <span className="font-bold text-gray-300">{c.title}:</span>
                          <span className="text-gray-400">{c.detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action proposal block */}
                {!isUser && msg.action_proposal && (
                  <div className="p-3.5 rounded-xl bg-gradient-to-r from-violet-950/60 to-cyan-950/60 border border-violet-500/30 space-y-2">
                    <div className="flex items-center gap-2 text-violet-300 font-bold text-[11px]">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{msg.action_proposal.summary_text}</span>
                    </div>

                    {actionSuccessMap[msg.id] ? (
                      <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[11px] px-2.5 py-1 bg-emerald-500/10 rounded-lg">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{actionSuccessMap[msg.id]}</span>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleExecuteAction(msg.action_proposal!, msg.id)}
                        disabled={executingActionId === msg.id}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] transition-all cursor-pointer disabled:opacity-50"
                      >
                        {executingActionId === msg.id ? (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                          <>
                            <span>Execute Action</span>
                            <ArrowRight className="w-3 h-3" />
                          </>
                        )}
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex gap-3.5 max-w-3xl">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white flex items-center justify-center">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl bg-[#0E1526] border border-white/10 flex items-center gap-2 text-xs text-gray-400">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
              <span>Synthesizing cross-module knowledge...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested chips & input */}
      <div className="p-4 border-t border-white/5 bg-[#090D18]/90 space-y-3">
        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(p)}
              className="shrink-0 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-[10px] text-gray-300 transition-all cursor-pointer border border-white/5"
            >
              {p}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your question or life command..."
            className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 font-medium"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="p-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white transition-all shadow-lg shadow-cyan-600/30 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
