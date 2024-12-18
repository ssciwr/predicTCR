<script setup lang="ts">
import { useSettingsStore } from "@/stores/settings";
import HeadingComponent from "@/components/HeadingComponent.vue";
import MarkdownComponent from "@/components/MarkdownComponent.vue";

const settingsStore = useSettingsStore();
</script>

<template>
  <main class="flex flex-col items-center justify-center">
    <HeadingComponent />
    <MarkdownComponent :markdown="settingsStore.settings.about_md" />
  </main>
</template>
