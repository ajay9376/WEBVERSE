'use client';

import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, Calendar, CheckSquare, Clock, Plus, 
  CheckCircle2, XCircle, AlertCircle, Sparkles, BookOpen 
} from 'lucide-react';
import { ApiService } from '@/lib/api';
import { SubjectItem, AssignmentItem, ExamItem, TimetableSlotItem } from '@/types';

export const AcademicsView: React.FC = () => {
  const [subjects, setSubjects] = useState<SubjectItem[]>([]);
  const [assignments, setAssignments] = useState<AssignmentItem[]>([]);
  const [exams, setExams] = useState<ExamItem[]>([]);
  const [timetable, setTimetable] = useState<TimetableSlotItem[]>([]);
  const [loading, setLoading] = useState(true);

  // New subject form state
  const [showAddSubject, setShowAddSubject] = useState(false);
  const [subName, setSubName] = useState('');
  const [subCode, setSubCode] = useState('');
  const [subProf, setSubProf] = useState('');

  const loadAcademicData = async () => {
    try {
      setLoading(true);
      const [subsData, asgnsData, examsData, ttData] = await Promise.all([
        ApiService.getSubjects(),
        ApiService.getAssignments(),
        ApiService.getExams(),
        ApiService.getTimetable(),
      ]);
      setSubjects(subsData || []);
      setAssignments(asgnsData || []);
      setExams(examsData || []);
      setTimetable(ttData || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAcademicData();
  }, []);

  const handleMarkAttendance = async (subjectId: string, status: 'PRESENT' | 'ABSENT') => {
    try {
      await ApiService.markAttendance({
        subject_id: subjectId,
        date: new Date().toISOString().split('T')[0],
        status,
      });
      await loadAcademicData();
    } catch (err: any) {
      alert(`Could not log attendance: ${err.message}`);
    }
  };

  const handleCreateSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subName.trim()) return;

    try {
      await ApiService.createSubject({
        name: subName,
        code: subCode,
        professor: subProf,
        color: '#8B5CF6',
        min_attendance_percent: 75.0,
        target_attendance_percent: 85.0,
      });
      setSubName('');
      setSubCode('');
      setSubProf('');
      setShowAddSubject(false);
      await loadAcademicData();
    } catch (err: any) {
      alert(`Could not create subject: ${err.message}`);
    }
  };

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Dimension Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 text-purple-400 text-xs font-bold uppercase tracking-wider mb-1">
            <GraduationCap className="w-4 h-4" />
            <span>Dimension: StudentOS</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">Academic Intelligence</h2>
          <p className="text-xs text-gray-400">
            Attendance monitoring, safe bunk predictions, timetable matrix, and upcoming exams.
          </p>
        </div>

        <button
          onClick={() => setShowAddSubject(!showAddSubject)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 transition-all cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Subject</span>
        </button>
      </div>

      {/* Add Subject Modal / Collapse Form */}
      {showAddSubject && (
        <form
          onSubmit={handleCreateSubject}
          className="p-5 rounded-2xl glass-panel-glow border border-purple-500/30 space-y-4 animate-in fade-in slide-in-from-top-2"
        >
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-purple-400" />
            <span>Register New Subject</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input
              type="text"
              placeholder="Subject Name (e.g. Design & Analysis of Algorithms)"
              value={subName}
              onChange={(e) => setSubName(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              required
            />
            <input
              type="text"
              placeholder="Course Code (e.g. CS501)"
              value={subCode}
              onChange={(e) => setSubCode(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
            <input
              type="text"
              placeholder="Professor / Faculty Name"
              value={subProf}
              onChange={(e) => setSubProf(e.target.value)}
              className="px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddSubject(false)}
              className="px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-semibold cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold cursor-pointer"
            >
              Save Subject
            </button>
          </div>
        </form>
      )}

      {/* 1. Subjects & Live Attendance Matrix */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-purple-400" />
            <span>Attendance & Safe Bunk Analytics</span>
          </h3>
          <span className="text-xs text-gray-400">{subjects.length} Subjects Registered</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((sub) => {
            const isSafe = sub.status_indicator === 'SAFE';
            const isOnTrack = sub.status_indicator === 'ON_TRACK';
            const isCritical = sub.status_indicator === 'CRITICAL' || sub.status_indicator === 'AT_RISK';

            return (
              <div
                key={sub.id}
                className={`p-5 rounded-2xl glass-panel border transition-all hover:scale-[1.01] ${
                  isSafe
                    ? 'border-emerald-500/30'
                    : isOnTrack
                    ? 'border-yellow-500/30'
                    : 'border-rose-500/30'
                }`}
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <span className="text-[10px] font-bold text-gray-400 block uppercase tracking-wider">
                      {sub.code || 'COURSE'} • {sub.professor || 'Faculty'}
                    </span>
                    <h4 className="font-bold text-sm text-white">{sub.name}</h4>
                  </div>
                  <div
                    className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                      isSafe
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : isOnTrack
                        ? 'bg-yellow-500/20 text-yellow-300'
                        : 'bg-rose-500/20 text-rose-300'
                    }`}
                  >
                    {sub.current_percentage}%
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden mb-3">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isSafe
                        ? 'bg-emerald-500'
                        : isOnTrack
                        ? 'bg-yellow-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${Math.min(100, sub.current_percentage)}%` }}
                  />
                </div>

                {/* Metric Badges */}
                <div className="grid grid-cols-2 gap-2 text-[11px] mb-4">
                  <div className="p-2 rounded-xl bg-white/5 text-gray-300">
                    <span className="text-[10px] text-gray-500 block">Attended</span>
                    <span className="font-bold text-white">{sub.attended_classes}</span> / {sub.total_classes} classes
                  </div>
                  <div className="p-2 rounded-xl bg-white/5 text-gray-300">
                    <span className="text-[10px] text-gray-500 block">
                      {isCritical ? 'Deficit Classes' : 'Safe Bunks'}
                    </span>
                    <span
                      className={`font-bold ${
                        isCritical ? 'text-rose-400' : 'text-emerald-400'
                      }`}
                    >
                      {isCritical ? `${sub.needed_classes} needed` : `${sub.bunkable_classes} available`}
                    </span>
                  </div>
                </div>

                {/* Quick Log Buttons */}
                <div className="flex items-center gap-2 pt-2 border-t border-white/5">
                  <span className="text-[10px] uppercase font-bold text-gray-500 mr-auto">Log Class:</span>
                  <button
                    onClick={() => handleMarkAttendance(sub.id, 'PRESENT')}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 text-[11px] font-bold transition-all cursor-pointer"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Present</span>
                  </button>
                  <button
                    onClick={() => handleMarkAttendance(sub.id, 'ABSENT')}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 text-[11px] font-bold transition-all cursor-pointer"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Bunk</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Timetable & Schedule Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timetable */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-panel">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-purple-400" />
              <span>Weekly Timetable Matrix</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {timetable.map((slot) => (
              <div
                key={slot.id}
                className="p-3.5 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between"
              >
                <div>
                  <span className="text-[10px] font-bold text-purple-400 uppercase">
                    {daysOfWeek[slot.day_of_week] || 'Day'} • Room {slot.room || 'TBD'}
                  </span>
                  <div className="font-bold text-xs text-white">{slot.subject_name}</div>
                </div>
                <div className="text-right">
                  <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 text-[10px] font-bold">
                    {slot.start_time} - {slot.end_time}
                  </span>
                </div>
              </div>
            ))}
            {timetable.length === 0 && (
              <p className="text-xs text-gray-500 py-4 col-span-2 text-center">
                No timetable slots registered yet. Seed demo data to populate schedule.
              </p>
            )}
          </div>
        </div>

        {/* Upcoming Exams & Tests */}
        <div className="p-5 rounded-2xl glass-panel">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Upcoming Exams</span>
          </h3>

          <div className="space-y-3">
            {exams.map((exam) => (
              <div
                key={exam.id}
                className="p-3.5 rounded-xl bg-white/5 border border-white/10 space-y-1.5"
              >
                <div className="flex items-center justify-between text-[10px] text-gray-400">
                  <span className="text-cyan-300 font-bold uppercase">{exam.subject_name}</span>
                  <span>{new Date(exam.exam_date).toLocaleDateString()}</span>
                </div>
                <h4 className="font-bold text-xs text-white">{exam.title}</h4>
                {exam.syllabus_covered && (
                  <p className="text-[11px] text-gray-400 line-clamp-2">
                    Syllabus: {exam.syllabus_covered}
                  </p>
                )}
              </div>
            ))}
            {exams.length === 0 && (
              <p className="text-xs text-gray-500 py-4 text-center">No exams scheduled.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
