<script setup lang="ts">
import { FwbButton, FwbInput, FwbListGroupItem } from "flowbite-vue";
import { computed } from "vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();

type Item = {
  id: string;
  url: string;
  text: string;
};

const items = computed((): Array<Item> => {
  try {
    return JSON.parse(settingsStore.settings.news_items_json);
  } catch (e) {
    console.log(e);
    return [];
  }
});

function add() {
  settingsStore.settings.news_items_json = JSON.stringify(
    items.value.concat([{ id: "", url: "", text: "" }]),
  );
}

function remove(id: string) {
  settingsStore.settings.news_items_json = JSON.stringify(
    items.value.filter((item) => item.id !== id),
  );
}

function save() {
  settingsStore.settings.news_items_json = JSON.stringify(items.value);
  settingsStore.saveChanges();
}
</script>

<template>
  <div class="flex flex-col mb-2 p-2" v-if="settingsStore.settings">
    <fwb-list-group-item v-for="item in items" v-bind:key="item.id">
      <div class="flex flex-col mb-4 flex-grow mr-2">
        <fwb-input v-model="item.id" label="ID" class="mb-1" />
        <fwb-input v-model="item.url" label="URL" class="mb-1" />
        <fwb-input v-model="item.text" label="Text" class="mb-1" />
        <fwb-button
          color="red"
          class="grow-0"
          @click="
            () => {
              remove(item.id);
            }
          "
          >Delete</fwb-button
        >
      </div>
    </fwb-list-group-item>
    <fwb-list-group-item>
      <fwb-button @click="add" class="my-2 grow">Add new item</fwb-button>
    </fwb-list-group-item>
    <fwb-button @click="save" class="mt-2" color="green"> Save </fwb-button>
  </div>
</template>
