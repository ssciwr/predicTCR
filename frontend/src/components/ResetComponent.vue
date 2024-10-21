<script setup lang="ts">
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
import CardComponent from "@/components/CardComponent.vue";
import { FwbInput, FwbButton, FwbAlert } from "flowbite-vue";
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
  <CardComponent title="Reset password">
    <p>
      If you have forgotten your password you can request a password reset email
      by entering the email address you used to sign up:
    </p>
    <div class="mt-4">
      <fwb-input
        v-model="reset_email_address"
        required
        id="reset_email"
        placeholder=""
        maxlength="256"
        autocomplete="username"
        label="Email"
        class="mb-2"
      />
      <fwb-button @click="do_reset" class="mb-2">Submit</fwb-button>
      <fwb-alert type="danger" v-if="reset_message.length > 0">
        {{ reset_message }}
      </fwb-alert>
    </div>
  </CardComponent>
</template>
