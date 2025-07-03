<script setup lang="ts">
import { FwbButton, FwbInput, FwbRange } from "flowbite-vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();
</script>

<template>
  <div class="flex flex-col space-y-4 m-2 p-2" v-if="settingsStore.settings">
    <fwb-range
      v-model="settingsStore.settings.default_personal_submission_quota"
      :steps="1"
      :min="0"
      :max="99"
      :label="`Default personal quota: ${settingsStore.settings.default_personal_submission_quota}`"
    />
    <fwb-range
      v-model="settingsStore.settings.default_personal_submission_interval_mins"
      :steps="1"
      :min="0"
      :max="60"
      :label="`Default interval between submissions: ${settingsStore.settings.default_personal_submission_interval_mins} minutes`"
    />
    <fwb-range
      v-model="settingsStore.settings.global_quota"
      :steps="1"
      :min="0"
      :max="9999"
      :label="`Remaining global quota: ${settingsStore.settings.global_quota}`"
    />
    <fwb-input
      v-model="settingsStore.settings.tumor_types"
      label="Tumor types (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settingsStore.settings.sources"
      label="Sources (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settingsStore.settings.platforms"
      label="Platforms (separated by ;)"
    ></fwb-input>
    <fwb-input
      v-model="settingsStore.settings.csv_required_columns"
      label="Required columns in CSV file (separated by ;)"
    ></fwb-input>
    <fwb-range
      v-model="settingsStore.settings.runner_job_timeout_mins"
      :steps="1"
      :min="1"
      :max="360"
      :label="`Timeout for runner jobs: ${settingsStore.settings.runner_job_timeout_mins} minutes`"
    />
    <fwb-range
      v-model="settingsStore.settings.max_filesize_h5_mb"
      :steps="1"
      :min="1"
      :max="100"
      :label="`Max h5 upload filesize: ${settingsStore.settings.max_filesize_h5_mb}mb`"
    />
    <fwb-range
      v-model="settingsStore.settings.max_filesize_csv_mb"
      :steps="1"
      :min="1"
      :max="100"
      :label="`Max csv upload filesize: ${settingsStore.settings.max_filesize_csv_mb}mb`"
    />
    <fwb-button @click="settingsStore.saveChanges" class="mt-4" color="green">
      Save settings
    </fwb-button>
  </div>
</template>
