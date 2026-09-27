export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'CANCELLED' | 'DUTY_LEAVE';
export type AssignmentStatus = 'PENDING' | 'IN_PROGRESS' | 'SUBMITTED' | 'GRADED';
export type TransactionType = 'INCOME' | 'EXPENSE';
export type PaymentMethod = 'UPI' | 'CARD' | 'CASH' | 'NET_BANKING' | 'OTHER';
export type DocumentCategory = 'INSURANCE' | 'CERTIFICATE' | 'BILL' | 'RECEIPT' | 'IDENTITY' | 'ACADEMIC' | 'MEDICAL' | 'OTHER';
export type ReminderPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  college_name?: string;
  semester?: string;
  branch?: string;
  monthly_budget_target?: string;
  created_at: string;
}

export interface SubjectItem {
  id: string;
  user_id: string;
  name: string;
  code?: string;
  professor?: string;
  color: string;
  min_attendance_percent: number;
  target_attendance_percent: number;
  total_classes: number;
  attended_classes: number;
  current_percentage: number;
  status_indicator: 'SAFE' | 'ON_TRACK' | 'AT_RISK' | 'CRITICAL';
  bunkable_classes: number;
  needed_classes: number;
  created_at: string;
}

export interface TimetableSlotItem {
  id: string;
  subject_id: string;
  subject_name: string;
  subject_code?: string;
  subject_color: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  room?: string;
}

export interface AssignmentItem {
  id: string;
  subject_id: string;
  subject_name: string;
  subject_color: string;
  title: string;
  description?: string;
  due_date: string;
  status: AssignmentStatus;
  total_marks?: number;
  obtained_marks?: number;
  created_at: string;
}

export interface ExamItem {
  id: string;
  subject_id: string;
  subject_name: string;
  subject_color: string;
  title: string;
  exam_date: string;
  location?: string;
  syllabus_covered?: string;
  total_marks?: number;
  obtained_marks?: number;
  created_at: string;
}

export interface ExpenseCategory {
  id: string;
  user_id: string;
  name: string;
  icon: string;
  color: string;
  budget_limit?: number;
  spent_amount?: number;
}

export interface CategorySpend {
  category_id?: string;
  category_name: string;
  color: string;
  amount: number;
  percentage: number;
}

export interface TransactionItem {
  id: string;
  category_id?: string;
  category_name: string;
  category_color: string;
  title: string;
  amount: number;
  type: TransactionType;
  date: string;
  payment_method: PaymentMethod;
  notes?: string;
  is_recurring: boolean;
  created_at: string;
}

export interface SubscriptionItem {
  id: string;
  name: string;
  amount: number;
  billing_cycle: string;
  next_billing_date: string;
  is_active: boolean;
  created_at: string;
}

export interface FinanceAnalytics {
  current_month: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  monthly_budget_target: number;
  budget_used_percentage: number;
  remaining_budget: number;
  is_over_budget: boolean;
  burn_rate_per_day: number;
  projected_month_end_expense: number;
  top_categories: CategorySpend[];
  recent_transactions: TransactionItem[];
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  category: DocumentCategory;
  tags?: string;
  extracted_text_preview?: string;
  metadata_fields?: Record<string, any>;
  is_indexed: boolean;
  created_at: string;
}

export interface ReminderItem {
  id: string;
  title: string;
  description?: string;
  due_at: string;
  priority: ReminderPriority;
  is_completed: boolean;
  linked_module?: string;
  linked_id?: string;
  created_at: string;
  is_overdue: boolean;
}

export interface CitationSource {
  module: string;
  title: string;
  detail: string;
  reference_id?: string;
}

export interface ActionProposal {
  action_type: string;
  module: string;
  params: Record<string, any>;
  summary_text: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  routed_modules: string[];
  source_references: CitationSource[];
  action_proposal?: ActionProposal;
  action_status?: 'PROPOSED' | 'EXECUTED' | 'FAILED';
  created_at: string;
}

export interface DashboardGlance {
  user_name: string;
  greeting: string;
  overall_attendance_percent: number;
  subjects_at_risk_count: number;
  upcoming_assignments: AssignmentItem[];
  upcoming_exams: ExamItem[];
  monthly_budget_target: number;
  monthly_total_spent: number;
  monthly_remaining_budget: number;
  budget_health_status: 'HEALTHY' | 'CAUTION' | 'CRITICAL';
  pending_reminders: ReminderItem[];
  urgent_alerts_count: number;
  recent_documents: DocumentItem[];
  active_dimensions: string[];
}
