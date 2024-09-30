<script setup lang="ts">
import { ref } from "vue";
import ListItem from "@/components/ListItem.vue";
import SamplesTable from "@/components/SamplesTable.vue";
import { apiClient, logout } from "@/utils/api-client";
import type { Sample } from "@/utils/types";

const tumor_types = ["lung", "breast", "other"];
const sources = ["TIL", "PBMC", "other"];
const required_columns = ["barcode", "cdr3", "chain"];

const sample_name = ref("");
const tumor_type = ref("lung");
const source = ref("TIL");
const selected_h5_file = ref(null as null | File);
const h5_file_input_key = ref(0);
const selected_csv_file = ref(null as null | File);
const csv_file_input_key = ref(0);
const new_sample_error_message = ref("");

function on_h5_file_changed(event: Event) {
  const max_upload_size_mb = 50;
  const target = event.target as HTMLInputElement;
  if (target.files != null && target.files.length > 0) {
    selected_h5_file.value = target.files[0];
    if (selected_h5_file.value.size > 1024 * 1024 * max_upload_size_mb) {
      selected_h5_file.value = null;
      h5_file_input_key.value++;
      window.alert(
        `Provided h5 file exceeds maximum allowed upload size of ${max_upload_size_mb}MB`,
      );
    }
  } else {
    selected_h5_file.value = null;
  }
}

async function validate_csv_file(file: File) {
  const blob = file as Blob;
  const text = await blob.text();
  const lines = text.split(/\n/);
  if (lines.length >= 1) {
    const columns = lines[0].split(/,/);
    console.log(columns);
    for (const required_column of required_columns) {
      if (!columns.includes(required_column)) {
        console.log(`Missing header: ${required_column}`);
        return false;
      }
    }
    return true;
  }
  return false;
}

async function on_csv_file_changed(event: Event) {
  const max_upload_size_mb = 10;
  const target = event.target as HTMLInputElement;
  if (target.files != null && target.files.length > 0) {
    selected_csv_file.value = target.files[0];
    if (selected_csv_file.value.size > 1024 * 1024 * max_upload_size_mb) {
      selected_csv_file.value = null;
      csv_file_input_key.value++;
      window.alert(
        `Provided csv file exceeds maximum allowed upload size of ${max_upload_size_mb}MB`,
      );
    } else if (!(await validate_csv_file(selected_csv_file.value as File))) {
      selected_csv_file.value = null;
      csv_file_input_key.value++;
      window.alert(
        `Provided csv file doesn't contain the required columns ${required_columns}`,
      );
    }
  } else {
    selected_csv_file.value = null;
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
  formData.append("h5_file", selected_h5_file.value as File);
  formData.append("csv_file", selected_csv_file.value as File);
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
  selected_h5_file.value = null;
  h5_file_input_key.value++;
  selected_csv_file.value = null;
  csv_file_input_key.value++;
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
          <label for="input_h5_file">H5 input file:</label>
          <input
            type="file"
            id="input_h5_file"
            name="h5 file"
            :multiple="false"
            @change="on_h5_file_changed($event)"
            :key="h5_file_input_key"
            accept=".h5,.he5,.hdf5"
            title="Select the h5 file to upload"
          />
        </p>
        <p>
          <label for="input_csv_file">CSV input file:</label>
          <input
            type="file"
            id="input_csv_file"
            name="csv file"
            :multiple="false"
            @change="on_csv_file_changed($event)"
            :key="csv_file_input_key"
            accept=".csv,.txt"
            title="Select the csv file to upload"
          />
        </p>
        <p>
          <input
            type="submit"
            :disabled="
              selected_h5_file === null ||
              selected_csv_file === null ||
              sample_name.length === 0
            "
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
