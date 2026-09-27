'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, Send, Loader2, Bot, User as UserIcon, 
  ShieldCheck, ArrowRight, CheckCircle2, Plus, 
  Brain, AlertTriangle, BookOpen, Wallet, FileText, Globe,
  MessageSquare, Trash2, History, ChevronLeft, ChevronRight
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { ChatMessage, ActionProposal, ConversationBrief } from '@/types';

// Per-module styling config
const MODULE_STYLE: Record<string, { bg: string; text: string; border: string; icon: React.ReactNode }> = {
  ACADEMICS: {
    bg: 'bg-indigo-500/15',
    text: 'text-indigo-300',
    border: 'border-indigo-500/30',
    icon: <BookOpen className="w-3 h-3" />,
  },
  FINANCE: {
    bg: 'bg-emerald-500/15',
    text: 'text-emerald-300',
    border: 'border-emerald-500/30',
    icon: <Wallet className="w-3 h-3" />,
  },
  LIFE_ADMIN: {
    bg: 'bg-amber-500/15',
    text: 'text-amber-300',
    border: 'border-amber-500/30',
    icon: <FileText className="w-3 h-3" />,
  },
  UNIVERSAL: {
    bg: 'bg-cyan-500/15',
    text: 'text-cyan-300',
    border: 'border-cyan-500/30',
    icon: <Globe className="w-3 h-3" />,
  },
};

