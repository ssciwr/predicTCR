<script setup lang="ts">
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
import ListItem from "@/components/ListItem.vue";
const reset_email_address = ref("");
const reset_message = ref("");
function do_reset() {
  apiClient
    .post("request_password_reset", {
      email: reset_email_address.value,
    })
    .then((response) => {
      reset_message.value = response.data.message;
    })
    .catch((error) => {
      reset_message.value = `${error.response.data.message}`;
    });
}
</script>

<template>
  <ListItem title="Reset password" icon="bi-person">
    <p>
      If you have forgotten your password you can request a password reset email
      by entering the email address you used to sign up:
    </p>
    <form @submit.prevent="do_reset">
      <p>
        <label for="reset_email">Email:</label>
        <input
          v-model="reset_email_address"
          id="reset_email"
          placeholder="your.name@uni-heidelberg.de"
          maxlength="256"
        />
      </p>
      <p>
        <input type="submit" />
        <span class="error-message pad-left">
          {{ reset_message }}
        </span>
      </p>
    </form>
  </ListItem>
</template>
