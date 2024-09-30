<script setup lang="ts">
// @ts-ignore
import {
  FwbButton,
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
} from "flowbite-vue";
import type { User } from "@/utils/types";
import { apiClient, logout } from "@/utils/api-client";
import { ref } from "vue";

defineProps<{
  runner: boolean;
}>();

const users = ref([] as User[]);

function get_users() {
  apiClient
    .get("admin/users")
    .then((response) => {
      users.value = response.data.users;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

get_users();

function enable_user(user_email: string) {
  apiClient
    .post("admin/enable_user", { user_email: user_email })
    .then(() => {
      get_users();
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

function disable_user(user_email: string) {
  apiClient
    .post("admin/disable_user", { user_email: user_email })
    .then(() => {
      get_users();
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}
</script>

<template>
  <fwb-table aria-label="Registered users">
    <fwb-table-head>
      <fwb-table-head-cell>Id</fwb-table-head-cell>
      <fwb-table-head-cell>Email</fwb-table-head-cell>
      <fwb-table-head-cell>Activated</fwb-table-head-cell>
      <fwb-table-head-cell>Enabled</fwb-table-head-cell>
      <fwb-table-head-cell>Remaining quota</fwb-table-head-cell>
      <fwb-table-head-cell>Last submission</fwb-table-head-cell>
      <fwb-table-head-cell>Admin</fwb-table-head-cell>
      <fwb-table-head-cell>Runner</fwb-table-head-cell>
      <fwb-table-head-cell>Enable/disable</fwb-table-head-cell>
    </fwb-table-head>
    <fwb-table-body>
      <fwb-table-row
        v-for="user in users"
        :key="user.id"
        :class="{ disabled: !user.enabled }"
      >
        <fwb-table-cell>{{ user.id }}</fwb-table-cell>
        <fwb-table-cell>{{ user.email }}</fwb-table-cell>
        <fwb-table-cell>{{ user.activated }}</fwb-table-cell>
        <fwb-table-cell>{{ user.enabled }}</fwb-table-cell>
        <fwb-table-cell>{{ user.quota }}</fwb-table-cell>
        <fwb-table-cell>
          {{
            new Date(user.last_submission_timestamp * 1000).toLocaleDateString(
              "de-DE",
            )
          }}
        </fwb-table-cell>
        <fwb-table-cell>{{ user.is_admin }}</fwb-table-cell>
        <fwb-table-cell>{{ user.is_runner }}</fwb-table-cell>
        <fwb-table-cell>
          <template v-if="user.enabled">
            <fwb-button @click="disable_user(user.email)" color="red"
              >Disable</fwb-button
            >
          </template>
          <template v-else>
            <fwb-button @click="enable_user(user.email)" color="green"
              >Enable</fwb-button
            >
          </template>
        </fwb-table-cell>
      </fwb-table-row>
    </fwb-table-body>
  </fwb-table>
</template>
