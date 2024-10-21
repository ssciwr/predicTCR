<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/stores/user";
import { FwbInput, FwbButton, FwbAlert } from "flowbite-vue";
import { apiClient } from "@/utils/api-client";
import router from "@/router";
const userStore = useUserStore();
const login_email_address = ref("");
const login_password = ref("");
const login_error_message = ref("");

function do_login() {
  apiClient
    .post("login", {
      email: login_email_address.value,
      password: login_password.value,
    })
    .then((response) => {
      login_error_message.value = "";
      userStore.user = response.data.user;
      userStore.token = response.data.access_token;
      router.push({ name: "samples" });
    })
    .catch((error) => {
      login_error_message.value = `Login failed: ${error.response.data.message}`;
      userStore.user = null;
      userStore.token = "";
    });
}
</script>

<template>
  <div>
    <form @submit.prevent="do_login">
      <fwb-input
        v-model="login_email_address"
        required
        id="login_email"
        placeholder="your.name@domain.com"
        maxlength="256"
        autocomplete="username"
        label="Email"
        class="mb-2"
      />
      <fwb-input
        v-model="login_password"
        required
        id="login_password"
        type="password"
        maxlength="256"
        autocomplete="current-password"
        label="Password"
        class="mb-2"
      />
      <fwb-button type="submit" class="mb-2">Login</fwb-button>
    </form>
    <fwb-alert type="danger" v-if="login_error_message.length > 0">
      {{ login_error_message }}
    </fwb-alert>
  </div>
</template>
