<script setup lang="ts">
import { FwbButton, FwbInput, FwbRange } from "flowbite-vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();
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
      v-model="settingsStore.settings.platforms"
      class="mb-2"
      label="Platforms (separated by ;)"
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
    <fwb-range
      v-model="settingsStore.settings.max_filesize_h5_mb"
      :steps="1"
      :min="1"
      :max="100"
      :label="`Max h5 upload filesize: ${settingsStore.settings.max_filesize_h5_mb}mb`"
      class="mb-2"
    />
    <fwb-range
      v-model="settingsStore.settings.max_filesize_csv_mb"
      :steps="1"
      :min="1"
      :max="100"
      :label="`Max csv upload filesize: ${settingsStore.settings.max_filesize_csv_mb}mb`"
      class="mb-2"
    />
    <fwb-button @click="settingsStore.saveChanges" class="mt-2" color="green">
      Save settings
    </fwb-button>
  </div>
</template>
