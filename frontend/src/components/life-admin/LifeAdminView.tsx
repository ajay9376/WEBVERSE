'use client';

import React, { useState, useEffect } from 'react';
import { 
  FolderKanban, FileText, Upload, Clock, AlertTriangle, 
  CheckCircle2, Plus, Sparkles, Tag, Calendar, ShieldAlert 
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { DocumentItem, ReminderItem, DocumentCategory } from '@/types';

export const LifeAdminView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadCategory, setUploadCategory] = useState<string>('OTHER');
  const [uploadTags, setUploadTags] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);

  // New reminder form state
  const [showAddReminder, setShowAddReminder] = useState(false);
  const [remTitle, setRemTitle] = useState('');
  const [remDate, setRemDate] = useState('');

  const loadLifeData = async () => {
    try {
      setLoading(true);
      const [docsData, remsData] = await Promise.all([
        ApiService.getDocuments(),
        ApiService.getReminders(),
      ]);
      setDocuments(docsData || []);
      setReminders(remsData || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLifeData();
  }, []);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('category', uploadCategory);
      formData.append('tags', uploadTags);

      await ApiService.uploadDocument(formData);
      setSelectedFile(null);
      setUploadTags('');
      await loadLifeData();
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!remTitle.trim() || !remDate) return;

    try {
      await ApiService.createReminder({
        title: remTitle,
        due_at: new Date(remDate).toISOString(),
        priority: 'MEDIUM',
      });
      setRemTitle('');
      setRemDate('');
      setShowAddReminder(false);
      await loadLifeData();
    } catch (err: any) {
      alert(`Could not create reminder: ${err.message}`);
    }
  };

  const handleToggleReminder = async (id: string) => {
    try {
      await ApiService.toggleReminder(id);
      await loadLifeData();
    } catch (err: any) {
      alert(`Could not toggle reminder: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Dimension Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
            <FolderKanban className="w-4 h-4" />
            <span>Dimension: Life Admin Vault</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">Life Admin & Vault</h2>
          <p className="text-xs text-gray-400">
            Intelligent document repository with auto-metadata extraction, expiry alerts, and personal reminders.
          </p>
        </div>

        <button
          onClick={() => setShowAddReminder(!showAddReminder)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs shadow-lg shadow-amber-600/30 transition-all cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Set Reminder</span>
        </button>
      </div>

      {/* Add Reminder Modal / Form */}
      {showAddReminder && (
        <form
          onSubmit={handleCreateReminder}
          className="p-5 rounded-2xl glass-panel-glow border border-amber-500/30 space-y-4 animate-in fade-in slide-in-from-top-2"
        >
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-400" />
            <span>Create New Reminder</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Reminder Title (e.g. Pay Hostel Electricity Bill)"
              value={remTitle}
              onChange={(e) => setRemTitle(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-amber-500"
              required
            />
            <input
              type="datetime-local"
              value={remDate}
              onChange={(e) => setRemDate(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-[#0F172A] border border-white/10 text-xs text-white focus:outline-none focus:border-amber-500"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddReminder(false)}
              className="px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold cursor-pointer"
            >
              Save Reminder
            </button>
          </div>
        </form>
      )}

      {/* 1. Document Upload & Auto-Metadata Extraction Zone */}
      <div className="p-6 rounded-2xl glass-panel border border-dashed border-violet-500/30">
        <form onSubmit={handleFileUpload} className="space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-violet-500/10 border border-violet-500/20 text-violet-300">
                <Upload className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Upload Document into Multiverse Vault</h3>
                <p className="text-[11px] text-gray-400">
                  PDFs, certificates, bills, or notes. Auto-extracts policy numbers, providers, and expiry dates.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <input
                type="file"
                id="vault-file-input"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="hidden"
                accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg"
              />
              <label
                htmlFor="vault-file-input"
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-bold transition-all cursor-pointer border border-white/10 text-center w-full sm:w-auto"
              >
                {selectedFile ? selectedFile.name : 'Choose File'}
              </label>

              <button
                type="submit"
                disabled={!selectedFile || isUploading}
                className="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold shadow-lg shadow-violet-600/30 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {isUploading ? 'Extracting & Indexing...' : 'Upload & Process'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* 2. Documents Vault & Reminders */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document Cards */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-violet-400" />
              <span>Document Vault ({documents.length})</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {documents.map((doc) => {
              const meta = doc.metadata_fields || {};
              return (
                <div
                  key={doc.id}
                  className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-violet-500/30 transition-all space-y-2.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-violet-500/10 text-violet-300">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="font-bold text-xs text-white max-w-[170px] truncate">
                          {doc.filename}
                        </h4>
                        <span className="text-[10px] text-gray-400 block">
                          {doc.category} • {doc.file_size} KB
                        </span>
                      </div>
                    </div>

                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                      RAG Indexed
                    </span>
                  </div>

                  {/* Extracted Metadata Fields */}
                  {Object.keys(meta).length > 0 && (
                    <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 space-y-1 text-[11px]">
                      {meta.policy_number && (
                        <div className="flex justify-between text-gray-300">
                          <span className="text-gray-500 text-[10px]">Policy No:</span>
                          <span className="font-mono font-bold text-violet-300">{meta.policy_number}</span>
                        </div>
                      )}
                      {meta.expiry_date && (
                        <div className="flex justify-between text-gray-300">
                          <span className="text-gray-500 text-[10px]">Expiry:</span>
                          <span className="font-bold text-amber-400">{meta.expiry_date}</span>
                        </div>
                      )}
                      {meta.provider && (
                        <div className="flex justify-between text-gray-300">
                          <span className="text-gray-500 text-[10px]">Provider:</span>
                          <span className="font-semibold text-gray-200">{meta.provider}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
            {documents.length === 0 && (
              <p className="text-xs text-gray-500 py-8 col-span-2 text-center">
                No documents uploaded yet. Upload an insurance PDF or certificate to test OCR & RAG.
              </p>
            )}
          </div>
        </div>

        {/* Reminders & Alerts */}
        <div className="p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span>Reminders & Alerts</span>
            </h3>
          </div>

          <div className="space-y-2.5">
            {reminders.map((rem) => (
              <div
                key={rem.id}
                onClick={() => handleToggleReminder(rem.id)}
                className={`p-3 rounded-xl border flex items-start gap-3 transition-all cursor-pointer ${
                  rem.is_completed
                    ? 'bg-white/5 border-white/5 opacity-50'
                    : rem.priority === 'CRITICAL' || rem.is_overdue
                    ? 'bg-rose-950/20 border-rose-500/30'
                    : 'bg-white/5 border-white/10 hover:border-amber-500/30'
                }`}
              >
                <div className="mt-0.5">
                  <CheckCircle2
                    className={`w-4 h-4 ${
                      rem.is_completed ? 'text-emerald-400' : 'text-gray-500 hover:text-white'
                    }`}
                  />
                </div>
                <div className="flex-1">
                  <h4
                    className={`text-xs font-bold ${
                      rem.is_completed ? 'line-through text-gray-400' : 'text-white'
                    }`}
                  >
                    {rem.title}
                  </h4>
                  <div className="flex items-center gap-2 text-[10px] text-gray-400 mt-0.5">
                    <span>{new Date(rem.due_at).toLocaleDateString()}</span>
                    {rem.is_overdue && !rem.is_completed && (
                      <span className="text-rose-400 font-bold uppercase">Overdue</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {reminders.length === 0 && (
              <p className="text-xs text-gray-500 py-6 text-center">No active reminders.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
