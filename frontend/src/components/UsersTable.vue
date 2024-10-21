<script setup lang="ts">
import {
  FwbButton,
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
  FwbModal,
  FwbCheckbox,
  FwbRange,
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
const current_user = ref(null as User | null);

const show_modal = ref(false);
function close_modal() {
  show_modal.value = false;
  get_users();
}

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

function update_user() {
  show_modal.value = false;
  apiClient
    .post("admin/user", current_user.value)
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
      <fwb-table-head-cell>Full results</fwb-table-head-cell>
      <fwb-table-head-cell>Quota</fwb-table-head-cell>
      <fwb-table-head-cell>Delay (mins)</fwb-table-head-cell>
      <fwb-table-head-cell>Admin</fwb-table-head-cell>
      <fwb-table-head-cell>Actions</fwb-table-head-cell>
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
        <fwb-table-cell>{{ user.full_results ? "✓" : "✗" }}</fwb-table-cell>
        <fwb-table-cell>{{ user.quota }}</fwb-table-cell>
        <fwb-table-cell>{{ user.submission_interval_minutes }}</fwb-table-cell>
        <fwb-table-cell>{{ user.is_admin ? "✓" : "✗" }}</fwb-table-cell>
        <fwb-table-cell>
          <fwb-button
            @click="
              current_user = user;
              show_modal = true;
            "
            class="mr-2"
            >Edit</fwb-button
          >
          <fwb-button
            @click="
              current_user = user;
              current_user.enabled = !current_user.enabled;
              update_user();
            "
            :color="user.enabled ? 'red' : 'green'"
            >{{ user.enabled ? "Disable" : "Enable" }}</fwb-button
          >
        </fwb-table-cell>
      </fwb-table-row>
    </fwb-table-body>
  </fwb-table>

  <fwb-modal size="lg" v-if="show_modal" @close="close_modal">
    <template #header>
      <div class="flex items-center text-lg">
        Edit {{ current_user?.email }}
      </div>
    </template>
    <template v-if="current_user" #body>
      <div class="flex flex-col m-2 p-2">
        <fwb-checkbox
          v-model="current_user.activated"
          label="Email address activated"
          class="mb-2"
        />
        <fwb-checkbox
          v-model="current_user.enabled"
          label="Account enabled"
          class="mb-2"
        />
        <fwb-checkbox
          v-model="current_user.full_results"
          label="Full results access"
          class="mb-2"
        />
        <fwb-range
          v-model="current_user.quota"
          :steps="1"
          :min="0"
          :max="99"
          :label="`Remaining quota: ${current_user.quota}`"
          class="mb-2"
        />
        <fwb-range
          v-model="current_user.submission_interval_minutes"
          :steps="1"
          :min="0"
          :max="60"
          :label="`Interval between submissions: ${current_user.submission_interval_minutes} minutes`"
          class="mb-2"
        />
      </div>
    </template>
    <template #footer>
      <div class="flex justify-between">
        <fwb-button @click="close_modal" color="alternative">
          Cancel
        </fwb-button>
        <fwb-button @click="update_user" color="green"> Save </fwb-button>
      </div>
    </template>
  </fwb-modal>
</template>
