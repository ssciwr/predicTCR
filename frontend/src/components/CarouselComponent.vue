<script setup lang="ts">
import { computed } from "vue";
import { VueperSlides, VueperSlide } from "vueperslides";
import "vueperslides/dist/vueperslides.css";
import { useSettingsStore } from "@/stores/settings";
const settingsStore = useSettingsStore();

const items = computed(() => {
  try {
    return JSON.parse(settingsStore.settings.news_items_json);
  } catch {
    return [];
  }
});
</script>

<template>
  <vueper-slides
    autoplay
    duration="3000"
    fixed-height="130px"
    :touchable="false"
  >
    <vueper-slide v-for="item in items" v-bind:key="item.id">
      <template #content>
        <div
          class="h-full mx-14 flex flex-col justify-center text-slate-300 pb-4"
        >
          <a :href="item.url" target="_blank">{{ item.text }}</a>
        </div>
      </template>
    </vueper-slide>
  </vueper-slides>
</template>
