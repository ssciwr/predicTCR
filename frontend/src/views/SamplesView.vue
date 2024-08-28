<script setup lang="ts">
import { ref } from "vue";
import ListItem from "@/components/ListItem.vue";
import SamplesTable from "@/components/SamplesTable.vue";
import { apiClient, logout } from "@/utils/api-client";
import type { Sample } from "@/utils/types";

const tumor_types = ["lung", "breast", "other"];
const sources = ["TIL", "PBMC", "other"];

const sample_name = ref("");
const tumor_type = ref("lung");
const source = ref("TIL");
const selected_files = ref(null as null | FileList);
const file_input_key = ref(0);
const new_sample_error_message = ref("");

function on_file_changed(event: Event) {
  const max_upload_size_mb = 20;
  let total_upload_size_bytes = 0;
  const target = event.target as HTMLInputElement;
  if (target.files != null && target.files.length > 0) {
    selected_files.value = target.files;
    for (const selected_file of target.files) {
      total_upload_size_bytes += selected_file.size;
    }
    if (total_upload_size_bytes > 1024 * 1024 * max_upload_size_mb) {
      selected_files.value = null;
      file_input_key.value++;
      window.alert(
        `Selected files exceed maximum upload size of ${max_upload_size_mb}MB`,
      );
    }
  } else {
    selected_files.value = null;
  }
}

const samples = ref([] as Sample[]);

apiClient
  .get("samples")
  .then((response) => {
    samples.value = response.data;
    console.log(samples.value);
  })
  .catch((error) => {
    if (error.response.status > 400) {
      logout();
    }
    console.log(error);
  });

function add_sample() {
  let formData = new FormData();
  formData.append("name", sample_name.value);
  formData.append("tumor_type", tumor_type.value);
  formData.append("source", source.value);
  if (selected_files.value !== null) {
    for (const file of selected_files.value) {
      formData.append("file", file);
    }
  }
  apiClient
    .post("sample", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      samples.value.push(response.data.sample);
      new_sample_error_message.value = "";
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      new_sample_error_message.value = error.response.data.message;
    });
  sample_name.value = "";
  selected_files.value = null;
  file_input_key.value++;
}
</script>

<template>
  <main>
    <ListItem title="Submit a sample" icon="bi-clipboard-plus">
      <p>To submit a new sample:</p>
      <form @submit.prevent="add_sample">
        <p>
          <label for="sample_name">Sample name:</label>
          <input
            v-model="sample_name"
            id="sample_name"
            placeholder="pXYZ_ABC_c1"
            maxlength="128"
          />
        </p>
        <p>
          <label for="tumor_type">Tumor type:</label>
          <select v-model="tumor_type" id="tumor_type">
            <option v-for="tumor_type in tumor_types">
              {{ tumor_type }}
            </option>
          </select>
        </p>
        <p>
          <label for="source">Source:</label>
          <select v-model="source" id="source">
            <option v-for="source in sources">
              {{ source }}
            </option>
          </select>
        </p>
        <p>
          <label for="input_file">Input file:</label>
          <input
            type="file"
            id="input_file"
            name="file"
            :multiple="true"
            @change="on_file_changed($event)"
            :key="file_input_key"
            title="Upload the input file"
          />
        </p>
        <p>
          <input
            type="submit"
            :disabled="selected_files === null || sample_name.length === 0"
          />
        </p>
        <div class="error-message">
          <template v-if="new_sample_error_message">
            {{ new_sample_error_message }}
          </template>
        </div>
      </form>
    </ListItem>
    <ListItem title="My samples" icon="bi-clipboard-data">
      <template v-if="samples.length > 0">
        <p>Your samples:</p>
        <SamplesTable :samples="samples" :admin="false"></SamplesTable>
      </template>
      <template v-else>
        <p>You don't yet have any samples.</p>
      </template>
    </ListItem>
  </main>
</template>
