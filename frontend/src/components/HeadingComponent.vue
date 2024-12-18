<script setup lang="ts">
import { FwbJumbotron } from "flowbite-vue";
</script>

<template>
  <fwb-jumbotron
    header-text="predicTCR v2"
    header-classes="text-slate-100"
    sub-text="Prediction of tumor-reactive T cells and TCRs from scRNA-seq data."
    sub-text-classes="text-slate-300"
    class="mb-4 bg-slate-800 bg-splash bg-no-repeat bg-center bg-cover md:rounded-lg py-0 lg:py-0 pt-8 lg:pt-8"
  >
    <slot></slot>
  </fwb-jumbotron>
</template>
