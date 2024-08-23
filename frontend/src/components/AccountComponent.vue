<script setup lang="ts">
import { ref, computed } from "vue";
import { apiClient, logout } from "@/utils/api-client";
import { validate_password } from "@/utils/validation";
import { useUserStore } from "@/stores/user";
import ListItem from "@/components/ListItem.vue";
const userStore = useUserStore();
const current_email = ref("");
if (userStore.user) {
  current_email.value = userStore.user.email;
}
const current_password = ref("");
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
const response_message = ref("");

function do_change_password() {
  apiClient
    .post("change_password", {
      current_password: current_password.value,
      new_password: new_password.value,
    })
    .then((response) => {
      response_message.value = response.data.message;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      response_message.value = error.response.data.message;
    });
}
</script>

<template v-if="userStore.user != null">
  <ListItem title="My account" icon="bi-person">
    <p>You are currently logged in as:</p>
    <p class="purple">{{ current_email }}</p>
    <p>
      <button
        @click="
          userStore.user = null;
          userStore.token = '';
        "
      >
        Logout
      </button>
    </p>
  </ListItem>
  <ListItem title="Change password" icon="bi-key">
    <form @submit.prevent="do_change_password">
      <p>
        <label for="account_passwd_old">Current Password:</label>
        <input
          v-model="current_password"
          id="account_passwd_old"
          type="password"
          placeholder="current password"
          maxlength="256"
        />
      </p>
      <p>
        <label for="account_passwd_new">New Password:</label>
        <input
          v-model="new_password"
          id="account_passwd_new"
          type="password"
          placeholder="new password"
          :title="new_password_message"
          maxlength="256"
        />
        <span class="error-message pad-left">{{ new_password_message }}</span>
      </p>
      <p>
        <label for="account_passwd_new2">Confirm New Password:</label>
        <input
          v-model="new_password2"
          id="account_passwd_new2"
          type="password"
          placeholder="new password"
          :title="new_password2_message"
          maxlength="256"
        />
        <span class="error-message pad-left">{{ new_password2_message }}</span>
      </p>
      <input
        type="submit"
        :title="new_password_message + ' ' + new_password2_message"
        :disabled="
          current_password.length === 0 ||
          new_password.length === 0 ||
          new_password2.length === 0 ||
          new_password_message.length + new_password2_message.length > 0
        "
      />
    </form>
    <div class="message">
      {{ response_message }}
    </div>
  </ListItem>
</template>
