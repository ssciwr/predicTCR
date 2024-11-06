<script setup lang="ts">
import CardComponent from "@/components/CardComponent.vue";
import { ref, computed } from "vue";
import { apiClient, logout } from "@/utils/api-client";
import { validate_password } from "@/utils/validation";
const props = defineProps({ reset_token: String });

const title = ref("Reset password");
const message = ref("");
const icon = ref("bi-key");
const show_form = ref(true);

const email = ref("");
const new_password = ref("");
const new_password_message = computed(() => {
  if (
    new_password.value.length === 0 ||
    validate_password(new_password.value)
  ) {
    return "";
  } else {
    return "At least 8 characters, including lower-case, upper-case and a number.";
  }
});
const new_password2 = ref("");
const new_password2_message = computed(() => {
  if (new_password.value == new_password2.value) {
    return "";
  } else {
    return "New passwords don't match";
  }
});

function reset_password() {
  apiClient
    .post("reset_password", {
      reset_token: props.reset_token,
      email: email.value,
      new_password: new_password.value,
    })
    .then((response) => {
      console.log(response);
      message.value = response.data.message;
      icon.value = "bi-person-check";
      title.value = "Password reset successful";
      show_form.value = false;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      if (error.response != null) {
        message.value = error.response.data.message;
      } else {
        message.value = "Cannot connect to server.";
      }
      icon.value = "bi-person-exclamation";
      title.value = "Password reset failed";
      show_form.value = false;
    });
}
</script>

<template>
  <main class="flex flex-col items-center justify-center">
    <CardComponent :title="title" :icon="icon">
      <form @submit.prevent="reset_password" v-if="show_form">
        <p>
          <label for="email_current">Email address:</label>
          <input
            v-model="email"
            id="email_current"
            placeholder="your.name@uni-heidelberg.de"
            maxlength="256"
          />
        </p>
        <p>
          <label for="passwd_new">New Password:</label>
          <input
            v-model="new_password"
            id="passwd_new"
            type="password"
            placeholder="new password"
            :title="new_password_message"
            maxlength="256"
          />
          <span class="error-message pad-left">{{ new_password_message }}</span>
        </p>
        <p>
          <label for="passwd_new2">Confirm New Password:</label>
          <input
            v-model="new_password2"
            id="passwd_new2"
            type="password"
            placeholder="new password"
            :title="new_password2_message"
            maxlength="256"
          />
          <span class="error-message pad-left">{{
            new_password2_message
          }}</span>
        </p>
        <input
          type="submit"
          :title="new_password_message + ' ' + new_password2_message"
          :disabled="
            email.length === 0 ||
            new_password.length === 0 ||
            new_password2.length === 0 ||
            new_password_message.length + new_password2_message.length > 0
          "
        />
      </form>
      <div class="message">
        {{ message }}
      </div>
      <p>Go to <RouterLink to="/login">login / signup</RouterLink> page.</p>
    </CardComponent>
  </main>
</template>
