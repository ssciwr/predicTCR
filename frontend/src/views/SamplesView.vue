<script setup lang="ts">
import { computed, ref } from "vue";
import ListItem from "@/components/ListItem.vue";
import SamplesTable from "@/components/SamplesTable.vue";
import { apiClient, logout } from "@/utils/api-client";
import { validate_sample_name } from "@/utils/validation";
import type { Sample, RunningOptions } from "@/utils/types";

const new_sample_name = ref("");
const new_sample_concentration = ref(200);
const new_sample_concentration_min = ref(143);
const new_sample_concentration_max = ref(1000);
const selected_files = ref(null as null | FileList);
const file_input_key = ref(0);
const new_sample_error_message = ref("");

function on_file_changed(event: Event) {
  const max_upload_size_mb = 4;
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

function duplicate_sample_name(sample_name: string) {
  return current_samples.value.some((e) => e.name === sample_name);
}

const new_sample_name_message = computed(() => {
  if (duplicate_sample_name(new_sample_name.value)) {
    return "Sample name already used";
  } else if (!validate_sample_name(new_sample_name.value)) {
    return "Only alphanumeric characters and underscores allowed";
  } else {
    return "";
  }
});

const new_sample_concentration_message = computed(() => {
  if (new_sample_concentration.value < new_sample_concentration_min.value) {
    return `Minimum sample concentration: ${new_sample_concentration_min.value} ng/μl`;
  } else if (
    new_sample_concentration.value > new_sample_concentration_max.value
  ) {
    return `Maximum sample concentration: ${new_sample_concentration_max.value} ng/μl`;
  } else {
    return "";
  }
});

const remaining = ref(0);
const remaining_message = ref("");

function update_remaining() {
  apiClient
    .get("remaining")
    .then((response) => {
      remaining.value = response.data.remaining;
      remaining_message.value = response.data.message;
    })
    .catch((error) => {
      console.log(error);
      remaining_message.value = "Error: could not connect to server";
    });
}

update_remaining();

const current_samples = ref([] as Sample[]);
const previous_samples = ref([] as Sample[]);

apiClient
  .get("samples")
  .then((response) => {
    current_samples.value = response.data.current_samples;
    previous_samples.value = response.data.previous_samples;
  })
  .catch((error) => {
    if (error.response.status > 400) {
      logout();
    }
    console.log(error);
  });

const running_options = ref([] as RunningOptions);
const new_running_option = ref("");

apiClient
  .get("running_options")
  .then((response) => {
    running_options.value = response.data.running_options;
    if (running_options.value.length > 0) {
      new_running_option.value = running_options.value[0];
    }
  })
  .catch((error) => {
    if (error.response.status > 400) {
      logout();
    }
    console.log(error);
  });

function add_sample() {
  let formData = new FormData();
  formData.append("name", new_sample_name.value);
  formData.append("running_option", new_running_option.value);
  formData.append("concentration", String(new_sample_concentration.value));
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
      current_samples.value.push(response.data.sample);
      new_sample_error_message.value = "";
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      new_sample_error_message.value = error.response.data.message;
    });
  update_remaining();
  new_sample_name.value = "";
  selected_files.value = null;
  file_input_key.value++;
}
</script>

<template>
  <main>
    <ListItem title="My samples" icon="bi-clipboard-data">
      <template v-if="current_samples.length > 0">
        <p>Your samples for this week:</p>
        <SamplesTable
          :samples="current_samples"
          :admin="false"
          :resubmit_button="false"
        ></SamplesTable>
      </template>
      <template v-else>
        <p>You don't have any samples this week.</p>
      </template>
    </ListItem>
    <ListItem title="Submit a sample" icon="bi-clipboard-plus">
      <template v-if="remaining > 0">
        <p>
          To submit a new sample, enter a sample name, and optionally upload any
          reference sequence files:
        </p>
        <form @submit.prevent="add_sample">
          <p>
            <label for="sample_name">Sample name:</label>
            <input
              v-model="new_sample_name"
              id="sample_name"
              placeholder="pXYZ_ABC_c1"
              maxlength="128"
              :title="new_sample_name_message"
            />
            <span class="error-message pad-left">
              <template v-if="new_sample_name">
                {{ new_sample_name_message }}
              </template>
            </span>
          </p>
          <p v-if="running_options.length > 2">
            <label for="running_option">Running option:</label>
            <select v-model="new_running_option" id="running_option">
              <option v-for="running_option in running_options">
                {{ running_option }}
              </option>
            </select>
          </p>
          <p>
            <label for="conc">Concentration (ng/μl):</label>
            <input
              v-model="new_sample_concentration"
              id="conc"
              type="number"
              :min="new_sample_concentration_min"
              :max="new_sample_concentration_max"
              placeholder="ng/μl"
              :title="new_sample_concentration_message"
            />
            <span class="error-message pad-left">
              {{ new_sample_concentration_message }}
            </span>
          </p>
          <p>
            <label for="ref_seq_file">Reference sequence (optional):</label>
            <input
              type="file"
              id="ref_seq_file"
              name="file"
              :multiple="true"
              @change="on_file_changed($event)"
              :key="file_input_key"
              title="Optionally upload a fasta file reference sequence"
            />
          </p>
          <p>
            <input
              type="submit"
              :disabled="
                new_sample_name_message.length +
                  new_sample_concentration_message.length >
                0
              "
              :title="
                new_sample_name_message +
                '\n' +
                new_sample_concentration_message
              "
            />
          </p>
          <div class="error-message">
            <template v-if="new_sample_error_message">
              {{ new_sample_error_message }}
            </template>
          </div>
        </form>
      </template>
      <template v-else>
        <p>
          {{ remaining_message }}
        </p>
        <p>
          Please try again on Monday, or email
          <a href="mailto:e.green@dkfz.de?subject=circuitSEQ"
            >e.green@dkfz.de</a
          >
          with urgent requests.
        </p>
      </template>
    </ListItem>
    <ListItem title="Results" icon="bi-clipboard-data">
      <template v-if="previous_samples.length > 0">
        <p>Results from your previous samples:</p>
        <SamplesTable
          :samples="previous_samples"
          :admin="false"
          :resubmit_button="false"
        ></SamplesTable>
      </template>
      <template v-else>
        <p>No previous samples.</p>
      </template>
    </ListItem>
  </main>
</template>