const HEALTH_BADGE: Record<string, { label: string; color: string }> = {
  EXCELLENT:       { label: '✦ Excellent', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
  GOOD:            { label: '● Good',      color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30' },
  NEEDS_ATTENTION: { label: '▲ Attention', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
  CRITICAL:        { label: '⚠ Critical',  color: 'text-red-400 bg-red-500/10 border-red-500/30' },
};

function renderContent(text: string): React.ReactNode {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`|\n)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="text-white font-bold">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className="px-1.5 py-0.5 rounded bg-black/40 text-cyan-300 font-mono text-[10px] border border-white/5">{part.slice(1, -1)}</code>;
    }
    if (part === '\n') return <br key={i} />;
    return <span key={i}>{part}</span>;
  });
}

interface ChatNexusViewProps {
  initialPrompt?: string;
}

export const ChatNexusView: React.FC<ChatNexusViewProps> = ({ initialPrompt }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState(initialPrompt || '');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [actionSuccessMap, setActionSuccessMap] = useState<Record<string, string>>({});
  const [executingActionId, setExecutingActionId] = useState<string | null>(null);
  const [lifeScore, setLifeScore] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationBrief[]>([]);
  const [showHistory, setShowHistory] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load conversation history on mount
  const loadConversations = async () => {
    try {
      setHistoryLoading(true);
      const list = await ApiService.getConversations();
      setConversations(list);
    } catch (e) {
      console.error("Failed to load conversations:", e);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  // Initial welcome message if no session active
  useEffect(() => {
    if (!sessionId && messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          session_id: 'initial',
          role: 'assistant',
          content: `Welcome to the **WEBVERSE Universal Intelligence Nexus**.\n\nI connect your **StudentOS (Academics)**, **AI Money Manager (Finance)**, and **Life Admin Vault** into one unified cross-module mind.\n\nTry asking cross-dimensional questions:\n\n- *"What is my current DAA attendance and how many classes can I miss?"*\n- *"Can I afford to travel this weekend considering my food expenses and bills?"*\n- *"I have exams next week. Make me a study plan."*\n- *"Add ₹250 for lunch to my expenses."*\n- *"Give me a holistic life health report."*`,
          routed_modules: ['UNIVERSAL'],
          source_references: [],
          created_at: new Date().toISOString(),
        },
      ]);
    }
  }, [sessionId, messages.length]);

  // Handle switching to an existing conversation
  const handleSelectConversation = async (convId: string) => {
    if (loading) return;
    try {
      setLoading(true);
      setSessionId(convId);
      const detail = await ApiService.getConversation(convId);
      if (detail && detail.messages) {
        setMessages(detail.messages);
      }
    } catch (e) {
      console.error("Failed to load session:", e);
    } finally {
      setLoading(false);
    }
  };

  // Handle starting a fresh conversation
  const handleNewSession = () => {
    setSessionId(undefined);
    setMessages([]);
    setLifeScore(null);
    setInputMessage('');
  };

  // Handle deleting a conversation
  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await ApiService.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (sessionId === convId) {
        handleNewSession();
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

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
        // Refresh conversations list in background
        loadConversations();
      }

      // Extract life score from cross_module context if available
      if ((resp as any).cross_module?.intelligence_overlay?.life_health_score) {
        setLifeScore((resp as any).cross_module.intelligence_overlay.life_health_score);
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
    "What is my current attendance status?",
    "How much have I spent this month?",
    "When does my insurance expire?",
    "Can I afford to travel this weekend?",
    "Give me a holistic life health report",
    "Add ₹250 for lunch",
    "Mark DAA attendance as present today",
  ];

  const healthBadge = lifeScore ? HEALTH_BADGE[lifeScore] : null;

  return (
    <div className="flex h-[calc(100vh-140px)] rounded-3xl glass-panel border border-white/10 overflow-hidden shadow-2xl relative">
      {/* Sessions Sidebar (Collapsible) */}
      <AnimatePresence initial={false}>
        {showHistory && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="border-r border-white/5 bg-[#07090F]/95 flex flex-col justify-between shrink-0 overflow-hidden z-20"
          >
            <div className="p-3 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-gray-300">
                <History className="w-3.5 h-3.5 text-cyan-400" />
                <span>Chat History</span>
              </div>
              <button
                onClick={handleNewSession}
                className="p-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 transition-all cursor-pointer"
                title="New Session"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
              {historyLoading ? (
                <div className="p-4 text-center text-gray-500 text-xs flex items-center justify-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  <span>Loading history...</span>
                </div>
              ) : conversations.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-xs leading-relaxed">
                  No saved conversations yet. Start a new thread!
                </div>
              ) : (
                conversations.map((c) => {
                  const isActive = c.id === sessionId;
                  return (
                    <motion.div
                      key={c.id}
                      whileHover={{ x: 2 }}
                      onClick={() => handleSelectConversation(c.id)}
                      className={`group flex items-center justify-between p-2.5 rounded-xl text-xs font-medium cursor-pointer transition-all border ${
                        isActive
                          ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-200 shadow-md shadow-cyan-500/5'
                          : 'bg-white/[0.02] border-white/5 text-gray-400 hover:text-gray-200 hover:bg-white/5'
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-cyan-400' : 'text-gray-500'}`} />
                        <span className="truncate">{c.title || 'Untitled Thread'}</span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400">
                          {c.message_count}
                        </span>
                        <button
                          onClick={(e) => handleDeleteConversation(c.id, e)}
                          className="p-1 rounded hover:bg-rose-500/20 text-gray-500 hover:text-rose-400 transition-all cursor-pointer"
                          title="Delete thread"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>

            <div className="p-3 border-t border-white/5 text-[10px] text-gray-500 flex items-center justify-between">
              <span>Universal RAG</span>
              <span className="text-cyan-400 font-mono">Ready</span>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#06080E]/70">
        {/* Nexus Header */}
        <div className="p-3.5 sm:p-4 border-b border-white/5 bg-[#090D18]/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowHistory((prev) => !prev)}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all cursor-pointer"
              title={showHistory ? 'Collapse History' : 'Expand History'}
            >
              {showHistory ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
              <Sparkles className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <h3 className="font-bold text-xs sm:text-sm text-white flex items-center gap-2">
                <span>Universal Intelligence Nexus</span>
                <span className="px-2 py-0.5 rounded-full text-[9px] bg-cyan-500/15 text-cyan-300 font-extrabold uppercase hidden sm:inline">
                  RAG Synthesis
                </span>
              </h3>
              <p className="text-[10px] sm:text-[11px] text-gray-400 truncate">
                Cross-module AI · Academics + Finance + Life Admin
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {healthBadge && (
              <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold ${healthBadge.color} hidden sm:inline`}>
                Life: {healthBadge.label}
              </span>
            )}
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={handleNewSession}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold transition-all cursor-pointer border border-white/5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Session</span>
            </motion.button>
          </div>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          <AnimatePresence initial={false}>
            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.2 }}
                  className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}
                >
                  {/* Avatar */}
                  <div
                    className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center text-xs font-bold shadow-md ${
                      isUser
                        ? 'bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-violet-600/20'
                        : 'bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-cyan-600/20'
                    }`}
                  >
                    {isUser ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  {/* Bubble */}
                  <div
                    className={`rounded-2xl p-4 text-xs leading-relaxed space-y-3 shadow-xl ${
                      isUser
                        ? 'bg-violet-600/30 border border-violet-500/40 text-white'
                        : 'bg-[#0E1526]/90 border border-white/10 text-gray-200'
                    }`}
                    style={{ minWidth: 140, maxWidth: '90%' }}
                  >
                    {/* Routing module badges */}
                    {!isUser && msg.routed_modules && msg.routed_modules.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pb-2 border-b border-white/5">
                        {msg.routed_modules.map((mod, i) => {
                          const style = MODULE_STYLE[mod] || MODULE_STYLE['UNIVERSAL'];
                          return (
                            <span
                              key={i}
                              className={`px-2 py-0.5 rounded border text-[9px] font-bold uppercase tracking-wider flex items-center gap-1 ${style.bg} ${style.text} ${style.border}`}
                            >
                              {style.icon}
                              {mod}
                            </span>
                          );
                        })}
                        {msg.routed_modules.length >= 2 && (
                          <span className="px-2 py-0.5 rounded border text-[9px] font-bold uppercase tracking-wider bg-purple-500/15 text-purple-300 border-purple-500/30 flex items-center gap-1">
                            <Brain className="w-3 h-3" />
                            CROSS-MODULE
                          </span>
                        )}
                      </div>
                    )}

                    {/* Content */}
                    <div className="text-xs leading-relaxed text-gray-200">
                      {renderContent(msg.content)}
                    </div>

                    {/* Citations */}
                    {!isUser && msg.source_references && msg.source_references.length > 0 && (
                      <div className="pt-2 border-t border-white/5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500 block mb-1.5">
                          Ground Truth Sources:
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

                    {/* Action Proposal card */}
                    {!isUser && msg.action_proposal && (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="p-3.5 rounded-xl bg-gradient-to-r from-violet-950/60 to-cyan-950/60 border border-violet-500/30 space-y-2.5"
                      >
                        <div className="flex items-center gap-2">
                          <Sparkles className="w-3.5 h-3.5 text-violet-300" />
                          <span className="text-violet-300 font-bold text-[11px]">
                            {msg.action_proposal.summary_text}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-black/30 text-gray-300 border border-white/10">
                            {msg.action_proposal.action_type}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-black/30 text-gray-300 border border-white/10">
                            {msg.action_proposal.module}
                          </span>
                        </div>

                        {actionSuccessMap[msg.id] ? (
                          <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[11px] px-2.5 py-1 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>{actionSuccessMap[msg.id]}</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2">
                            <motion.button
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                              onClick={() => handleExecuteAction(msg.action_proposal!, msg.id)}
                              disabled={executingActionId === msg.id}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] transition-all cursor-pointer disabled:opacity-50 shadow-md shadow-emerald-600/20"
                            >
                              {executingActionId === msg.id ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                              ) : (
                                <>
                                  <span>Confirm & Execute</span>
                                  <ArrowRight className="w-3 h-3" />
                                </>
                              )}
                            </motion.button>
                            <span className="text-[10px] text-gray-500 italic">
                              Safe verification required
                            </span>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>

          {loading && (
            <motion.div 
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 max-w-3xl"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white flex items-center justify-center">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-2xl bg-[#0E1526] border border-white/10 flex items-center gap-3 text-xs text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                <div>
                  <span className="text-white font-semibold block">Synthesizing Multiverse Context...</span>
                  <span className="text-gray-500">Retrieving cross-module state & generating response</span>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested chips & input form */}
        <div className="p-3.5 sm:p-4 border-t border-white/5 bg-[#090D18]/90 space-y-3">
          <div className="flex items-center gap-2 overflow-x-auto pb-1" style={{ scrollbarWidth: 'none' }}>
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
              placeholder="Ask anything or propose a life action (e.g. 'Add ₹350 for dinner')..."
              className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 font-medium"
              disabled={loading}
            />
            <motion.button
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="p-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white transition-all shadow-lg shadow-cyan-600/30 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </motion.button>
          </form>
        </div>
      </div>
    </div>
  );
};
