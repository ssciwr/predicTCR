<script setup lang="ts">
import { ref, computed } from "vue";
import { apiClient, logout } from "@/utils/api-client";
import { validate_password } from "@/utils/validation";
import { useUserStore } from "@/stores/user";
import CardComponent from "@/components/CardComponent.vue";
import { FwbInput, FwbButton, FwbAlert } from "flowbite-vue";
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
  <CardComponent title="My account">
    <p>You are currently logged in as {{ current_email }}</p>
    <p>
      <fwb-button
        class="my-2"
        @click="
          userStore.user = null;
          userStore.token = '';
        "
      >
        Logout
      </fwb-button>
    </p>
  </CardComponent>
  <CardComponent title="Change password">
    <fwb-input
      v-model="current_password"
      label="Current password"
      required
      id="account_passwd_old"
      type="password"
      placeholder="current password"
      maxlength="256"
      autocomplete="current-password"
      class="mb-2"
    />
    <fwb-input
      v-model="new_password"
      label="New password"
      required
      id="account_passwd_new"
      type="password"
      placeholder="new password"
      :title="new_password_message"
      maxlength="256"
      class="mb-2"
    />
    <fwb-alert
      type="danger"
      v-if="new_password_message.length > 0"
      class="mb-2"
    >
      {{ new_password_message }}
    </fwb-alert>
    <fwb-input
      v-model="new_password2"
      label="Confirm new password"
      required
      id="account_passwd_new2"
      type="password"
      placeholder="new password"
      :title="new_password2_message"
      maxlength="256"
      class="mb-2"
    />
    <fwb-alert
      type="danger"
      v-if="new_password2_message.length > 0"
      class="mb-2"
    >
      {{ new_password2_message }}
    </fwb-alert>
    <fwb-button
      @click="do_change_password"
      :title="new_password_message + ' ' + new_password2_message"
      class="mb-2"
      :disabled="
        current_password.length === 0 ||
        new_password.length === 0 ||
        new_password2.length === 0 ||
        new_password_message.length + new_password2_message.length > 0
      "
      >Submit</fwb-button
    >
    <fwb-alert type="info" v-if="response_message.length > 0">
      {{ response_message }}
    </fwb-alert>
  </CardComponent>
</template>
