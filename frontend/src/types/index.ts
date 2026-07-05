export interface User {
  id: number;
  email: string;
  full_name: string;
  user_type: 'client' | 'lawyer' | 'admin';
  created_at: string;
}

export interface Case {
  id: number;
  title: string;
  description: string;
  case_type: string;
  jurisdiction: string;
  court_level: string;
  status: 'open' | 'in_progress' | 'closed' | 'won' | 'lost' | 'appealed';
  opposing_party?: string;
  ai_analysis?: CaseAnalysis;
  confidence_score?: number;
  created_at: string;
  updated_at: string;
}

export interface CaseAnalysis {
  win_probability: number;
  key_issues: string[];
  legal_strategy: string;
  relevant_statutes: string[];
  similar_cases: Array<{name: string; court: string; year: number; outcome: string}>;
  next_steps: string[];
  risk_factors: string[];
  estimated_duration: string;
  estimated_cost: string;
}

export interface Document {
  id: number;
  title: string;
  document_type: string;
  template_id?: string;
  content: string;
  language: string;
  status: 'draft' | 'final' | 'signed';
  is_ai_generated: boolean;
  created_at: string;
  updated_at: string;
}

export interface Lawyer {
  id: number;
  full_name: string;
  bar_council_number: string;
  specializations: string[];
  practice_areas: string[];
  city: string;
  state: string;
  years_experience: number;
  hourly_rate: number;
  consultation_fee: number;
  rating: number;
  review_count: number;
  languages: string[];
  bio: string;
  court_levels: string[];
  available: boolean;
  verified: boolean;
}

export interface Template {
  id: string;
  name: string;
  category: string;
  description: string;
  fields: string[];
  applicable_law: string;
}

export interface Course {
  id: string;
  title: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  description: string;
  duration_hours: number;
  lessons_count: number;
  category: string;
  lessons?: Lesson[];
  quiz?: QuizQuestion[];
}

export interface Lesson {
  id: number;
  title: string;
  content: string;
  duration_mins: number;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent_used?: string;
  confidence_score?: number;
  timestamp: Date;
}

export interface Plan {
  id: string;
  name: string;
  price_inr: number;
  price_paise: number;
  billing: string;
  tagline: string;
  features: string[];
  limits: { ai_queries: number; cases: number; documents: number; research: number };
  popular: boolean;
}

export interface Subscription {
  plan: string;
  status: string;
  current_period_end: string | null;
  limits: Plan['limits'];
  razorpay_key_id: string | null;
}

export interface SearchResult {
  title: string;
  type: 'statute' | 'case' | 'principle';
  court?: string;
  year?: number;
  excerpt: string;
  relevance_score: number;
  full_text?: string;
}
