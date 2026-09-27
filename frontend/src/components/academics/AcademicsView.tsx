'use client';

import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, Calendar, CheckSquare, Clock, Plus, 
  CheckCircle2, XCircle, AlertCircle, BookOpen, Calculator,
  FileText, Award, FolderGit2, Trash2, Edit3, User, Sparkles,
  ExternalLink, Layers, ArrowUpRight, Check, RefreshCw
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { 
  SubjectItem, AssignmentItem, ExamItem, TimetableSlotItem,
  InternalMarkItem, AcademicProjectItem, AcademicNoteItem,
  AcademicProfile, AcademicDashboardData
} from '@/types';
import { AttendanceProjectionModal } from './AttendanceProjectionModal';

type AcademicTab = 'overview' | 'subjects' | 'timetable' | 'assignments' | 'exams_marks' | 'projects_notes';

export const AcademicsView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AcademicTab>('overview');
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<AcademicDashboardData | null>(null);

  // Entities state
  const [profile, setProfile] = useState<AcademicProfile | null>(null);
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [timetable, setTimetable] = useState<TimetableSlotItem[]>([]);
  const [assignments, setAssignments] = useState<AssignmentItem[]>([]);
  const [exams, setExams] = useState<ExamItem[]>([]);
  const [marks, setMarks] = useState<InternalMarkItem[]>([]);
  const [projects, setProjects] = useState<AcademicProjectItem[]>([]);
  const [notes, setNotes] = useState<AcademicNoteItem[]>([]);

  // Modals state
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showSubjectModal, setShowSubjectModal] = useState(false);
  const [showAttendanceModal, setShowAttendanceModal] = useState(false);
  const [showTimetableModal, setShowTimetableModal] = useState(false);
  const [showAssignmentModal, setShowAssignmentModal] = useState(false);
  const [showExamModal, setShowExamModal] = useState(false);
  const [showMarkModal, setShowMarkModal] = useState(false);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [projectionSubjectId, setProjectionSubjectId] = useState<string | null>(null);

  // Form states
  const [profileForm, setProfileForm] = useState({
    college_name: '',
    university: '',
    degree: '',
    branch: '',
    current_year: 3,
    current_semester: 6,
    roll_number: '',
    academic_start_year: 2023,
  });

  const [subjectForm, setSubjectForm] = useState({
    name: '',
    code: '',
    credits: 3,
    semester: 6,
    faculty_name: '',
    color: '#8B5CF6',
    total_classes: 0,
    attended_classes: 0,
    target_attendance: 80.0,
    min_attendance: 75.0,
  });

  const [attendanceForm, setAttendanceForm] = useState({
    subject_id: '',
    date: new Date().toISOString().split('T')[0],
    status: 'PRESENT',
    remarks: '',
  });

  const [timetableForm, setTimetableForm] = useState({
    subject_id: '',
    day_of_week: 0,
    start_time: '09:00',
    end_time: '10:00',
    room: 'Room 101',
    faculty_name: '',
  });

  const [assignmentForm, setAssignmentForm] = useState({
    subject_id: '',
    title: '',
    description: '',
    due_date: new Date(Date.now() + 86400000 * 3).toISOString().slice(0, 16),
    priority: 'MEDIUM' as 'LOW' | 'MEDIUM' | 'HIGH',
    total_marks: 20,
  });

  const [examForm, setExamForm] = useState({
    subject_id: '',
    title: '',
    exam_type: 'MIDTERM' as any,
    exam_date: new Date(Date.now() + 86400000 * 7).toISOString().slice(0, 16),
    start_time: '10:00',
    end_time: '13:00',
    venue: 'Hall A',
    syllabus_covered: '',
    max_marks: 100,
  });

  const [markForm, setMarkForm] = useState({
    subject_id: '',
    assessment_name: '',
    assessment_type: 'QUIZ' as any,
    marks_obtained: 18,
    max_marks: 20,
    assessment_date: new Date().toISOString().split('T')[0],
    remarks: '',
  });

  const [projectForm, setProjectForm] = useState({
    subject_id: '',
    title: '',
    description: '',
    status: 'IN_PROGRESS' as any,
    deadline: new Date(Date.now() + 86400000 * 14).toISOString().slice(0, 16),
    repository_url: '',
    documentation_url: '',
  });

  const [noteForm, setNoteForm] = useState({
    subject_id: '',
    title: '',
    description: '',
    tags: '',
  });

  const loadAllAcademicData = async () => {
    try {
      setLoading(true);
      const [
        dashData,
        profData,
        subsData,
        ttData,
        asgnsData,
        examsData,
        marksData,
        projsData,
        notesData
      ] = await Promise.all([
        ApiService.getAcademicDashboard().catch(() => null),
        ApiService.getAcademicProfile().catch(() => null),
        ApiService.getSubjects(),
        ApiService.getTimetable(),
        ApiService.getAssignments(),
        ApiService.getExams(),
        ApiService.getInternalMarks(),
        ApiService.getProjects(),
        ApiService.getNotes(),
      ]);

      setDashboardData(dashData);
      setProfile(profData);
      if (profData) {
        setProfileForm({
          college_name: profData.college_name || '',
          university: profData.university || '',
          degree: profData.degree || '',
          branch: profData.branch || '',
          current_year: profData.current_year || 3,
          current_semester: profData.current_semester || 6,
          roll_number: profData.roll_number || '',
          academic_start_year: profData.academic_start_year || 2023,
        });
      }
      setSubjects(subsData || []);
      setTimetable(ttData || []);
      setAssignments(asgnsData || []);
      setExams(examsData || []);
      setMarks(marksData || []);
      setProjects(projsData || []);
      setNotes(notesData || []);

      if (subsData && subsData.length > 0) {
        const defaultSubId = subsData[0].id;
        setAttendanceForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
        setTimetableForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
        setAssignmentForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
        setExamForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
        setMarkForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
        setProjectForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
        setNoteForm(prev => ({ ...prev, subject_id: prev.subject_id || defaultSubId }));
      }
    } catch (e) {
      console.error('Error loading academic data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllAcademicData();
  }, []);

  // Handlers
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiService.updateAcademicProfile(profileForm);
      setShowProfileModal(false);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Could not save profile: ${err.message}`);
    }
  };

  const handleCreateSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectForm.name.trim()) return;
    try {
      await ApiService.createSubject(subjectForm);
      setShowSubjectModal(false);
      setSubjectForm({
        name: '',
        code: '',
        credits: 3,
        semester: 6,
        faculty_name: '',
        color: '#8B5CF6',
        total_classes: 0,
        attended_classes: 0,
        target_attendance: 80.0,
        min_attendance: 75.0,
      });
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Could not create subject: ${err.message}`);
    }
  };

  const handleDeleteSubject = async (id: string) => {
    if (!confirm('Are you sure you want to delete this subject? All linked attendance, assignments, and timetable slots will be removed.')) return;
    try {
      await ApiService.deleteSubject(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting subject: ${err.message}`);
    }
  };

  const handleLogAttendance = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!attendanceForm.subject_id) return;
    try {
      await ApiService.markAttendance(attendanceForm);
      setShowAttendanceModal(false);
      setAttendanceForm(prev => ({ ...prev, remarks: '' }));
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error logging attendance: ${err.message}`);
    }
  };

  const handleQuickMarkAttendance = async (subjectId: string, status: 'PRESENT' | 'ABSENT' | 'DUTY') => {
    try {
      await ApiService.markAttendance({
        subject_id: subjectId,
        date: new Date().toISOString().split('T')[0],
        status,
      });
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Could not log attendance: ${err.message}`);
    }
  };

  const handleCreateTimetableSlot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!timetableForm.subject_id) return;
    try {
      await ApiService.createTimetableSlot(timetableForm);
      setShowTimetableModal(false);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error creating timetable slot: ${err.message}`);
    }
  };

  const handleDeleteTimetableSlot = async (id: string) => {
    try {
      await ApiService.deleteTimetableSlot(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting slot: ${err.message}`);
    }
  };

  const handleCreateAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignmentForm.title.trim() || !assignmentForm.subject_id) return;
    try {
      await ApiService.createAssignment({
        ...assignmentForm,
        due_date: new Date(assignmentForm.due_date).toISOString(),
      });
      setShowAssignmentModal(false);
      setAssignmentForm(prev => ({ ...prev, title: '', description: '' }));
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error creating assignment: ${err.message}`);
    }
  };

  const handleToggleAssignmentStatus = async (asgn: AssignmentItem) => {
    const nextStatus = asgn.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
    try {
      await ApiService.updateAssignment(asgn.id, { status: nextStatus as any });
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error updating assignment: ${err.message}`);
    }
  };

  const handleDeleteAssignment = async (id: string) => {
    try {
      await ApiService.deleteAssignment(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting assignment: ${err.message}`);
    }
  };

  const handleCreateExam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!examForm.title.trim() || !examForm.subject_id) return;
    try {
      await ApiService.createExam({
        ...examForm,
        exam_date: new Date(examForm.exam_date).toISOString(),
      });
      setShowExamModal(false);
      setExamForm(prev => ({ ...prev, title: '', syllabus_covered: '' }));
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error creating exam: ${err.message}`);
    }
  };

  const handleDeleteExam = async (id: string) => {
    try {
      await ApiService.deleteExam(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting exam: ${err.message}`);
    }
  };

  const handleCreateMark = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!markForm.assessment_name.trim() || !markForm.subject_id) return;
    try {
      await ApiService.createInternalMark(markForm);
      setShowMarkModal(false);
      setMarkForm(prev => ({ ...prev, assessment_name: '', remarks: '' }));
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error logging marks: ${err.message}`);
    }
  };

  const handleDeleteMark = async (id: string) => {
    try {
      await ApiService.deleteInternalMark(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting mark: ${err.message}`);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectForm.title.trim()) return;
    try {
      await ApiService.createProject({
        ...projectForm,
        deadline: projectForm.deadline ? new Date(projectForm.deadline).toISOString() : undefined,
      });
      setShowProjectModal(false);
      setProjectForm(prev => ({ ...prev, title: '', description: '', repository_url: '', documentation_url: '' }));
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error creating project: ${err.message}`);
    }
  };

  const handleDeleteProject = async (id: string) => {
    try {
      await ApiService.deleteProject(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting project: ${err.message}`);
    }
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteForm.title.trim() || !noteForm.subject_id) return;
    try {
      await ApiService.createNote(noteForm);
      setShowNoteModal(false);
      setNoteForm(prev => ({ ...prev, title: '', description: '', tags: '' }));
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error saving note: ${err.message}`);
    }
  };

  const handleDeleteNote = async (id: string) => {
    try {
      await ApiService.deleteNote(id);
      await loadAllAcademicData();
    } catch (err: any) {
      alert(`Error deleting note: ${err.message}`);
    }
  };

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const overallAttendance = dashboardData?.attendance?.overall_percentage ?? 100.0;
  const totalClassesHeld = dashboardData?.attendance?.total_classes ?? 0;
  const totalClassesAttended = dashboardData?.attendance?.attended_classes ?? 0;
  const belowTargetCount = dashboardData?.attendance?.below_target_count ?? 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Dimension Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-6 rounded-3xl glass-panel-glow border border-purple-500/20">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase tracking-wider">
            <GraduationCap className="w-4 h-4" />
            <span>Dimension 01 • StudentOS Academic Matrix</span>
          </div>
          <h2 className="text-3xl font-black text-white tracking-tight">Academic Intelligence</h2>
          <p className="text-xs text-gray-400 max-w-xl">
            Deterministic attendance telemetry, timetable matrices, exam preparedness, internal marks, and study records.
          </p>
        </div>

        {/* Quick Student Badge */}
        <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-2.5 rounded-2xl">
          <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/30">
            <User className="w-5 h-5" />
          </div>
          <div className="pr-2">
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>{profile?.degree || 'Degree'} • Sem {profile?.current_semester || '6'}</span>
              <button
                onClick={() => setShowProfileModal(true)}
                className="text-[10px] text-purple-400 hover:text-purple-300 underline cursor-pointer"
              >
                Edit
              </button>
            </div>
            <div className="text-[10px] text-gray-400">
              {profile?.college_name || 'College not configured'}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none border-b border-white/10">
        {[
          { id: 'overview', label: 'Overview & Matrix', icon: Layers },
          { id: 'subjects', label: `Subjects (${subjects.length})`, icon: BookOpen },
          { id: 'timetable', label: `Timetable (${timetable.length})`, icon: Calendar },
          { id: 'assignments', label: `Assignments (${assignments.filter(a => a.status !== 'COMPLETED').length})`, icon: CheckSquare },
          { id: 'exams_marks', label: `Exams & Marks (${exams.length + marks.length})`, icon: Award },
          { id: 'projects_notes', label: `Projects & Notes (${projects.length + notes.length})`, icon: FolderGit2 },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as AcademicTab)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30 border border-purple-400/30'
                  : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 border border-transparent'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Global Quick Actions Bar */}
      <div className="flex flex-wrap items-center gap-2.5 p-3 rounded-2xl bg-white/5 border border-white/10">
        <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider pl-2">Quick Actions:</span>
        <button
          onClick={() => setShowSubjectModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-bold transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Subject</span>
        </button>
        <button
          onClick={() => setShowAttendanceModal(true)}
          disabled={subjects.length === 0}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-bold transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Mark Attendance</span>
        </button>
        <button
          onClick={() => setShowAssignmentModal(true)}
          disabled={subjects.length === 0}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-bold transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <CheckSquare className="w-3.5 h-3.5" />
          <span>Add Assignment</span>
        </button>
        <button
          onClick={() => setShowExamModal(true)}
          disabled={subjects.length === 0}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 text-xs font-bold transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Clock className="w-3.5 h-3.5" />
          <span>Add Exam</span>
        </button>
        <button
          onClick={() => setShowMarkModal(true)}
          disabled={subjects.length === 0}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-bold transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Award className="w-3.5 h-3.5" />
          <span>Log Mark</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: OVERVIEW & MATRIX */}
      {/* ========================================================================= */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Overall Attendance */}
            <div className="p-5 rounded-2xl glass-panel border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Overall Attendance</span>
                <GraduationCap className="w-4 h-4 text-purple-400" />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-white">{overallAttendance}%</span>
                <span className="text-xs text-gray-400">({totalClassesAttended}/{totalClassesHeld} held)</span>
              </div>
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${
                    overallAttendance >= 80 ? 'bg-emerald-500' : overallAttendance >= 75 ? 'bg-yellow-500' : 'bg-rose-500'
                  }`}
                  style={{ width: `${Math.min(100, overallAttendance)}%` }}
                />
              </div>
            </div>

            {/* Subjects Status */}
            <div className="p-5 rounded-2xl glass-panel border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Enrolled Subjects</span>
                <BookOpen className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-3xl font-black text-white">{subjects.length}</div>
              <div className="text-xs text-gray-400">
                {belowTargetCount > 0 ? (
                  <span className="text-amber-400 font-bold">{belowTargetCount} subject(s) below target</span>
                ) : (
                  <span className="text-emerald-400 font-bold">All subjects meeting target</span>
                )}
              </div>
            </div>

            {/* Pending Assignments */}
            <div className="p-5 rounded-2xl glass-panel border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Pending Assignments</span>
                <CheckSquare className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-3xl font-black text-white">
                {assignments.filter(a => a.status !== 'COMPLETED').length}
              </div>
              <div className="text-xs text-gray-400">Active submission tasks</div>
            </div>

            {/* Upcoming Exams */}
            <div className="p-5 rounded-2xl glass-panel border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Scheduled Exams</span>
                <Clock className="w-4 h-4 text-rose-400" />
              </div>
              <div className="text-3xl font-black text-white">{exams.length}</div>
              <div className="text-xs text-gray-400">Assessments on schedule</div>
            </div>
          </div>

          {/* Quick Glances: Subjects + Timetable Today */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Subject Attendance Matrix Glance */}
            <div className="lg:col-span-2 p-5 rounded-3xl glass-panel space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400" />
                  <span>Subject Attendance Telemetry</span>
                </h3>
                <button
                  onClick={() => setActiveTab('subjects')}
                  className="text-xs text-purple-400 hover:text-purple-300 font-bold flex items-center gap-1 cursor-pointer"
                >
                  <span>View All</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {subjects.length === 0 ? (
                <div className="py-10 text-center space-y-3">
                  <BookOpen className="w-8 h-8 text-gray-600 mx-auto" />
                  <p className="text-xs text-gray-400">No subjects registered yet.</p>
                  <button
                    onClick={() => setShowSubjectModal(true)}
                    className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold cursor-pointer"
                  >
                    Add Your First Subject
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {subjects.slice(0, 4).map((sub) => (
                    <div key={sub.id} className="p-3.5 rounded-2xl bg-white/5 border border-white/10 space-y-2.5">
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-[10px] font-bold text-gray-400 uppercase block">{sub.code || 'COURSE'}</span>
                          <h4 className="font-bold text-xs text-white truncate max-w-[160px]">{sub.name}</h4>
                        </div>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${
                          sub.status_indicator === 'SAFE' ? 'bg-emerald-500/20 text-emerald-300' :
                          sub.status_indicator === 'ON_TRACK' ? 'bg-yellow-500/20 text-yellow-300' :
                          'bg-rose-500/20 text-rose-300'
                        }`}>
                          {sub.current_percentage}%
                        </span>
                      </div>
                      <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            sub.status_indicator === 'SAFE' ? 'bg-emerald-500' :
                            sub.status_indicator === 'ON_TRACK' ? 'bg-yellow-500' : 'bg-rose-500'
                          }`}
                          style={{ width: `${Math.min(100, sub.current_percentage)}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-gray-400">
                        <span>{sub.attended_classes}/{sub.total_classes} classes</span>
                        <button
                          onClick={() => setProjectionSubjectId(sub.id)}
                          className="text-purple-400 hover:text-purple-300 font-bold flex items-center gap-1 cursor-pointer"
                        >
                          <Calculator className="w-3 h-3" />
                          <span>Simulate</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Upcoming Deadlines Glance */}
            <div className="p-5 rounded-3xl glass-panel space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-400" />
                  <span>Upcoming Deadlines</span>
                </h3>
                <button
                  onClick={() => setActiveTab('assignments')}
                  className="text-xs text-purple-400 hover:text-purple-300 font-bold flex items-center gap-1 cursor-pointer"
                >
                  <span>View All</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {assignments.length === 0 ? (
                <div className="py-10 text-center text-xs text-gray-500">
                  No upcoming deadlines on schedule.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {assignments.slice(0, 3).map((asgn) => (
                    <div key={asgn.id} className="p-3 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between">
                      <div>
                        <div className="text-[10px] text-purple-400 font-bold uppercase">{asgn.subject_name}</div>
                        <div className="text-xs font-bold text-white">{asgn.title}</div>
                        <div className="text-[10px] text-gray-400">Due: {new Date(asgn.due_date).toLocaleDateString()}</div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        asgn.priority === 'HIGH' ? 'bg-rose-500/20 text-rose-300' :
                        asgn.priority === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
                        'bg-blue-500/20 text-blue-300'
                      }`}>
                        {asgn.priority}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: SUBJECTS & LIVE ATTENDANCE */}
      {/* ========================================================================= */}
      {activeTab === 'subjects' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-black text-white">Course Subjects & Attendance</h3>
              <p className="text-xs text-gray-400">Authoritative class attendance counts and projection trajectories.</p>
            </div>
            <button
              onClick={() => setShowSubjectModal(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Add Subject</span>
            </button>
          </div>

          {subjects.length === 0 ? (
            <div className="py-16 text-center space-y-4 p-8 rounded-3xl glass-panel border border-white/10">
              <BookOpen className="w-12 h-12 text-gray-600 mx-auto" />
              <div className="space-y-1">
                <h4 className="text-base font-bold text-white">No Subjects Added Yet</h4>
                <p className="text-xs text-gray-400 max-w-sm mx-auto">
                  Add your enrolled courses to track attendance counts, safe bunks, and exam requirements.
                </p>
              </div>
              <button
                onClick={() => setShowSubjectModal(true)}
                className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold shadow-lg shadow-purple-600/30 cursor-pointer"
              >
                + Register Subject
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {subjects.map((sub) => {
                const isSafe = sub.status_indicator === 'SAFE';
                const isOnTrack = sub.status_indicator === 'ON_TRACK';

                return (
                  <div
                    key={sub.id}
                    className={`p-5 rounded-3xl glass-panel border transition-all space-y-4 ${
                      isSafe ? 'border-emerald-500/30' : isOnTrack ? 'border-yellow-500/30' : 'border-rose-500/30'
                    }`}
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block">
                          {sub.code || 'COURSE'} • {sub.credits} Credits • {sub.faculty_name || 'Faculty'}
                        </span>
                        <h4 className="font-black text-sm text-white">{sub.name}</h4>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => setProjectionSubjectId(sub.id)}
                          title="Simulate Projections"
                          className="p-1.5 rounded-lg bg-purple-500/15 text-purple-300 hover:bg-purple-500/25 cursor-pointer"
                        >
                          <Calculator className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteSubject(sub.id)}
                          title="Delete Subject"
                          className="p-1.5 rounded-lg bg-white/5 text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Attendance Gauge */}
                    <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-gray-300">Attendance</span>
                        <span className="text-xl font-black text-white">{sub.current_percentage}%</span>
                      </div>
                      <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${
                            isSafe ? 'bg-emerald-500' : isOnTrack ? 'bg-yellow-500' : 'bg-rose-500'
                          }`}
                          style={{ width: `${Math.min(100, sub.current_percentage)}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-gray-400 pt-1">
                        <span>{sub.attended_classes} of {sub.total_classes} attended</span>
                        <span>Target: {sub.target_attendance}%</span>
                      </div>
                    </div>

                    {/* Metrics Status Badges */}
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div className="p-2.5 rounded-xl bg-white/5 border border-white/5">
                        <span className="text-[10px] text-gray-400 block font-bold uppercase">Safe Bunks</span>
                        <span className="font-bold text-emerald-400">{sub.bunkable_classes} available</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-white/5 border border-white/5">
                        <span className="text-[10px] text-gray-400 block font-bold uppercase">Target Deficit</span>
                        <span className="font-bold text-cyan-400">{sub.needed_classes} needed</span>
                      </div>
                    </div>

                    {/* Quick Logging Buttons */}
                    <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                      <span className="text-[10px] font-bold text-gray-500 uppercase mr-auto">Log:</span>
                      <button
                        onClick={() => handleQuickMarkAttendance(sub.id, 'PRESENT')}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-xs font-bold cursor-pointer"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Present</span>
                      </button>
                      <button
                        onClick={() => handleQuickMarkAttendance(sub.id, 'ABSENT')}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 text-xs font-bold cursor-pointer"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Bunk</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: TIMETABLE MATRIX */}
      {/* ========================================================================= */}
      {activeTab === 'timetable' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-black text-white">Weekly Timetable Schedule</h3>
              <p className="text-xs text-gray-400">Class timings, room allocations, and faculty assignments across Monday–Saturday.</p>
            </div>
            <button
              onClick={() => setShowTimetableModal(true)}
              disabled={subjects.length === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer disabled:opacity-40"
            >
              <Plus className="w-4 h-4" />
              <span>Add Timetable Slot</span>
            </button>
          </div>

          {timetable.length === 0 ? (
            <div className="py-16 text-center space-y-4 p-8 rounded-3xl glass-panel border border-white/10">
              <Calendar className="w-12 h-12 text-gray-600 mx-auto" />
              <div className="space-y-1">
                <h4 className="text-base font-bold text-white">No Timetable Slots Registered</h4>
                <p className="text-xs text-gray-400 max-w-sm mx-auto">
                  Add weekly lectures to build your personalized classroom matrix.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {daysOfWeek.map((dayName, dayIdx) => {
                const daySlots = timetable.filter(s => s.day_of_week === dayIdx);
                if (daySlots.length === 0) return null;

                return (
                  <div key={dayIdx} className="p-5 rounded-3xl glass-panel border border-white/10 space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b border-white/10">
                      <span className="text-xs font-black uppercase text-purple-400 tracking-wider">{dayName}</span>
                      <span className="text-[10px] text-gray-400 font-bold">{daySlots.length} Classes</span>
                    </div>

                    <div className="space-y-2">
                      {daySlots.map((slot) => (
                        <div key={slot.id} className="p-3 rounded-2xl bg-white/5 border border-white/5 space-y-1.5 group relative">
                          <div className="flex items-start justify-between">
                            <div>
                              <div className="text-xs font-bold text-white">{slot.subject_name}</div>
                              <div className="text-[10px] text-gray-400">
                                {slot.room || 'Room TBD'} {slot.faculty_name ? `• ${slot.faculty_name}` : ''}
                              </div>
                            </div>
                            <span className="px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 text-[10px] font-mono font-bold">
                              {slot.start_time} - {slot.end_time}
                            </span>
                          </div>
                          <button
                            onClick={() => handleDeleteTimetableSlot(slot.id)}
                            className="absolute top-2 right-2 p-1 rounded bg-rose-500/20 text-rose-300 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: ASSIGNMENTS */}
      {/* ========================================================================= */}
      {activeTab === 'assignments' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-black text-white">Assignments & Deadlines</h3>
              <p className="text-xs text-gray-400">Track homework, problem sets, and academic deadlines with priority alerts.</p>
            </div>
            <button
              onClick={() => setShowAssignmentModal(true)}
              disabled={subjects.length === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer disabled:opacity-40"
            >
              <Plus className="w-4 h-4" />
              <span>Add Assignment</span>
            </button>
          </div>

          {assignments.length === 0 ? (
            <div className="py-16 text-center space-y-4 p-8 rounded-3xl glass-panel border border-white/10">
              <CheckSquare className="w-12 h-12 text-gray-600 mx-auto" />
              <div className="space-y-1">
                <h4 className="text-base font-bold text-white">No Assignments Logged</h4>
                <p className="text-xs text-gray-400 max-w-sm mx-auto">
                  Add coursework assignments to monitor upcoming due dates.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {assignments.map((asgn) => {
                const isCompleted = asgn.status === 'COMPLETED';

                return (
                  <div 
                    key={asgn.id}
                    className={`p-5 rounded-3xl glass-panel border transition-all space-y-3 ${
                      isCompleted ? 'border-emerald-500/20 opacity-70' : 'border-white/10'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block">
                          {asgn.subject_name}
                        </span>
                        <h4 className={`font-bold text-sm text-white ${isCompleted ? 'line-through text-gray-400' : ''}`}>
                          {asgn.title}
                        </h4>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        asgn.priority === 'HIGH' ? 'bg-rose-500/20 text-rose-300' :
                        asgn.priority === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
                        'bg-blue-500/20 text-blue-300'
                      }`}>
                        {asgn.priority}
                      </span>
                    </div>

                    {asgn.description && (
                      <p className="text-xs text-gray-400 line-clamp-2">{asgn.description}</p>
                    )}

                    <div className="flex items-center justify-between text-[11px] text-gray-400 pt-2 border-t border-white/5">
                      <span>Due: {new Date(asgn.due_date).toLocaleDateString()}</span>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => handleToggleAssignmentStatus(asgn)}
                          className={`px-2.5 py-1 rounded-lg text-xs font-bold flex items-center gap-1 cursor-pointer ${
                            isCompleted
                              ? 'bg-emerald-500/20 text-emerald-300'
                              : 'bg-white/10 hover:bg-emerald-500/20 text-gray-300 hover:text-emerald-300'
                          }`}
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>{isCompleted ? 'Done' : 'Complete'}</span>
                        </button>
                        <button
                          onClick={() => handleDeleteAssignment(asgn.id)}
                          className="p-1.5 rounded-lg bg-white/5 text-gray-400 hover:text-rose-400 cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: EXAMS & INTERNAL MARKS */}
      {/* ========================================================================= */}
      {activeTab === 'exams_marks' && (
        <div className="space-y-8">
          {/* Section A: Upcoming Exams */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-black text-white">Upcoming Exams</h3>
                <p className="text-xs text-gray-400">Mid-semester, quizzes, labs, and end-term examinations.</p>
              </div>
              <button
                onClick={() => setShowExamModal(true)}
                disabled={subjects.length === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer disabled:opacity-40"
              >
                <Plus className="w-4 h-4" />
                <span>Add Exam</span>
              </button>
            </div>

            {exams.length === 0 ? (
              <div className="py-12 text-center p-6 rounded-3xl glass-panel border border-white/10 text-xs text-gray-500">
                No exams scheduled yet.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {exams.map((exam) => (
                  <div key={exam.id} className="p-5 rounded-3xl glass-panel border border-cyan-500/20 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block">
                          {exam.subject_name} • {exam.exam_type}
                        </span>
                        <h4 className="font-bold text-sm text-white">{exam.title}</h4>
                      </div>
                      <button
                        onClick={() => handleDeleteExam(exam.id)}
                        className="p-1 rounded bg-white/5 text-gray-400 hover:text-rose-400 cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="space-y-1 text-xs text-gray-300">
                      <div>📅 {new Date(exam.exam_date).toLocaleDateString()} at {exam.start_time || 'TBD'}</div>
                      <div>📍 Venue: {exam.venue || 'Classroom Hall'}</div>
                      {exam.syllabus_covered && (
                        <p className="text-[11px] text-gray-400 mt-1">Syllabus: {exam.syllabus_covered}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section B: Internal Marks Ledger */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-black text-white">Internal Assessment Marks</h3>
                <p className="text-xs text-gray-400">Scorecard of internal continuous evaluation marks.</p>
              </div>
              <button
                onClick={() => setShowMarkModal(true)}
                disabled={subjects.length === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer disabled:opacity-40"
              >
                <Plus className="w-4 h-4" />
                <span>Log Assessment Mark</span>
              </button>
            </div>

            {marks.length === 0 ? (
              <div className="py-12 text-center p-6 rounded-3xl glass-panel border border-white/10 text-xs text-gray-500">
                No internal marks recorded yet.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {marks.map((m) => (
                  <div key={m.id} className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] text-purple-400 font-bold uppercase">{m.subject_name}</span>
                        <div className="text-xs font-bold text-white">{m.assessment_name}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-base font-black text-white">{m.marks_obtained}/{m.max_marks}</div>
                        <div className="text-[10px] text-emerald-400 font-bold">{m.percentage}%</div>
                      </div>
                    </div>
                    {m.remarks && <p className="text-[11px] text-gray-400 italic">{m.remarks}</p>}
                    <div className="flex justify-end pt-1">
                      <button
                        onClick={() => handleDeleteMark(m.id)}
                        className="text-[10px] text-rose-400 hover:underline cursor-pointer"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 6: PROJECTS & NOTES */}
      {/* ========================================================================= */}
      {activeTab === 'projects_notes' && (
        <div className="space-y-8">
          {/* Projects */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-black text-white">Academic Projects</h3>
                <p className="text-xs text-gray-400">Course projects, research milestones, and repositories.</p>
              </div>
              <button
                onClick={() => setShowProjectModal(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Add Project</span>
              </button>
            </div>

            {projects.length === 0 ? (
              <div className="py-12 text-center p-6 rounded-3xl glass-panel border border-white/10 text-xs text-gray-500">
                No academic projects recorded.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.map((proj) => (
                  <div key={proj.id} className="p-5 rounded-3xl glass-panel border border-white/10 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        {proj.subject_name && (
                          <span className="text-[10px] font-bold text-purple-400 uppercase">{proj.subject_name}</span>
                        )}
                        <h4 className="font-bold text-sm text-white">{proj.title}</h4>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300">
                        {proj.status}
                      </span>
                    </div>
                    {proj.description && <p className="text-xs text-gray-400">{proj.description}</p>}
                    <div className="flex items-center gap-3 pt-2 border-t border-white/5 text-xs">
                      {proj.repository_url && (
                        <a
                          href={proj.repository_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-purple-400 hover:text-purple-300 flex items-center gap-1"
                        >
                          <FolderGit2 className="w-3.5 h-3.5" />
                          <span>Code Repository</span>
                        </a>
                      )}
                      {proj.documentation_url && (
                        <a
                          href={proj.documentation_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Docs</span>
                        </a>
                      )}
                      <button
                        onClick={() => handleDeleteProject(proj.id)}
                        className="ml-auto text-gray-500 hover:text-rose-400 cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Notes */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-black text-white">Academic Notes</h3>
                <p className="text-xs text-gray-400">Class notes, lecture summaries, and tagged study material.</p>
              </div>
              <button
                onClick={() => setShowNoteModal(true)}
                disabled={subjects.length === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer disabled:opacity-40"
              >
                <Plus className="w-4 h-4" />
                <span>Add Note</span>
              </button>
            </div>

            {notes.length === 0 ? (
              <div className="py-12 text-center p-6 rounded-3xl glass-panel border border-white/10 text-xs text-gray-500">
                No academic notes stored yet.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {notes.map((note) => (
                  <div key={note.id} className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                    <span className="text-[10px] text-purple-400 font-bold uppercase">{note.subject_name}</span>
                    <h4 className="font-bold text-xs text-white">{note.title}</h4>
                    {note.description && <p className="text-xs text-gray-400 line-clamp-3">{note.description}</p>}
                    {note.tags && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {note.tags.split(',').map((t, idx) => (
                          <span key={idx} className="px-1.5 py-0.5 rounded bg-white/5 text-[9px] text-gray-400">
                            #{t.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="flex justify-end pt-1">
                      <button
                        onClick={() => handleDeleteNote(note.id)}
                        className="text-[10px] text-rose-400 hover:underline cursor-pointer"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODALS */}
      {/* ========================================================================= */}

      {/* 1. Academic Profile Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Configure Academic Profile</h3>
            <form onSubmit={handleSaveProfile} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">College / University Name</label>
                <input
                  type="text"
                  value={profileForm.college_name}
                  onChange={e => setProfileForm(p => ({ ...p, college_name: e.target.value }))}
                  placeholder="e.g. MIT World Peace University"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Degree</label>
                  <input
                    type="text"
                    value={profileForm.degree}
                    onChange={e => setProfileForm(p => ({ ...p, degree: e.target.value }))}
                    placeholder="B.Tech, B.Sc"
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Branch / Major</label>
                  <input
                    type="text"
                    value={profileForm.branch}
                    onChange={e => setProfileForm(p => ({ ...p, branch: e.target.value }))}
                    placeholder="Computer Science"
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Current Semester</label>
                  <input
                    type="number"
                    value={profileForm.current_semester}
                    onChange={e => setProfileForm(p => ({ ...p, current_semester: parseInt(e.target.value) || 1 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Roll / Student ID</label>
                  <input
                    type="text"
                    value={profileForm.roll_number}
                    onChange={e => setProfileForm(p => ({ ...p, roll_number: e.target.value }))}
                    placeholder="MIT-2023-CS-042"
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowProfileModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-white shadow-lg shadow-purple-600/30"
                >
                  Save Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 2. Add Subject Modal */}
      {showSubjectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Add New Subject</h3>
            <form onSubmit={handleCreateSubject} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Subject Name</label>
                <input
                  type="text"
                  value={subjectForm.name}
                  onChange={e => setSubjectForm(s => ({ ...s, name: e.target.value }))}
                  placeholder="e.g. Design & Analysis of Algorithms"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Course Code</label>
                  <input
                    type="text"
                    value={subjectForm.code}
                    onChange={e => setSubjectForm(s => ({ ...s, code: e.target.value }))}
                    placeholder="CS301"
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Credits</label>
                  <input
                    type="number"
                    value={subjectForm.credits}
                    onChange={e => setSubjectForm(s => ({ ...s, credits: parseInt(e.target.value) || 3 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Faculty / Professor Name</label>
                <input
                  type="text"
                  value={subjectForm.faculty_name}
                  onChange={e => setSubjectForm(s => ({ ...s, faculty_name: e.target.value }))}
                  placeholder="Dr. Alan Turing"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Classes Attended</label>
                  <input
                    type="number"
                    value={subjectForm.attended_classes}
                    onChange={e => setSubjectForm(s => ({ ...s, attended_classes: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Total Classes Held</label>
                  <input
                    type="number"
                    value={subjectForm.total_classes}
                    onChange={e => setSubjectForm(s => ({ ...s, total_classes: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowSubjectModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-white shadow-lg shadow-purple-600/30"
                >
                  Save Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 3. Mark Attendance Modal */}
      {showAttendanceModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Mark Attendance Event</h3>
            <form onSubmit={handleLogAttendance} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Select Subject</label>
                <select
                  value={attendanceForm.subject_id}
                  onChange={e => setAttendanceForm(a => ({ ...a, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code || 'COURSE'})</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Date</label>
                  <input
                    type="date"
                    value={attendanceForm.date}
                    onChange={e => setAttendanceForm(a => ({ ...a, date: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Status</label>
                  <select
                    value={attendanceForm.status}
                    onChange={e => setAttendanceForm(a => ({ ...a, status: e.target.value as any }))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                  >
                    <option value="PRESENT">PRESENT</option>
                    <option value="ABSENT">ABSENT</option>
                    <option value="DUTY">DUTY LEAVE</option>
                    <option value="EXCUSED">EXCUSED</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Remarks (Optional)</label>
                <input
                  type="text"
                  value={attendanceForm.remarks}
                  onChange={e => setAttendanceForm(a => ({ ...a, remarks: e.target.value }))}
                  placeholder="e.g. Graph Algorithms lecture"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAttendanceModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-bold text-white shadow-lg shadow-emerald-600/30"
                >
                  Log Attendance
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 4. Add Timetable Slot Modal */}
      {showTimetableModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Add Timetable Slot</h3>
            <form onSubmit={handleCreateTimetableSlot} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Select Subject</label>
                <select
                  value={timetableForm.subject_id}
                  onChange={e => setTimetableForm(t => ({ ...t, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code || 'COURSE'})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Day of the Week</label>
                <select
                  value={timetableForm.day_of_week}
                  onChange={e => setTimetableForm(t => ({ ...t, day_of_week: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {daysOfWeek.map((d, idx) => (
                    <option key={idx} value={idx}>{d}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Start Time</label>
                  <input
                    type="time"
                    value={timetableForm.start_time}
                    onChange={e => setTimetableForm(t => ({ ...t, start_time: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">End Time</label>
                  <input
                    type="time"
                    value={timetableForm.end_time}
                    onChange={e => setTimetableForm(t => ({ ...t, end_time: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Room / Hall</label>
                <input
                  type="text"
                  value={timetableForm.room}
                  onChange={e => setTimetableForm(t => ({ ...t, room: e.target.value }))}
                  placeholder="e.g. Lab 3 / Hall 404"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowTimetableModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-white shadow-lg shadow-purple-600/30"
                >
                  Save Slot
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 5. Add Assignment Modal */}
      {showAssignmentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Add Assignment</h3>
            <form onSubmit={handleCreateAssignment} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Select Subject</label>
                <select
                  value={assignmentForm.subject_id}
                  onChange={e => setAssignmentForm(a => ({ ...a, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code || 'COURSE'})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Assignment Title</label>
                <input
                  type="text"
                  value={assignmentForm.title}
                  onChange={e => setAssignmentForm(a => ({ ...a, title: e.target.value }))}
                  placeholder="e.g. Dynamic Programming Problem Set"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Due Date & Time</label>
                  <input
                    type="datetime-local"
                    value={assignmentForm.due_date}
                    onChange={e => setAssignmentForm(a => ({ ...a, due_date: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Priority</label>
                  <select
                    value={assignmentForm.priority}
                    onChange={e => setAssignmentForm(a => ({ ...a, priority: e.target.value as any }))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Description / Notes</label>
                <textarea
                  value={assignmentForm.description}
                  onChange={e => setAssignmentForm(a => ({ ...a, description: e.target.value }))}
                  placeholder="Requirements, problem IDs, submission link..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAssignmentModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 font-bold text-white shadow-lg shadow-cyan-600/30"
                >
                  Save Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 6. Add Exam Modal */}
      {showExamModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Schedule Examination</h3>
            <form onSubmit={handleCreateExam} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Select Subject</label>
                <select
                  value={examForm.subject_id}
                  onChange={e => setExamForm(x => ({ ...x, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code || 'COURSE'})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Exam Title</label>
                <input
                  type="text"
                  value={examForm.title}
                  onChange={e => setExamForm(x => ({ ...x, title: e.target.value }))}
                  placeholder="e.g. Mid-Sem Examination"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Exam Type</label>
                  <select
                    value={examForm.exam_type}
                    onChange={e => setExamForm(x => ({ ...x, exam_type: e.target.value as any }))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                  >
                    <option value="QUIZ">QUIZ</option>
                    <option value="INTERNAL">INTERNAL</option>
                    <option value="MIDTERM">MIDTERM</option>
                    <option value="END_SEM">END_SEM</option>
                    <option value="LAB">LAB</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Exam Date & Time</label>
                  <input
                    type="datetime-local"
                    value={examForm.exam_date}
                    onChange={e => setExamForm(x => ({ ...x, exam_date: e.target.value }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Venue / Room</label>
                  <input
                    type="text"
                    value={examForm.venue}
                    onChange={e => setExamForm(x => ({ ...x, venue: e.target.value }))}
                    placeholder="Hall B-201"
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Max Marks</label>
                  <input
                    type="number"
                    value={examForm.max_marks}
                    onChange={e => setExamForm(x => ({ ...x, max_marks: parseFloat(e.target.value) || 100 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Syllabus Covered</label>
                <textarea
                  value={examForm.syllabus_covered}
                  onChange={e => setExamForm(x => ({ ...x, syllabus_covered: e.target.value }))}
                  placeholder="Units 1, 2, and 3: Graph Traversal, DP, Greedy"
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowExamModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-white shadow-lg shadow-purple-600/30"
                >
                  Schedule Exam
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 7. Add Mark Modal */}
      {showMarkModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Log Internal Assessment Marks</h3>
            <form onSubmit={handleCreateMark} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Select Subject</label>
                <select
                  value={markForm.subject_id}
                  onChange={e => setMarkForm(m => ({ ...m, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code || 'COURSE'})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Assessment Name</label>
                <input
                  type="text"
                  value={markForm.assessment_name}
                  onChange={e => setMarkForm(m => ({ ...m, assessment_name: e.target.value }))}
                  placeholder="e.g. Quiz 1: Relational Algebra"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Marks Obtained</label>
                  <input
                    type="number"
                    step="0.5"
                    value={markForm.marks_obtained}
                    onChange={e => setMarkForm(m => ({ ...m, marks_obtained: parseFloat(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Maximum Marks</label>
                  <input
                    type="number"
                    step="0.5"
                    value={markForm.max_marks}
                    onChange={e => setMarkForm(m => ({ ...m, max_marks: parseFloat(e.target.value) || 20 }))}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Remarks</label>
                <input
                  type="text"
                  value={markForm.remarks}
                  onChange={e => setMarkForm(m => ({ ...m, remarks: e.target.value }))}
                  placeholder="e.g. Top score"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowMarkModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 font-bold text-white shadow-lg shadow-rose-600/30"
                >
                  Save Marks
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 8. Add Project Modal */}
      {showProjectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Add Academic Project</h3>
            <form onSubmit={handleCreateProject} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Project Title</label>
                <input
                  type="text"
                  value={projectForm.title}
                  onChange={e => setProjectForm(p => ({ ...p, title: e.target.value }))}
                  placeholder="e.g. Distributed Key-Value Store"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Linked Subject (Optional)</label>
                <select
                  value={projectForm.subject_id}
                  onChange={e => setProjectForm(p => ({ ...p, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  <option value="">-- Standalone / General Project --</option>
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Description</label>
                <textarea
                  value={projectForm.description}
                  onChange={e => setProjectForm(p => ({ ...p, description: e.target.value }))}
                  placeholder="Core architecture and tech stack..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-gray-400 block mb-1">Repository URL</label>
                  <input
                    type="url"
                    value={projectForm.repository_url}
                    onChange={e => setProjectForm(p => ({ ...p, repository_url: e.target.value }))}
                    placeholder="https://github.com/..."
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
                <div>
                  <label className="text-gray-400 block mb-1">Docs URL</label>
                  <input
                    type="url"
                    value={projectForm.documentation_url}
                    onChange={e => setProjectForm(p => ({ ...p, documentation_url: e.target.value }))}
                    placeholder="https://..."
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowProjectModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-white shadow-lg shadow-purple-600/30"
                >
                  Save Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 9. Add Note Modal */}
      {showNoteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl glass-panel-glow border border-purple-500/40 bg-slate-950/90 text-white space-y-4">
            <h3 className="text-base font-black">Add Academic Note</h3>
            <form onSubmit={handleCreateNote} className="space-y-3 text-xs">
              <div>
                <label className="text-gray-400 block mb-1">Select Subject</label>
                <select
                  value={noteForm.subject_id}
                  onChange={e => setNoteForm(n => ({ ...n, subject_id: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-white/10 text-white"
                >
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code || 'COURSE'})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Note Title</label>
                <input
                  type="text"
                  value={noteForm.title}
                  onChange={e => setNoteForm(n => ({ ...n, title: e.target.value }))}
                  placeholder="e.g. B-Tree Disk Layouts"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                  required
                />
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Content / Summary</label>
                <textarea
                  value={noteForm.description}
                  onChange={e => setNoteForm(n => ({ ...n, description: e.target.value }))}
                  placeholder="Key concepts, formulas, lecture pointers..."
                  rows={3}
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Tags (Comma-separated)</label>
                <input
                  type="text"
                  value={noteForm.tags}
                  onChange={e => setNoteForm(n => ({ ...n, tags: e.target.value }))}
                  placeholder="dbms, btree, storage"
                  className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowNoteModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-white shadow-lg shadow-purple-600/30"
                >
                  Save Note
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 10. Attendance Projection Simulator Modal */}
      {projectionSubjectId && (
        <AttendanceProjectionModal
          subjectId={projectionSubjectId}
          onClose={() => setProjectionSubjectId(null)}
        />
      )}
    </div>
  );
};
