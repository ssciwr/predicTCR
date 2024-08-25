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
};
