export type Sample = {
  id: number;
  email: string;
  primary_key: string;
  tube_primary_key: string;
  name: string;
  running_option: string;
  concentration: number;
  date: string;
  has_reference_seq_zip: boolean;
  has_results_zip: boolean;
};

export type User = {
  id: number;
  email: string;
  activated: boolean;
  is_admin: boolean;
};

export type Settings = {
  plate_n_rows: number;
  plate_n_cols: number;
  running_options: Array<string>;
  last_submission_day: number;
};

export type RunningOptions = Array<string>;
