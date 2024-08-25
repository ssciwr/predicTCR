function validate_email(email: string) {
  const re = /\S+@\S+\.\S+$/;
  return re.test(email);
}

function validate_password(password: string) {
  // at least 8 chars, including lower-case, upper-case, number
  const re = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$/;
  return re.test(password);
}

export { validate_email, validate_password };
