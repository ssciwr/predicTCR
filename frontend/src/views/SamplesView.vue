<script setup lang="ts">
import { onUnmounted, ref } from "vue";
import SamplesTable from "@/components/SamplesTable.vue";
import ListComponent from "@/components/ListComponent.vue";
import SelectWithOther from "@/components/SelectWithOther.vue";
import ListItem from "@/components/ListItem.vue";
import { apiClient, logout } from "@/utils/api-client";
import type { Sample } from "@/utils/types";
import {
  FwbA,
  FwbAlert,
  FwbButton,
  FwbCheckbox,
  FwbFileInput,
  FwbInput,
  FwbModal,
} from "flowbite-vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();
const required_columns = ref([] as Array<string>);

function closeModalSubmit() {
  agree_to_conditions.value = false;
  showModalSubmit.value = false;
}
function openModalSubmit() {
  showModalSubmit.value = true;
}
const showModalSubmit = ref(false);
const agree_to_conditions = ref(false);

const sample_name = ref("");
const tumor_type = ref("");
const source = ref("");
const platform = ref("");
const selected_h5_file = ref(null as null | File);
const h5_file_input_key = ref(0);
const selected_csv_file = ref(null as null | File);
const csv_file_input_key = ref(0);
const new_sample_error_message = ref("");

function on_h5_file_changed(event: Event) {
  const max_upload_size_mb = settingsStore.settings.max_filesize_h5_mb;
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
    for (const required_column of required_columns.value) {
      if (!columns.includes(required_column)) {
        return false;
      }
    }
    return true;
  }
  return false;
}

async function on_csv_file_changed(event: Event) {
  const max_upload_size_mb = settingsStore.settings.max_filesize_csv_mb;
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
        `Provided csv file doesn't contain the required columns ${required_columns.value}`,
      );
    }
  } else {
    selected_csv_file.value = null;
  }
}

required_columns.value = settingsStore.settings.csv_required_columns.split(";");

const samples = ref([] as Sample[]);

function update_samples() {
  apiClient
    .get("samples")
    .then((response) => {
      samples.value = response.data;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

update_samples();

const submit_message = ref("");

let update_data_handle = setTimeout(function update_data() {
  update_samples();
  update_submit_message();
  update_data_handle = setTimeout(update_data, 20000);
});

onUnmounted(() => {
  clearTimeout(update_data_handle);
});

function update_submit_message() {
  apiClient
    .get("user_submit_message")
    .then((response) => {
      submit_message.value = response.data.message;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

update_submit_message();

function add_sample() {
  let formData = new FormData();
  formData.append("name", sample_name.value);
  formData.append("tumor_type", tumor_type.value);
  formData.append("source", source.value);
  formData.append("platform", platform.value);
  formData.append("h5_file", selected_h5_file.value as File);
  formData.append("csv_file", selected_csv_file.value as File);
  apiClient
    .post("sample", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      update_samples();
      update_submit_message();
      new_sample_error_message.value = "";
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      new_sample_error_message.value = error.response.data.message;
    });
  closeModalSubmit();
  sample_name.value = "";
  selected_h5_file.value = null;
  h5_file_input_key.value++;
  selected_csv_file.value = null;
  csv_file_input_key.value++;
}
</script>

<template>
  <main class="flex flex-col items-center justify-center">
    <ListComponent>
      <ListItem title="Submit a sample">
        <template v-if="submit_message.length > 0">
          {{ submit_message }}
        </template>
        <template v-else>
          <div class="flex flex-col mt-2">
            <fwb-input
              v-model="sample_name"
              required
              label="Sample name"
              id="sample_name"
              placeholder="pXYZ_ABC_c1"
              maxlength="128"
              class="mb-2"
            />
            <SelectWithOther
              v-model="tumor_type"
              :options="settingsStore.settings.tumor_types"
              id="tumor_type"
              label="Tumor type"
            />
            <SelectWithOther
              v-model="source"
              :options="settingsStore.settings.sources"
              id="source"
              label="Source"
            />
            <SelectWithOther
              v-model="platform"
              :options="settingsStore.settings.platforms"
              id="platform"
              label="Platform"
            />
            <fwb-file-input
              type="file"
              id="input_h5_file"
              label="H5 input file"
              name="h5 file"
              @change="on_h5_file_changed($event)"
              :key="h5_file_input_key"
              accept=".h5,.he5,.hdf5"
              title="Select the h5 file to upload"
              class="mb-2"
            />
            <fwb-file-input
              type="file"
              id="input_csv_file"
              label="CSV input file"
              name="csv file"
              @change="on_csv_file_changed($event)"
              :key="csv_file_input_key"
              accept=".csv,.txt"
              title="Select the csv file to upload"
              class="mb-2"
            />
            <fwb-button
              @click="openModalSubmit"
              :disabled="
                selected_h5_file === null ||
                selected_csv_file === null ||
                sample_name.length === 0
              "
              >Submit
            </fwb-button>
            <fwb-alert type="danger" v-if="new_sample_error_message">
              {{ new_sample_error_message }}
            </fwb-alert>
          </div>
        </template>
      </ListItem>
      <ListItem title="My samples">
        <template v-if="samples.length > 0">
          <SamplesTable
            :samples="samples"
            :admin="false"
            class="mt-2"
          ></SamplesTable>
        </template>
        <template v-else>
          <p>You don't yet have any samples.</p>
        </template>
      </ListItem>
    </ListComponent>
  </main>

  <fwb-modal size="md" v-if="showModalSubmit" @close="closeModalSubmit">
    <template #header>
      <div class="flex items-center text-lg">Conditions of use</div>
    </template>
    <template #body>
      <fwb-p>
        This service is provided for non-commercial use only, and is not to be
        used for training models.
      </fwb-p>
      <fwb-p>
        Note: predicTCR performs best on scSEQ datasets subsetted to contain
        only T cells, for more details see the
        <fwb-al href="/about" target="_blank" rel="noopener noreferrer"
          >About</fwb-al
        >
        section.
      </fwb-p>
      <fwb-checkbox
        v-model="agree_to_conditions"
        label="I agree to the conditions of use"
        class="py-4"
      />
      <fwb-button @click="add_sample" :disabled="!agree_to_conditions"
        >Submit</fwb-button
      >
    </template>
  </fwb-modal>
</template>
