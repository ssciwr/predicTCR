<script setup lang="ts">
import { FwbButton, FwbTextarea } from "flowbite-vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();
</script>

<template>
  <div class="flex flex-col mb-2 p-2" v-if="settingsStore.settings">
    <fwb-textarea
      v-model="settingsStore.settings.about_md"
      :rows="32"
      class="mb-2"
      label="About page text (markdown)"
    ></fwb-textarea>
    <fwb-button @click="settingsStore.saveChanges" class="mt-2" color="green">
      Save
    </fwb-button>
  </div>
</template>
