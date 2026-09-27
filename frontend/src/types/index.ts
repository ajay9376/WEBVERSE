export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'DUTY' | 'EXCUSED';
export type AssignmentStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
export type AssignmentPriority = 'LOW' | 'MEDIUM' | 'HIGH';
export type ExamType = 'QUIZ' | 'INTERNAL' | 'MIDTERM' | 'END_SEM' | 'LAB' | 'OTHER';
export type AssessmentType = 'QUIZ' | 'ASSIGNMENT' | 'MIDTERM' | 'LAB' | 'PROJECT' | 'OTHER';
export type ProjectStatus = 'PLANNING' | 'IN_PROGRESS' | 'COMPLETED' | 'SUBMITTED';

export type CategoryType = 'INCOME' | 'EXPENSE';
export type TransactionType = 'INCOME' | 'EXPENSE';
export type PaymentMethod = 'UPI' | 'CARD' | 'CASH' | 'BANK_TRANSFER' | 'NET_BANKING' | 'OTHER';
export type BillingCycle = 'WEEKLY' | 'MONTHLY' | 'QUARTERLY' | 'YEARLY' | 'CUSTOM';
export type SubscriptionStatus = 'ACTIVE' | 'PAUSED' | 'CANCELLED';

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

export interface AcademicProfile {
  id: string;
  user_id: string;
  college_name?: string;
  university?: string;
  degree?: string;
  branch?: string;
  current_year?: number;
  current_semester?: number;
  roll_number?: string;
  academic_start_year?: number;
  created_at: string;
  updated_at: string;
}

export interface SubjectItem {
  id: string;
  user_id: string;
  name: string;
  code?: string;
  credits: number;
  semester?: number;
  faculty_name?: string;
  color: string;
  total_classes: number;
  attended_classes: number;
  target_attendance: number;
  min_attendance: number;
  current_percentage: number;
  status_indicator: 'SAFE' | 'ON_TRACK' | 'WARNING' | 'CRITICAL' | 'NO_DATA';
  bunkable_classes: number;
  needed_classes: number;
  created_at: string;
  updated_at: string;
}

