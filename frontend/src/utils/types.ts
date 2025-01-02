export type Sample = {
  id: number;
  email: string;
  name: string;
  tumor_type: string;
  source: number;
  timestamp: number;
  timestamp_job_start: number;
  timestamp_job_end: number;
  status: string;
  has_results_zip: boolean;
  error_message: string;
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
  runner_job_timeout_mins: number;
  about_md: string;
  max_filesize_h5_mb: number;
  max_filesize_csv_mb: number;
};

export type Job = {
  id: number;
  sample_id: number;
  runner_id: number;
  runner_hostname: string;
  timestamp_start: number;
  timestamp_end: number;
  status: string;
  error_message: string;
};
