<script setup lang="ts">
// @ts-ignore
import {
  FwbA,
  FwbButton,
  FwbModal,
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
} from "flowbite-vue";
import {
  apiClient,
  download_input_csv_file,
  download_input_h5_file,
  download_result,
  download_admin_result,
  logout,
  download_string_as_file,
} from "@/utils/api-client";
import type { Sample } from "@/utils/types";
import { ref } from "vue";

const props = defineProps<{
  samples: Sample[];
  admin: boolean;
}>();

const emit = defineEmits(["samplesModified"]);

const current_sample_id = ref(null as number | null);
const show_delete_modal = ref(false);
const show_resubmit_modal = ref(false);
function close_modals() {
  show_resubmit_modal.value = false;
  show_delete_modal.value = false;
}

function resubmit_current_sample() {
  close_modals();
  apiClient
    .post(`admin/resubmit-sample/${current_sample_id.value}`)
    .then(() => {
      emit("samplesModified");
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

function delete_current_sample() {
  close_modals();
  apiClient
    .delete(`admin/samples/${current_sample_id.value}`)
    .then(() => {
      emit("samplesModified");
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

function timestamp_to_date(timestamp_secs: number): string {
  const secs_to_ms = 1000;
  return new Date(timestamp_secs * secs_to_ms).toLocaleDateString("de-DE");
}

function job_runtime(sample: Sample): string {
  // returns job runtime as hh::mm::ss
  const runtime_secs = sample.timestamp_job_end - sample.timestamp_job_start;
  const secs_to_ms = 1000;
  if (runtime_secs <= 0) {
    return "-";
  }
  return new Date(runtime_secs * secs_to_ms).toISOString().slice(11, 19);
}

function download_samples_as_csv() {
  let csv =
    "Id,Date,Email,SampleName,TumorType,Source,Platform,Status,Runtime\n";
  for (const sample of props.samples) {
    csv += `${sample.id},${timestamp_to_date(sample.timestamp)},${sample.email},${sample.name},${sample.tumor_type},${sample.source},${sample.platform},${sample.status},${job_runtime(sample)}\n`;
  }
  download_string_as_file("samples.csv", csv);
}
</script>

<template>
  <fwb-table aria-label="Samples">
    <fwb-table-head>
      <fwb-table-head-cell v-if="admin">Id</fwb-table-head-cell>
      <fwb-table-head-cell>Date</fwb-table-head-cell>
      <fwb-table-head-cell v-if="admin">Email</fwb-table-head-cell>
      <fwb-table-head-cell>Sample Name</fwb-table-head-cell>
      <fwb-table-head-cell>Tumor type</fwb-table-head-cell>
      <fwb-table-head-cell>Source</fwb-table-head-cell>
      <fwb-table-head-cell>Platform</fwb-table-head-cell>
      <fwb-table-head-cell>Status</fwb-table-head-cell>
      <fwb-table-head-cell v-if="admin">Runtime</fwb-table-head-cell>
      <fwb-table-head-cell>Inputs</fwb-table-head-cell>
      <fwb-table-head-cell>Results</fwb-table-head-cell>
      <fwb-table-head-cell>Error message</fwb-table-head-cell>
      <fwb-table-head-cell v-if="admin">Actions</fwb-table-head-cell>
    </fwb-table-head>
    <fwb-table-body>
      <fwb-table-row
        v-for="sample in samples"
        :key="sample.id"
        :class="sample.status === 'failed' ? '!bg-red-200' : '!bg-slate-50'"
      >
        <fwb-table-cell v-if="admin">{{ sample.id }}</fwb-table-cell>
        <fwb-table-cell>{{
          timestamp_to_date(sample.timestamp)
        }}</fwb-table-cell>
        <fwb-table-cell v-if="admin">{{ sample.email }}</fwb-table-cell>
        <fwb-table-cell>{{ sample.name }}</fwb-table-cell>
        <fwb-table-cell>{{ sample.tumor_type }}</fwb-table-cell>
        <fwb-table-cell>{{ sample.source }}</fwb-table-cell>
        <fwb-table-cell>{{ sample.platform }}</fwb-table-cell>
        <fwb-table-cell>{{ sample.status }}</fwb-table-cell>
        <fwb-table-cell v-if="admin">{{ job_runtime(sample) }}</fwb-table-cell>
        <fwb-table-cell>
          <fwb-a
            href=""
            @click.prevent="download_input_h5_file(sample.id, sample.name)"
          >
            h5
          </fwb-a>
          /
          <fwb-a
            href=""
            @click.prevent="download_input_csv_file(sample.id, sample.name)"
          >
            csv
          </fwb-a>
        </fwb-table-cell>
        <fwb-table-cell>
          <template v-if="admin">
            <fwb-a
              href=""
              @click.prevent="download_admin_result(sample.id, sample.name)"
              >zip</fwb-a
            >
          </template>
          <template v-else-if="sample.has_results_zip">
            <fwb-a
              href=""
              @click.prevent="download_result(sample.id, sample.name)"
              >zip</fwb-a
            >
          </template>
          <template v-else> - </template>
        </fwb-table-cell>
        <fwb-table-cell>{{ sample.error_message }}</fwb-table-cell>
        <fwb-table-cell v-if="admin">
          <fwb-button
            @click="
              current_sample_id = sample.id;
              show_resubmit_modal = true;
            "
            class="mr-2"
            >Resubmit</fwb-button
          >
          <fwb-button
            @click="
              current_sample_id = sample.id;
              show_delete_modal = true;
            "
            class="mr-2"
            color="red"
            >Delete</fwb-button
          >
        </fwb-table-cell>
      </fwb-table-row>
    </fwb-table-body>
  </fwb-table>
  <fwb-button v-if="admin" class="mt-2" @click="download_samples_as_csv"
    >Download as CSV</fwb-button
  >

  <fwb-modal size="lg" v-if="show_resubmit_modal" @close="close_modals">
    <template #header>
      <div class="flex items-center text-lg">Resubmit sample</div>
    </template>
    <template #body
      >Are you sure you want to resubmit this sample (any existing results will
      be deleted)?
    </template>
    <template #footer>
      <div class="flex justify-between">
        <fwb-button @click="close_modals" color="alternative">
          No, cancel
        </fwb-button>
        <fwb-button @click="resubmit_current_sample" color="green">
          Yes, resubmit
        </fwb-button>
      </div>
    </template>
  </fwb-modal>

  <fwb-modal size="lg" v-if="show_delete_modal" @close="close_modals">
    <template #header>
      <div class="flex items-center text-lg">Delete sample</div>
    </template>
    <template #body> Are you sure you want to delete this sample? </template>
    <template #footer>
      <div class="flex justify-between">
        <fwb-button @click="close_modals" color="alternative">
          No, cancel
        </fwb-button>
        <fwb-button @click="delete_current_sample" color="red">
          Yes, delete
        </fwb-button>
      </div>
    </template>
  </fwb-modal>
</template>
