<script setup lang="ts">
import { FwbButton, FwbInput, FwbRange, FwbTextarea } from "flowbite-vue";
import { useSettingsStore } from "@/stores/settings";
import { apiClient, logout } from "@/utils/api-client";
const settingsStore = useSettingsStore();
settingsStore.refresh();

function update_settings() {
  apiClient
    .post("admin/settings", settingsStore.settings)
    .then(() => {
      console.log("Settings updated");
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
  <div class="flex flex-col m-2 p-2" v-if="settingsStore.settings">
    <fwb-range
      v-model="settingsStore.settings.default_personal_submission_quota"
      :steps="1"
      :min="0"
      :max="99"
      :label="`Default personal quota: ${settingsStore.settings.default_personal_submission_quota}`"
      class="mb-2"
    />
    <fwb-range
      v-model="settingsStore.settings.default_personal_submission_interval_mins"
      :steps="1"
      :min="0"
      :max="60"
      :label="`Default interval between submissions: ${settingsStore.settings.default_personal_submission_interval_mins} minutes`"
      class="mb-2"
    />
    <fwb-range
      v-model="settingsStore.settings.global_quota"
      :steps="1"
      :min="0"
      :max="9999"
      :label="`Remaining global quota: ${settingsStore.settings.global_quota}`"
      class="mb-2"
    />
    <fwb-input
      v-model="settingsStore.settings.tumor_types"
      class="mb-2"
      label="Tumor types (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settingsStore.settings.sources"
      class="mb-2"
      label="Sources (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settingsStore.settings.csv_required_columns"
      class="mb-2"
      label="Required columns in CSV file (separated by ;)"
    ></fwb-input>
    <fwb-range
      v-model="settingsStore.settings.runner_job_timeout_mins"
      :steps="1"
      :min="1"
      :max="360"
      :label="`Timeout for runner jobs: ${settingsStore.settings.runner_job_timeout_mins} minutes`"
      class="mb-2"
    />
    <fwb-textarea
      v-model="settingsStore.settings.about_md"
      :rows="32"
      class="mb-2"
      label="About page text (markdown)"
    ></fwb-textarea>
    <fwb-button @click="update_settings" class="mt-2" color="green">
      Save settings</fwb-button
    >
  </div>
</template>
