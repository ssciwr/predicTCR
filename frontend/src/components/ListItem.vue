<script setup lang="ts">
import {
  FwbTimelineBody,
  FwbTimelineContent,
  FwbTimelineItem,
  FwbTimelinePoint,
  FwbTimelineTitle,
} from "flowbite-vue";

defineProps({
  title: String,
});
</script>

<template>
  <fwb-timeline-item>
    <fwb-timeline-point>
      <img src="/logo.png" alt="predicTCR" />
    </fwb-timeline-point>
    <fwb-timeline-content>
      <fwb-timeline-title>{{ title }}</fwb-timeline-title>
      <fwb-timeline-body>
        <slot></slot>
      </fwb-timeline-body>
    </fwb-timeline-content>
  </fwb-timeline-item>
</template>
