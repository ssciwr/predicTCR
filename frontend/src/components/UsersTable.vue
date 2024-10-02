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
import { ref, computed } from "vue";

const props = defineProps<{
  is_runner: boolean;
}>();

const users = ref([] as User[]);
const filtered_users = computed(() => {
  return users.value.filter((user) => {
    return user.is_runner === props.is_runner;
  });
});

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
      <fwb-table-head-cell>Quota</fwb-table-head-cell>
      <fwb-table-head-cell>Last submission</fwb-table-head-cell>
      <fwb-table-head-cell>Admin</fwb-table-head-cell>
      <fwb-table-head-cell>Enable/disable</fwb-table-head-cell>
    </fwb-table-head>
    <fwb-table-body>
      <fwb-table-row
        v-for="user in filtered_users"
        :key="user.id"
        :class="user.enabled ? '!bg-slate-50' : '!bg-red-200'"
      >
        <fwb-table-cell>{{ user.id }}</fwb-table-cell>
        <fwb-table-cell>{{ user.email }}</fwb-table-cell>
        <fwb-table-cell>{{ user.activated ? "✓" : "✗" }}</fwb-table-cell>
        <fwb-table-cell>{{ user.enabled ? "✓" : "✗" }}</fwb-table-cell>
        <fwb-table-cell>{{ user.quota }}</fwb-table-cell>
        <fwb-table-cell>
          {{
            new Date(user.last_submission_timestamp * 1000).toLocaleDateString(
              "de-DE",
            )
          }}
        </fwb-table-cell>
        <fwb-table-cell>{{ user.is_admin ? "✓" : "✗" }}</fwb-table-cell>
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
