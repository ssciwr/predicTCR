<script setup lang="ts">
import {
  FwbTable,
  FwbTableBody,
  FwbTableCell,
  FwbTableHead,
  FwbTableHeadCell,
  FwbTableRow,
} from "flowbite-vue";
import type { Job } from "@/utils/types";
import { apiClient, logout } from "@/utils/api-client";
import { ref } from "vue";

const jobs = ref([] as Job[]);

function get_jobs() {
  apiClient
    .get("admin/jobs")
    .then((response) => {
      jobs.value = response.data.jobs;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

get_jobs();
</script>

<template>
  <fwb-table aria-label="Runner jobs">
    <fwb-table-head>
      <fwb-table-head-cell>Id</fwb-table-head-cell>
      <fwb-table-head-cell>SampleId</fwb-table-head-cell>
      <fwb-table-head-cell>Start</fwb-table-head-cell>
      <fwb-table-head-cell>Runtime</fwb-table-head-cell>
      <fwb-table-head-cell>Status</fwb-table-head-cell>
      <fwb-table-head-cell>Error message</fwb-table-head-cell>
    </fwb-table-head>
    <fwb-table-body>
      <fwb-table-row
        v-for="job in jobs"
        :key="job.id"
        :class="job.status !== 'failed' ? '!bg-slate-50' : '!bg-red-200'"
      >
        <fwb-table-cell>{{ job.id }}</fwb-table-cell>
        <fwb-table-cell>{{ job.sample_id }}</fwb-table-cell>
        <fwb-table-cell>{{
          new Date(job.timestamp_start * 1000).toISOString()
        }}</fwb-table-cell>
        <fwb-table-cell
          >{{ (job.timestamp_end - job.timestamp_start) / 60 }}m</fwb-table-cell
        >
        <fwb-table-cell>{{ job.status }}</fwb-table-cell>
        <fwb-table-cell>{{ job.error_message }}</fwb-table-cell>
      </fwb-table-row>
    </fwb-table-body>
  </fwb-table>
</template>
