<script setup lang="ts">
import { FwbCard } from "flowbite-vue";

defineProps({
  title: String,
  img: String,
});
</script>

<template>
  <div class="flex mb-4 justify-center !max-w-full">
    <fwb-card :img-src="img" variant="horizontal" href="">
      <div class="p-5">
        <h5
          class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white"
        >
          {{ title }}
        </h5>
        <div
          class="flex flex-col space-y-4 font-normal text-gray-700 dark:text-gray-400"
        >
          <slot></slot>
        </div>
      </div>
    </fwb-card>
  </div>
</template>
