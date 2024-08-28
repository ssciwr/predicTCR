import { expect, test } from "vitest";
import { validate_password, validate_email } from "../validation";

test.each([
  "",
  "abc123A",
  "passwordpassword",
  "abc12345678",
  "asd!(*&@#@!(*#%ASDASDFGK",
])("validate_password::invalid %s", (invalid_password) => {
  expect(validate_password(invalid_password)).toBeFalsy();
});

test.each([
  "123456Aa",
  "abcABC123",
  "abcQ12345678",
  "as8d!(*&@#@!(*#%ASDASDFGK",
])("validate_password::valid %s", (valid_password) => {
  expect(validate_password(valid_password)).toBeTruthy();
});

test.each(["", "asadas", "@asdas.com"])(
  "validate_email::invalid %s",
  (invalid_email) => {
    expect(validate_email(invalid_email)).toBeFalsy();
  },
);

test.each([
  "a@b.com",
  "me@embl.de",
  "joe@embl.dex",
  "x@embl.de",
  "a.b@dkfz.de",
  "x.y.z@uni-heidelberg.de",
  "x.y.z@embl.uni-heidelberg.de",
])("validate_email::valid %s", (valid_email) => {
  expect(validate_email(valid_email)).toBeTruthy();
});
