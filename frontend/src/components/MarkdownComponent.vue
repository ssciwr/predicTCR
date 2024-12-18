<script setup lang="ts">
import showdown from "showdown";
import { computed } from "vue";

const props = defineProps({
  markdown: {
    type: String,
    required: true,
  },
});

const markdownConverter = new showdown.Converter();
const convertedHtml = computed(() =>
  markdownConverter.makeHtml(props.markdown),
);
</script>

<template>
  <article class="markdown-body">
    <div v-html="convertedHtml"></div>
  </article>
</template>
