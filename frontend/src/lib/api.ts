import {
  AcademicProfile,
  SubjectItem,
  AttendanceRecordItem,
  AttendanceSummary,
  AttendanceProjection,
  TimetableSlotItem,
  AssignmentItem,
  ExamItem,
  InternalMarkItem,
  AcademicProjectItem,
  AcademicNoteItem,
  AcademicDashboardData,
  DashboardGlance,
  FinanceDashboardData,
  SpendingTrendsResponse,
  ExpenseCategory,
  TransactionListResponse,
  TransactionItem,
  BudgetItem,
  BudgetUsageSummary,
  SubscriptionItem,
  LifeAdminCategory,
  DocumentItem,
  BillItem,
  InsurancePolicyItem,
  ImportantDateItem,
  ReminderItem,
  LifeAdminDashboardData,
  ConversationBrief,
  ConversationDetail,
  ChatMessage,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiService {
  public static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('webverse_token');
  }

  public static setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('webverse_token', token);
    }
  }

  public static clearToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('webverse_token');
    }
  }

  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}`;
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorMsg;
      } catch (e) {
        // ignore
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // ==================== AUTH & SYSTEM ====================
  static async register(data: any) {
    return this.request<{ access_token: string; token_type: string; user_id: string; email: string; full_name: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async login(data: any) {
    return this.request<{ access_token: string; token_type: string; user_id: string; email: string; full_name: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async getMe() {
    return this.request<any>('/auth/me');
  }

  static async getDashboardStats() {
    return this.request<any>('/dashboard/stats');
  }

  static async getDashboardGlance() {
    return this.request<DashboardGlance>('/dashboard/glance');
  }

  // ==================== STUDENTOS / ACADEMICS ====================
  static async getAcademicProfile() {
    return this.request<AcademicProfile | null>('/academics/profile').catch(() => null);
  }

  static async updateAcademicProfile(data: Partial<AcademicProfile>) {
    return this.request<AcademicProfile>('/academics/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async getSubjects() {
    return this.request<SubjectItem[]>('/academics/subjects').catch(() => []);
  }

  static async getSubject(id: string) {
    return this.request<SubjectItem>(`/academics/subjects/${id}`);
  }

  static async createSubject(data: Partial<SubjectItem>) {
    return this.request<SubjectItem>('/academics/subjects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateSubject(id: string, data: Partial<SubjectItem>) {
    return this.request<SubjectItem>(`/academics/subjects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteSubject(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/subjects/${id}`, {
      method: 'DELETE',
    });
  }

  static async markAttendance(data: { subject_id: string; date: string; status: string; remarks?: string }) {
    return this.request<AttendanceRecordItem>('/academics/attendance/mark', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async getSubjectAttendanceHistory(subjectId: string) {
    return this.request<AttendanceRecordItem[]>(`/academics/subjects/${subjectId}/attendance`).catch(() => []);
  }

  static async getAttendanceSummary() {
    return this.request<AttendanceSummary>('/academics/attendance/summary');
  }

  static async getAttendanceProjection(subjectId: string) {
    return this.request<AttendanceProjection>(`/academics/attendance/${subjectId}/projection`);
  }

  static async getTimetable() {
    return this.request<TimetableSlotItem[]>('/academics/timetable').catch(() => []);
  }

  static async createTimetableSlot(data: Partial<TimetableSlotItem>) {
    return this.request<TimetableSlotItem>('/academics/timetable', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateTimetableSlot(id: string, data: Partial<TimetableSlotItem>) {
    return this.request<TimetableSlotItem>(`/academics/timetable/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteTimetableSlot(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/timetable/${id}`, {
      method: 'DELETE',
    });
  }

  static async getAssignments(statusFilter?: string) {
    return this.request<AssignmentItem[]>(`/academics/assignments${statusFilter ? `?status_filter=${statusFilter}` : ''}`).catch(() => []);
  }

  static async createAssignment(data: Partial<AssignmentItem>) {
    return this.request<AssignmentItem>('/academics/assignments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateAssignment(id: string, data: Partial<AssignmentItem>) {
    return this.request<AssignmentItem>(`/academics/assignments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteAssignment(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/assignments/${id}`, {
      method: 'DELETE',
    });
  }

  static async getExams() {
    return this.request<ExamItem[]>('/academics/exams').catch(() => []);
  }

  static async createExam(data: Partial<ExamItem>) {
    return this.request<ExamItem>('/academics/exams', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateExam(id: string, data: Partial<ExamItem>) {
    return this.request<ExamItem>(`/academics/exams/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteExam(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/exams/${id}`, {
      method: 'DELETE',
    });
  }

  static async getInternalMarks(subjectId?: string) {
    return this.request<InternalMarkItem[]>(`/academics/marks${subjectId ? `?subject_id=${subjectId}` : ''}`).catch(() => []);
  }

  static async createInternalMark(data: Partial<InternalMarkItem>) {
    return this.request<InternalMarkItem>('/academics/marks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async deleteInternalMark(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/marks/${id}`, {
      method: 'DELETE',
    });
  }

  static async getProjects() {
    return this.request<AcademicProjectItem[]>('/academics/projects').catch(() => []);
  }

  static async createProject(data: Partial<AcademicProjectItem>) {
    return this.request<AcademicProjectItem>('/academics/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateProject(id: string, data: Partial<AcademicProjectItem>) {
    return this.request<AcademicProjectItem>(`/academics/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteProject(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/projects/${id}`, {
      method: 'DELETE',
    });
  }

  static async getNotes(subjectId?: string) {
    return this.request<AcademicNoteItem[]>(`/academics/notes${subjectId ? `?subject_id=${subjectId}` : ''}`).catch(() => []);
  }

  static async createNote(data: Partial<AcademicNoteItem>) {
    return this.request<AcademicNoteItem>('/academics/notes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async deleteNote(id: string) {
    return this.request<{ status: string; message: string }>(`/academics/notes/${id}`, {
      method: 'DELETE',
    });
  }

  static async getAcademicDashboard() {
    return this.request<AcademicDashboardData>('/academics/dashboard');
  }

  // ==================== FINANCE / MONEY MANAGER ====================
  static async getFinanceDashboard(period?: string) {
    return this.request<FinanceDashboardData>(`/finance/dashboard${period ? `?period=${period}` : ''}`);
  }

  static async getFinanceAnalytics(month?: string) {
    return this.getFinanceDashboard(month).catch(() => null);
  }

  static async getFinanceSummary(period?: string) {
    return this.request<any>(`/finance/summary${period ? `?period=${period}` : ''}`);
  }

  static async getCategoryAnalytics(period?: string) {
    return this.request<any>(`/finance/analytics/categories${period ? `?period=${period}` : ''}`);
  }

  static async getSpendingTrends(months: number = 6) {
    return this.request<SpendingTrendsResponse>(`/finance/analytics/trends?months=${months}`);
  }

  static async getCategories(categoryType?: string) {
    return this.request<ExpenseCategory[]>(`/finance/categories${categoryType ? `?type=${categoryType}` : ''}`).catch(() => []);
  }

  static async createCategory(data: Partial<ExpenseCategory>) {
    return this.request<ExpenseCategory>('/finance/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateCategory(id: string, data: Partial<ExpenseCategory>) {
    return this.request<ExpenseCategory>(`/finance/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteCategory(id: string) {
    return this.request<{ message: string; category_id: string }>(`/finance/categories/${id}`, {
      method: 'DELETE',
    });
  }

  static async getTransactions(params?: {
    category_id?: string;
    type?: string;
    time_range?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }) {
    const query = new URLSearchParams();
    if (params?.category_id) query.append('category_id', params.category_id);
    if (params?.type) query.append('type', params.type);
    if (params?.time_range) query.append('time_range', params.time_range);
    if (params?.start_date) query.append('start_date', params.start_date);
    if (params?.end_date) query.append('end_date', params.end_date);
    if (params?.search) query.append('search', params.search);
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());
    const qs = query.toString();
    return this.request<TransactionListResponse>(`/finance/transactions${qs ? `?${qs}` : ''}`);
  }

  static async createTransaction(data: Partial<TransactionItem>) {
    return this.request<TransactionItem>('/finance/transactions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateTransaction(id: string, data: Partial<TransactionItem>) {
    return this.request<TransactionItem>(`/finance/transactions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteTransaction(id: string) {
    return this.request<{ message: string; transaction_id: string }>(`/finance/transactions/${id}`, {
      method: 'DELETE',
    });
  }

  static async getBudgets(period?: string) {
    return this.request<BudgetItem[]>(`/finance/budgets${period ? `?period=${period}` : ''}`).catch(() => []);
  }

  static async setBudget(data: Partial<BudgetItem>) {
    return this.request<BudgetItem>('/finance/budgets', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async deleteBudget(id: string) {
    return this.request<{ message: string; budget_id: string }>(`/finance/budgets/${id}`, {
      method: 'DELETE',
    });
  }

  static async getBudgetSummary(period?: string) {
    return this.request<BudgetUsageSummary>(`/finance/budgets/summary${period ? `?period=${period}` : ''}`);
  }

  static async getSubscriptions(status?: string) {
    return this.request<SubscriptionItem[]>(`/finance/subscriptions${status ? `?status=${status}` : ''}`).catch(() => []);
  }

  static async createSubscription(data: Partial<SubscriptionItem>) {
    return this.request<SubscriptionItem>('/finance/subscriptions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateSubscription(id: string, data: Partial<SubscriptionItem>) {
    return this.request<SubscriptionItem>(`/finance/subscriptions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteSubscription(id: string) {
    return this.request<{ message: string; subscription_id: string }>(`/finance/subscriptions/${id}`, {
      method: 'DELETE',
    });
  }


  // ----------------- Life Admin Vault APIs -----------------
  static async getLifeAdminDashboard() {
    return this.request<LifeAdminDashboardData>('/life-admin/dashboard');
  }

  static async getLifeAdminCategories() {
    return this.request<LifeAdminCategory[]>('/life-admin/categories').catch(() => []);
  }

  static async createLifeAdminCategory(data: Partial<LifeAdminCategory>) {
    return this.request<LifeAdminCategory>('/life-admin/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async deleteLifeAdminCategory(id: string) {
    return this.request<{ success: boolean; message: string }>(`/life-admin/categories/${id}`, {
      method: 'DELETE',
    });
  }

  static async getDocuments(params?: { category?: string; search?: string; expiry_filter?: string }) {
    const query = new URLSearchParams();
    if (params?.category && params.category !== 'ALL') query.append('category', params.category);
    if (params?.search) query.append('search', params.search);
    if (params?.expiry_filter) query.append('expiry_filter', params.expiry_filter);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<DocumentItem[]>(`/life-admin/documents${qs}`).catch(() => []);
  }

  static async getDocument(id: string) {
    return this.request<DocumentItem>(`/life-admin/documents/${id}`);
  }

  static async uploadDocument(formData: FormData) {
    const token = this.getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(`${API_BASE_URL}/life-admin/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json() as Promise<DocumentItem>;
  }

  static async createDocumentMetadata(data: Partial<DocumentItem>) {
    return this.request<DocumentItem>('/life-admin/documents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateDocument(id: string, data: Partial<DocumentItem>) {
    return this.request<DocumentItem>(`/life-admin/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteDocument(id: string) {
    return this.request<{ success: boolean; message: string }>(`/life-admin/documents/${id}`, {
      method: 'DELETE',
    });
  }

  static async downloadDocument(id: string, filename: string) {
    const token = this.getToken();
    const res = await fetch(`${API_BASE_URL}/life-admin/documents/${id}/download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error('Failed to download document');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // Bills
  static async getBills(params?: { status?: string; category?: string; provider?: string; search?: string }) {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'ALL') query.append('status', params.status);
    if (params?.category) query.append('category', params.category);
    if (params?.provider) query.append('provider', params.provider);
    if (params?.search) query.append('search', params.search);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<BillItem[]>(`/life-admin/bills${qs}`).catch(() => []);
  }

  static async createBill(data: Partial<BillItem>) {
    return this.request<BillItem>('/life-admin/bills', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateBill(id: string, data: Partial<BillItem>) {
    return this.request<BillItem>(`/life-admin/bills/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async payBill(id: string, paymentReference?: string) {
    const qs = paymentReference ? `?payment_reference=${encodeURIComponent(paymentReference)}` : '';
    return this.request<BillItem>(`/life-admin/bills/${id}/pay${qs}`, {
      method: 'PATCH',
    });
  }

  static async deleteBill(id: string) {
    return this.request<{ success: boolean; message: string }>(`/life-admin/bills/${id}`, {
      method: 'DELETE',
    });
  }

  // Insurance Policies
  static async getPolicies(params?: { policy_type?: string; provider?: string; search?: string }) {
    const query = new URLSearchParams();
    if (params?.policy_type && params.policy_type !== 'ALL') query.append('policy_type', params.policy_type);
    if (params?.provider) query.append('provider', params.provider);
    if (params?.search) query.append('search', params.search);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<InsurancePolicyItem[]>(`/life-admin/policies${qs}`).catch(() => []);
  }

  static async createPolicy(data: Partial<InsurancePolicyItem>) {
    return this.request<InsurancePolicyItem>('/life-admin/policies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updatePolicy(id: string, data: Partial<InsurancePolicyItem>) {
    return this.request<InsurancePolicyItem>(`/life-admin/policies/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deletePolicy(id: string) {
    return this.request<{ success: boolean; message: string }>(`/life-admin/policies/${id}`, {
      method: 'DELETE',
    });
  }

  // Important Dates
  static async getImportantDates(params?: { category?: string; search?: string }) {
    const query = new URLSearchParams();
    if (params?.category && params.category !== 'ALL') query.append('category', params.category);
    if (params?.search) query.append('search', params.search);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<ImportantDateItem[]>(`/life-admin/dates${qs}`).catch(() => []);
  }

  static async createImportantDate(data: Partial<ImportantDateItem>) {
    return this.request<ImportantDateItem>('/life-admin/dates', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateImportantDate(id: string, data: Partial<ImportantDateItem>) {
    return this.request<ImportantDateItem>(`/life-admin/dates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async deleteImportantDate(id: string) {
    return this.request<{ success: boolean; message: string }>(`/life-admin/dates/${id}`, {
      method: 'DELETE',
    });
  }

  // Reminders
  static async getReminders(params?: { status?: string; priority?: string }) {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.priority) query.append('priority', params.priority);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<ReminderItem[]>(`/life-admin/reminders${qs}`).catch(() => []);
  }

  static async createReminder(data: Partial<ReminderItem>) {
    return this.request<ReminderItem>('/life-admin/reminders', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async updateReminder(id: string, data: Partial<ReminderItem>) {
    return this.request<ReminderItem>(`/life-admin/reminders/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async toggleReminder(id: string) {
    return this.request<ReminderItem>(`/life-admin/reminders/${id}/toggle`, {
      method: 'PATCH',
    });
  }

  static async deleteReminder(id: string) {
    return this.request<{ success: boolean; message: string }>(`/life-admin/reminders/${id}`, {
      method: 'DELETE',
    });
  }

  static async sendChatMessage(data: { message: string; session_id?: string }) {
    return this.request<any>('/ai/chat', { method: 'POST', body: JSON.stringify(data) });
  }

  static async executeAIAction(data: { action_type: string; params: any; message_id?: string }) {
    return this.request<any>('/ai/action/execute', { method: 'POST', body: JSON.stringify(data) });
  }

  // Conversation Management
  static async getConversations() {
    return this.request<ConversationBrief[]>('/ai/conversations').catch(() => []);
  }

  static async getConversation(conversationId: string) {
    return this.request<ConversationDetail>(`/ai/conversations/${conversationId}`);
  }

  static async createConversation(data: { title: string; module_focus?: string }) {
    return this.request<ConversationBrief>('/ai/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async deleteConversation(conversationId: string) {
    return this.request<void>(`/ai/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  static async getConversationMessages(conversationId: string) {
    return this.request<ChatMessage[]>(`/ai/conversations/${conversationId}/messages`).catch(() => []);
  }
}
