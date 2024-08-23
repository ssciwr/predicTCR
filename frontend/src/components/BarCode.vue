<script setup lang="ts">
import JsBarcode from "jsbarcode";
import { ref, onMounted } from "vue";
const props = defineProps({
  value: { type: String, required: true },
});
const barcode = ref(null);
onMounted(() => {
  JsBarcode(barcode.value, props.value, {
    height: 32,
    fontSize: 14,
    background: "rgba(0,0,0,0)",
  });
});
</script>

<template>
  <svg ref="barcode"></svg>
</template>
