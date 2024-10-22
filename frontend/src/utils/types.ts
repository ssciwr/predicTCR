export type Sample = {
  id: number;
  email: string;
  name: string;
  tumor_type: string;
  source: number;
  timestamp: number;
  status: string;
  has_results_zip: boolean;
};

export type User = {
  id: number;
  email: string;
  activated: boolean;
  enabled: boolean;
  quota: number;
  last_submission_timestamp: number;
  is_admin: boolean;
  is_runner: boolean;
  full_results: boolean;
  submission_interval_minutes: number;
};

export type Settings = {
  id: number;
  default_personal_submission_quota: number;
  default_personal_submission_interval_mins: number;
  global_quota: number;
  tumor_types: string;
  sources: string;
  csv_required_columns: string;
};
