<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/stores/user";
import { apiClient } from "@/utils/api-client";
import ListItem from "@/components/ListItem.vue";
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
    })
    .catch((error) => {
      login_error_message.value = `Login failed: ${error.response.data.message}`;
      userStore.user = null;
      userStore.token = "";
    });
}
</script>

<template>
  <ListItem title="Login" icon="bi-person">
    <p>Log in with the email address and password you used to sign up:</p>
    <form @submit.prevent="do_login">
      <p>
        <label for="login_email">Email:</label>
        <input
          v-model="login_email_address"
          id="login_email"
          placeholder="your.name@domain.com"
          maxlength="256"
          autocomplete="username"
        />
      </p>
      <p>
        <label for="login_password">Password:</label>
        <input
          v-model="login_password"
          id="login_password"
          type="password"
          maxlength="256"
          autocomplete="current-password"
        />
      </p>
      <p>
        <input type="submit" />
        <span class="error-message pad-left">
          {{ login_error_message }}
        </span>
      </p>
    </form>
  </ListItem>
</template>
