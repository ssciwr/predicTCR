<script setup lang="ts">
import { FwbButton, FwbInput, FwbRange } from "flowbite-vue";
import { ref } from "vue";
import { apiClient, logout } from "@/utils/api-client";
import type { Settings } from "@/utils/types";

const settings = ref(null as Settings | null);

function get_settings() {
  apiClient
    .get("/settings")
    .then((response) => {
      settings.value = response.data;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

get_settings();

function update_settings() {
  apiClient
    .post("admin/settings", settings.value)
    .then(() => {
      get_settings();
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
  <div class="flex flex-col m-2 p-2" v-if="settings">
    <fwb-range
      v-model="settings.default_personal_submission_quota"
      :steps="1"
      :min="0"
      :max="99"
      :label="`Default personal quota: ${settings.default_personal_submission_quota}`"
      class="mb-2"
    />
    <fwb-range
      v-model="settings.default_personal_submission_interval_mins"
      :steps="1"
      :min="0"
      :max="60"
      :label="`Default interval between submissions: ${settings.default_personal_submission_interval_mins} minutes`"
      class="mb-2"
    />
    <fwb-range
      v-model="settings.global_quota"
      :steps="1"
      :min="0"
      :max="9999"
      :label="`Remaining global quota: ${settings.global_quota}`"
      class="mb-2"
    />
    <fwb-input
      v-model="settings.tumor_types"
      class="mb-2"
      label="Tumor types (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settings.sources"
      class="mb-2"
      label="Sources (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settings.csv_required_columns"
      class="mb-2"
      label="Required columns in CSV file (separated by ;)"
    ></fwb-input>
    <fwb-button @click="update_settings" color="green">
      Save settings</fwb-button
    >
  </div>
</template>
