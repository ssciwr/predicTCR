<script setup lang="ts">
// @ts-ignore
import {
  FwbA,
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
} from "flowbite-vue";
import {
  download_input_csv_file,
  download_input_h5_file,
  download_result,
} from "@/utils/api-client";
import type { Sample } from "@/utils/types";

defineProps<{
  samples: Sample[];
  admin: boolean;
}>();
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
      <fwb-table-head-cell>Status</fwb-table-head-cell>
      <fwb-table-head-cell>Inputs</fwb-table-head-cell>
      <fwb-table-head-cell>Results</fwb-table-head-cell>
    </fwb-table-head>
    <fwb-table-body>
      <fwb-table-row v-for="sample in samples" :key="sample.id">
        <fwb-table-cell v-if="admin">{{ sample["id"] }}</fwb-table-cell>
        <fwb-table-cell>{{
          new Date(sample["timestamp"] * 1000).toLocaleDateString()
        }}</fwb-table-cell>
        <fwb-table-cell v-if="admin">{{ sample["email"] }}</fwb-table-cell>
        <fwb-table-cell>{{ sample["name"] }}</fwb-table-cell>
        <fwb-table-cell>{{ sample["tumor_type"] }}</fwb-table-cell>
        <fwb-table-cell>{{ sample["source"] }}</fwb-table-cell>
        <fwb-table-cell>{{ sample["status"] }}</fwb-table-cell>
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
          <template v-if="sample.has_results_zip">
            <fwb-a
              href=""
              @click.prevent="download_result(sample.id, sample.name)"
              >zip</fwb-a
            >
          </template>
          <template v-else> - </template>
        </fwb-table-cell>
      </fwb-table-row>
    </fwb-table-body>
  </fwb-table>
</template>
