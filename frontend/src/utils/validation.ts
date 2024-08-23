function validate_email(email: string) {
  const re = /\S+@((\S*heidelberg)|embl|dkfz)\.de$/;
  return re.test(email);
}

function validate_password(password: string) {
  // at least 8 chars, including lower-case, upper-case, number
  const re = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$/;
  return re.test(password);
}

function validate_sample_name(sample_name: string) {
  // only alphanumeric characters or underscores
  const re = /^([A-Za-z0-9_]+)$/;
  return re.test(sample_name);
}

export { validate_email, validate_password, validate_sample_name };
