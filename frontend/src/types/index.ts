/**
 * SecureRedLab - Frontend Type Definitions
 * Phase 8.1 - Project Setup
 */

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  id: string
  email: string
  username: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  last_login?: string
}

export enum UserRole {
  ADMIN = 'admin',
  ANALYST = 'analyst',
  VIEWER = 'viewer',
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

// ============================================================================
// Scan Types
// ============================================================================

export interface Scan {
  id: string
  name?: string
  target: string
  type?: string
  tool?: string
  scan_type?: ScanType
  status: ScanStatus | string
  progress: number
  started_at?: string
  completed_at?: string
  duration?: number
  user_id?: string
  results?: ScanResults
  error?: string
  created_at: string
  updated_at: string
}

export interface ScanConfig {
  target: string
  scan_type: ScanType | string
  options?: Record<string, any>
}

export enum ScanType {
  NMAP = 'nmap',
  NUCLEI = 'nuclei',
  CUSTOM = 'custom',
}

export enum ScanStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface ScanResults {
  open_ports?: number[]
  services?: ServiceInfo[]
  vulnerabilities?: Vulnerability[]
  os_detection?: string
  summary: string
}

export interface ServiceInfo {
  port: number
  protocol: string
  service: string
  version?: string
  state: string
}

// ============================================================================
// Attack/Exploitation Types
// ============================================================================

export interface Attack {
  id: string
  name?: string
  scan_id?: string
  target: string
  type?: string
  tool?: string
  attack_type?: AttackType
  module?: string
  payload?: string
  status: AttackStatus | string
  severity?: string
  progress: number
  started_at?: string
  completed_at?: string
  user_id?: string
  results?: AttackResults
  error?: string
  created_at: string
  updated_at: string
}

export interface AttackConfig {
  target: string
  attack_type: AttackType | string
  module?: string
  options?: Record<string, any>
}

export enum AttackType {
  METASPLOIT = 'metasploit',
  SQLMAP = 'sqlmap',
  CUSTOM = 'custom',
}

export enum AttackStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  SUCCESS = 'success',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface AttackResults {
  success: boolean
  exploited: boolean
  sessions?: Session[]
  vulnerabilities?: Vulnerability[]
  output: string
}

export interface Session {
  id: string
  type: string
  host: string
  port: number
  established_at: string
  info?: Record<string, any>
}

// ============================================================================
// Vulnerability Types
// ============================================================================

export interface Vulnerability {
  id: string
  scan_id?: string
  name: string
  title?: string
  severity: VulnerabilitySeverity | string
  cvss_score?: number
  cvss_vector?: string
  cve_id?: string
  cwe_id?: string
  description: string
  affected_service?: string
  target?: string
  port?: number
  recommendation?: string
  references?: string[]
  discovered_at?: string
  status?: string
  resolved_at?: string
  evidence?: string | Record<string, any>
  created_at: string
  updated_at: string
}

export enum VulnerabilitySeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  INFO = 'info',
}

// ============================================================================
// Report Types
// ============================================================================

export interface Report {
  id: string
  title: string
  type: ReportType
  status: ReportStatus
  created_at: string
  updated_at: string
  user_id: string
  scans: string[]
  attacks: string[]
  summary: ReportSummary
  file_path?: string
}

export enum ReportType {
  EXECUTIVE = 'executive',
  TECHNICAL = 'technical',
  COMPLIANCE = 'compliance',
}

export enum ReportStatus {
  DRAFT = 'draft',
  GENERATING = 'generating',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface ReportSummary {
  total_scans: number
  total_attacks: number
  total_vulnerabilities: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  info_count: number
}

// ============================================================================
// Real-time Event Types
// ============================================================================

export interface WebSocketMessage {
  type: EventType
  data: any
  timestamp: string
}

export enum EventType {
  SCAN_STARTED = 'scan.started',
  SCAN_PROGRESS = 'scan.progress',
  SCAN_COMPLETED = 'scan.completed',
  SCAN_FAILED = 'scan.failed',
  
  ATTACK_STARTED = 'attack.started',
  ATTACK_PROGRESS = 'attack.progress',
  ATTACK_COMPLETED = 'attack.completed',
  ATTACK_FAILED = 'attack.failed',
  
  SYSTEM_ALERT = 'system.alert',
  SYSTEM_INFO = 'system.info',
}

export interface ProgressUpdate {
  entity_id: string
  entity_type: 'scan' | 'attack'
  progress: number
  message: string
  timestamp: string
}

// ============================================================================
// Dashboard Stats Types
// ============================================================================

export interface DashboardStats {
  total_scans: number
  active_scans: number
  total_attacks: number
  active_attacks: number
  total_vulnerabilities: number
  critical_vulnerabilities: number
  recent_scans: Scan[]
  recent_attacks: Attack[]
  severity_distribution: SeverityDistribution
  scan_history: ChartDataPoint[]
}

export interface SeverityDistribution {
  critical: number
  high: number
  medium: number
  low: number
  info: number
}

export interface ChartDataPoint {
  date: string
  value: number
  label?: string
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ============================================================================
// Form Types
// ============================================================================

export interface ScanFormData {
  target: string
  scan_type: ScanType
  ports?: string
  options?: Record<string, any>
}

export interface AttackFormData {
  target: string
  attack_type: AttackType
  module: string
  payload?: string
  options?: Record<string, any>
}

// ============================================================================
// Theme Types
// ============================================================================

export type Theme = 'light' | 'dark' | 'system'

// ============================================================================
// Notification Types
// ============================================================================

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: string
  read: boolean
  action?: NotificationAction
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
}

export interface NotificationAction {
  label: string
  url: string
}