export interface AttendanceRecordItem {
  id: string;
  user_id: string;
  subject_id: string;
  subject_name?: string;
  subject_code?: string;
  date: string;
  status: AttendanceStatus;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

export interface AttendanceSummary {
  overall_percentage: number;
  total_classes: number;
  attended_classes: number;
  below_target_count: number;
  subjects_count: number;
  subjects: SubjectItem[];
}

export interface AttendanceProjection {
  subject_id: string;
  subject_name: string;
  subject_code?: string;
  total_classes: number;
  attended_classes: number;
  current_percentage: number;
  target_percentage: number;
  min_percentage: number;
  status_indicator: string;
  classes_needed_for_target: number;
  classes_safe_to_bunk: number;
  if_attend_next_1: number;
  if_miss_next_1: number;
  if_attend_next_3: number;
  if_miss_next_3: number;
  if_attend_next_5: number;
  if_miss_next_5: number;
}

export interface TimetableSlotItem {
  id: string;
  user_id: string;
  subject_id: string;
  subject_name: string;
  subject_code?: string;
  subject_color?: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  room?: string;
  faculty_name?: string;
  created_at: string;
  updated_at: string;
}

export interface AssignmentItem {
  id: string;
  user_id: string;
  subject_id: string;
  subject_name: string;
  subject_code?: string;
  subject_color?: string;
  title: string;
  description?: string;
  due_date: string;
  status: AssignmentStatus;
  priority: AssignmentPriority;
  total_marks?: number;
  obtained_marks?: number;
  created_at: string;
  updated_at: string;
}

export interface ExamItem {
  id: string;
  user_id: string;
  subject_id: string;
  subject_name: string;
  subject_code?: string;
  subject_color?: string;
  title: string;
  exam_type: ExamType;
  exam_date: string;
  start_time?: string;
  end_time?: string;
  venue?: string;
  syllabus_covered?: string;
  max_marks?: number;
  obtained_marks?: number;
  created_at: string;
  updated_at: string;
}

export interface InternalMarkItem {
  id: string;
  user_id: string;
  subject_id: string;
  subject_name?: string;
  subject_code?: string;
  assessment_name: string;
  assessment_type: AssessmentType;
  marks_obtained: number;
  max_marks: number;
  percentage: number;
  assessment_date?: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicProjectItem {
  id: string;
  user_id: string;
  subject_id?: string;
  subject_name?: string;
  title: string;
  description?: string;
  status: ProjectStatus;
  deadline?: string;
  repository_url?: string;
  documentation_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicNoteItem {
  id: string;
  user_id: string;
  subject_id: string;
  subject_name?: string;
  title: string;
  description?: string;
  tags?: string;
  file_url?: string;
  file_name?: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicDashboardData {
  profile?: AcademicProfile;
  current_semester?: number;
  subjects_count: number;
  attendance: {
    overall_percentage: number;
    total_classes: number;
    attended_classes: number;
    below_target_count: number;
  };
  low_attendance_subjects: SubjectItem[];
  upcoming_assignments: AssignmentItem[];
  upcoming_exams: ExamItem[];
  pending_assignments_count: number;
  recent_marks: InternalMarkItem[];
  projects_count: number;
  notes_count: number;
}

export interface ExpenseCategory {
  id: string;
  user_id: string;
  name: string;
  category_type: CategoryType;
  icon: string;
  color: string;
  budget_limit?: number;
  spent_amount?: number;
  is_system?: boolean;
  created_at?: string;
}

export interface CategorySpend {
  category_id?: string;
  category_name: string;
  color: string;
  icon: string;
  amount: number;
  percentage: number;
  budget_limit?: number;
  is_over_budget?: boolean;
}

export interface TransactionItem {
  id: string;
  user_id: string;
  category_id?: string;
  category_name: string;
  category_color: string;
  category_icon?: string;
  title: string;
  merchant?: string;
  amount: number;
  type: TransactionType;
  transaction_type?: TransactionType;
  date: string;
  payment_method: PaymentMethod;
  notes?: string;
  is_recurring: boolean;
  receipt_document_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface TransactionListResponse {
  transactions: TransactionItem[];
  total_count: number;
  total_income: number;
  total_expenses: number;
  net_balance: number;
}

export interface BudgetItem {
  id: string;
  user_id: string;
  category_id?: string;
  category_name?: string;
  category_color?: string;
  amount: number;
  month: number;
  year: number;
  period: string;
  spent_amount: number;
  remaining_amount: number;
  percentage_used: number;
  is_over_budget: boolean;
  created_at: string;
}

export interface BudgetUsageSummary {
  period: string;
  overall_budget: number;
  total_spent: number;
  remaining_budget: number;
  percentage_used: number;
  is_over_budget: boolean;
  category_budgets: BudgetItem[];
}

export interface SubscriptionItem {
  id: string;
  user_id: string;
  category_id?: string;
  category_name?: string;
  name: string;
  amount: number;
  billing_cycle: BillingCycle;
  next_billing_date: string;
  payment_method: PaymentMethod;
  status: SubscriptionStatus;
  notes?: string;
  monthly_equivalent: number;
  is_active: boolean;
  created_at: string;
}

export interface MonthlyTrendPoint {
  month_label: string;
  period: string;
  income: number;
  expenses: number;
  net_savings: number;
}

export interface SpendingTrendsResponse {
  period_count: number;
  trends: MonthlyTrendPoint[];
}

export interface FinanceDashboardData {
  period: string;
  total_income: number;
  total_expenses: number;
  net_balance: number;
  savings_percentage: number;
  monthly_budget_target: number;
  remaining_budget: number;
  budget_used_percentage: number;
  is_over_budget: boolean;
  burn_rate_per_day: number;
  projected_month_end_expense: number;
  active_subscriptions_count: number;
  monthly_subscription_total: number;
  top_categories: CategorySpend[];
  recent_transactions: TransactionItem[];
  upcoming_subscriptions: SubscriptionItem[];
  spending_trends: MonthlyTrendPoint[];
}

export type FinanceAnalytics = FinanceDashboardData;


export type DocumentCategory = 
  | 'IDENTITY' 
  | 'EDUCATION' 
  | 'INSURANCE' 
  | 'FINANCE' 
  | 'BILLS' 
  | 'MEDICAL' 
  | 'TRAVEL' 
  | 'CERTIFICATES' 
  | 'LEGAL' 
  | 'OTHER';

export type BillStatus = 'PENDING' | 'PAID' | 'OVERDUE' | 'CANCELLED';
export type RecurrencePattern = 'NONE' | 'WEEKLY' | 'MONTHLY' | 'QUARTERLY' | 'YEARLY' | 'CUSTOM';
export type PolicyType = 'HEALTH' | 'VEHICLE' | 'LIFE' | 'TRAVEL' | 'HOME' | 'OTHER';
export type PremiumFrequency = 'MONTHLY' | 'QUARTERLY' | 'YEARLY' | 'ONE_TIME';
export type ImportantDateCategory = 'PASSPORT' | 'LICENSE' | 'WARRANTY' | 'COLLEGE' | 'RENEWAL' | 'ANNIVERSARY' | 'OTHER';
export type ReminderPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ReminderStatus = 'PENDING' | 'COMPLETED' | 'CANCELLED';

export interface LifeAdminCategory {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  icon: string;
  color: string;
  is_system: boolean;
  created_at?: string;
}

export interface DocumentItem {
  id: string;
  user_id?: string;
  category_id?: string;
  title: string;
  description?: string;
  filename: string;
  file_name?: string;
  file_type: string;
  mime_type?: string;
  file_size: number;
  category: DocumentCategory;
  tags?: string;
  document_date?: string;
  expiry_date?: string;
  issuer?: string;
  reference_number?: string;
  extracted_text_preview?: string;
  metadata_fields?: Record<string, any>;
  is_indexed: boolean;
  days_until_expiry?: number;
  is_expired?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface BillItem {
  id: string;
  user_id: string;
  title: string;
  provider: string;
  category: string;
  amount: number;
  due_date: string;
  status: BillStatus;
  recurring: boolean;
  recurrence: RecurrencePattern;
  payment_reference?: string;
  notes?: string;
  days_until_due: number;
  days_overdue: number;
  is_overdue: boolean;
  created_at: string;
  updated_at?: string;
}

export interface InsurancePolicyItem {
  id: string;
  user_id: string;
  provider: string;
  policy_name: string;
  policy_number: string;
  policy_type: PolicyType;
  start_date?: string;
  expiry_date: string;
  premium_amount: number;
  premium_frequency: PremiumFrequency;
  coverage_amount?: number;
  document_id?: string;
  notes?: string;
  days_until_expiry: number;
  is_expired: boolean;
  is_expiring_soon: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ImportantDateItem {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  date: string;
  category: ImportantDateCategory;
  recurring: boolean;
  recurrence: RecurrencePattern;
  days_remaining: number;
  is_past: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ReminderItem {
  id: string;
  user_id?: string;
  title: string;
  description?: string;
  due_at: string;
  priority: ReminderPriority;
  status?: ReminderStatus;
  is_completed: boolean;
  linked_module?: string;
  linked_id?: string;
  created_at: string;
  updated_at?: string;
  is_overdue: boolean;
  days_until_due?: number;
}

export interface LifeAdminDashboardData {
  total_documents: number;
  category_counts: Record<string, number>;
  bills_summary: {
    pending_count: number;
    overdue_count: number;
    paid_count: number;
    total_pending_amount: number;
    total_overdue_amount: number;
    upcoming_bills: BillItem[];
  };
  policies_summary: {
    total_policies: number;
    expiring_soon_count: number;
    total_annual_premiums: number;
    expiring_policies: InsurancePolicyItem[];
  };
  upcoming_dates: ImportantDateItem[];
  pending_reminders: ReminderItem[];
  recent_documents: DocumentItem[];
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
