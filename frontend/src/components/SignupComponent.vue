<script setup lang="ts">
import { ref, computed } from "vue";
import { apiClient } from "@/utils/api-client";
import { validate_email, validate_password } from "@/utils/validation";
import { FwbInput, FwbButton, FwbAlert } from "flowbite-vue";
const signup_email_address = ref("");
const signup_email_address_message = computed(() => {
  if (validate_email(signup_email_address.value)) {
    return "";
  } else {
    return "Please use a valid email address.";
  }
});
const signup_password = ref("");
const signup_password_message = computed(() => {
  if (validate_password(signup_password.value)) {
    return "";
  } else {
    return "At least 8 characters, including lower-case, upper-case and a number.";
  }
});
const signup_response_message = ref("");

function do_signup() {
  apiClient
    .post("signup", {
      email: signup_email_address.value,
      password: signup_password.value,
    })
    .then((response) => {
      signup_response_message.value = response.data.message;
    })
    .catch((error) => {
      signup_response_message.value = error.response.data.message;
    });
}
</script>

<template>
  <div>
    <p>
      If you don't yet have an account, you can create one by entering a valid
      email address and choosing a password. Your account will then need to be
      manually activated by an administrator before you are able to log in:
    </p>
    <div class="mt-4">
      <fwb-input
        v-model="signup_email_address"
        required
        id="signup_email"
        placeholder=""
        maxlength="256"
        autocomplete="username"
        label="Email"
        class="mb-2"
        :validation-status="
          signup_email_address_message.length > 0 ? 'error' : 'success'
        "
      >
        <template #validationMessage>
          {{ signup_email_address_message }}
        </template>
      </fwb-input>
      <fwb-input
        v-model="signup_password"
        required
        id="signup_password"
        type="password"
        label="Password"
        placeholder=""
        maxlength="256"
        class="mb-2"
        :validation-status="
          signup_password_message.length > 0 ? 'error' : 'success'
        "
      >
        <template #validationMessage>
          {{ signup_password_message }}
        </template>
      </fwb-input>
      <fwb-button
        @click="do_signup"
        class="mb-2"
        :disabled="
          signup_email_address_message.length + signup_password_message.length >
          0
        "
        >Sign up</fwb-button
      >
      <fwb-alert type="info" v-if="signup_response_message.length > 0">
        {{ signup_response_message }}
      </fwb-alert>
    </div>
  </div>
</template>
