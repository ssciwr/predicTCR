<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { FwbSelect, FwbInput } from "flowbite-vue";
const model = defineModel();
const otherText = "Other (please specify)";
const textInput = ref("");
const selectInput = ref("");
const showTextInput = ref(true);

type OptionsType = {
  name: string;
  value: string;
};

watch([selectInput, textInput], ([newSelectInput, newTextInput]) => {
  if (newSelectInput === otherText) {
    showTextInput.value = true;
    model.value = newTextInput;
  } else {
    showTextInput.value = false;
    textInput.value = "";
    model.value = newSelectInput;
  }
});

function string_to_options(str: string): Array<OptionsType> {
  const items = `${str};${otherText}`.split(";");
  return items.map((x) => ({ value: x, name: x }));
}

const props = defineProps({
  options: String,
  id: String,
  label: String,
});

const optionsArray = computed(() => {
  if (!props.options) {
    return [];
  }
  return string_to_options(props.options);
});
</script>

<template>
  <div class="flex flex-row mb-2">
    <fwb-select
      v-model="selectInput"
      :options="optionsArray"
      :id="id"
      :label="label"
      class="grow"
    />
    <fwb-input
      v-if="showTextInput"
      v-model="textInput"
      label="Other"
      class="ml-2 grow"
    />
  </div>
</template>
