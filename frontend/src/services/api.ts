export interface ASTEvidence {
  rule_id: string;
  rule_name: string;
  line_number: number;
  col_offset: number;
  end_line_number?: number;
  node_type: string;
  snippet: string;
  evidence_text: string;
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
  recommended_fix: string;
}

export interface RuleMatch {
  rule_id: string;
  rule_name: string;
  category: string;
  severity: string;
  score: number;
  description: string;
}

export interface MigrationStageLog {
  stage_number: number;
  stage_name: string;
  status: 'completed' | 'failed' | 'skipped';
  latency_ms: number;
  details: Record<string, any>;
  message: string;
}

export interface PytestOutput {
  exit_code: number;
  passed: boolean;
  summary: string;
  stdout: string;
  stderr: string;
  tests_run: number;
  duration_s: number;
  failure_details?: string;
}

export interface MigrationRunRecord {
  id: string;
  created_at: string;
  source_code: string;
  migrated_code: string;
  diff: string;
  status: 'success' | 'repaired' | 'failed' | 'syntax_error';
  passed_validation: boolean;
  repair_attempts: number;
  total_latency_ms: number;
  ast_findings: ASTEvidence[];
  stages: MigrationStageLog[];
  pytest_result?: PytestOutput;
  rules_applied: string[];
  error_message?: string;
}

export interface ExperimentSummary {
  experiment_id: string;
  experiment_name: string;
  description: string;
  total_cases: number;
  passed_cases: number;
  pass_rate: number;
  syntax_rate: number;
  rule_recall: number;
  avg_latency_ms: number;
  repair_success_rate: number;
  category_breakdown: Record<string, {
    total: number;
    passed: number;
    pass_rate: number;
    syntax_rate: number;
    recall: number;
    avg_latency_ms: number;
  }>;
  timestamp: string;
}

export interface BenchmarkCase {
  id: string;
  name: string;
  category: string;
  description: string;
  source_code_v1: string;
  test_code: string;
  expected_rules: string[];
  golden_v2_code?: string;
}

export interface SystemHealth {
  status: string;
  version: string;
  provider: string;
  is_ollama_online: boolean;
  rules_count: number;
  environment: string;
}

export interface MigrationRule {
  id: string;
  name: string;
  category: string;
  severity: string;
  description: string;
  v1_pattern: string;
  v2_pattern: string;
  code_example_before: string;
  code_example_after: string;
  fix_strategy: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  provider: 'local' | 'google' | 'guest';
  created_at: string;
}

export interface UserStats {
  saved_migrations: number;
  benchmark_runs: number;
  success_rate: number;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
  stats: UserStats;
}

const API_BASE = '/api';

let currentToken: string | null = localStorage.getItem('clientshift_token');

export const setAuthToken = (token: string | null) => {
  currentToken = token;
  if (token) {
    localStorage.setItem('clientshift_token', token);
  } else {
    localStorage.removeItem('clientshift_token');
  }
};

export const getAuthToken = (): string | null => {
  return currentToken;
};

const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  if (currentToken) {
    headers['Authorization'] = `Bearer ${currentToken}`;
  }
  return headers;
};

export const api = {
  // Authentication Endpoints
  async signup(payload: { email: string; password: string; full_name: string }): Promise<AuthTokenResponse> {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Signup failed' }));
      throw new Error(err.detail || 'Signup failed');
    }
    const data: AuthTokenResponse = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  async login(payload: { email: string; password: string }): Promise<AuthTokenResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
      throw new Error(err.detail || 'Login failed');
    }
    const data: AuthTokenResponse = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  async googleAuth(payload: { credential?: string; email?: string; full_name?: string; avatar_url?: string }): Promise<AuthTokenResponse> {
    const res = await fetch(`${API_BASE}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Google authentication failed' }));
      throw new Error(err.detail || 'Google authentication failed');
    }
    const data: AuthTokenResponse = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  async guestLogin(): Promise<AuthTokenResponse> {
    const res = await fetch(`${API_BASE}/auth/guest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Guest login failed');
    const data: AuthTokenResponse = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  async getMe(): Promise<{ user: UserProfile; stats: UserStats }> {
    const token = getAuthToken();
    if (!token) throw new Error('No active authentication token');
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      setAuthToken(null);
      throw new Error('Session expired');
    }
    return res.json();
  },

  async getHealth(): Promise<SystemHealth> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async getRules(): Promise<MigrationRule[]> {
    const res = await fetch(`${API_BASE}/rules`);
    if (!res.ok) throw new Error('Failed to fetch catalog rules');
    return res.json();
  },

  async analyzeCode(source_code: string): Promise<{
    ast_findings: ASTEvidence[];
    matched_rules: RuleMatch[];
    syntax_error?: string;
  }> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ source_code })
    });
    if (!res.ok) throw new Error('Analysis request failed');
    return res.json();
  },

  async migrateCode(source_code: string, test_code?: string, max_repairs: number = 2): Promise<MigrationRunRecord> {
    const res = await fetch(`${API_BASE}/migrate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ source_code, test_code, max_repairs })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Migration failed' }));
      throw new Error(err.detail || 'Migration failed');
    }
    return res.json();
  },

  async listMigrations(limit: number = 30): Promise<MigrationRunRecord[]> {
    const res = await fetch(`${API_BASE}/migrations?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch migrations list');
    return res.json();
  },

  async getMigration(id: string): Promise<MigrationRunRecord> {
    const res = await fetch(`${API_BASE}/migrations/${id}`);
    if (!res.ok) throw new Error('Migration not found');
    return res.json();
  },

  async getBenchmarkSummaries(): Promise<ExperimentSummary[]> {
    const res = await fetch(`${API_BASE}/benchmark/summary`);
    if (!res.ok) throw new Error('Failed to fetch benchmark summary');
    return res.json();
  },

  async getBenchmarkCases(category?: string, limit?: number): Promise<BenchmarkCase[]> {
    let url = `${API_BASE}/benchmark/cases`;
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (limit) params.append('limit', limit.toString());
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch benchmark cases');
    return res.json();
  },

  async runBenchmark(experiment_id: string = 'all', limit?: number, category?: string): Promise<ExperimentSummary[]> {
    const res = await fetch(`${API_BASE}/benchmark/run`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ experiment_id, limit, category })
    });
    if (!res.ok) throw new Error('Benchmark execution failed');
    return res.json();
  },

  async chatWithNilo(payload: {
    message: string;
    code_context?: string;
    error_context?: string;
    current_stage?: string;
  }): Promise<{ reply: string; suggested_actions: string[]; rule_references: string[] }> {
    const res = await fetch(`${API_BASE}/nilo/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Nilo assistant chat request failed');
    return res.json();
  }
};
