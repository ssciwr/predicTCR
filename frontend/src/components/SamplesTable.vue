<script setup lang="ts">
// @ts-ignore
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
  <table class="zebra" aria-label="Samples">
    <tr>
      <th v-if="admin">Id</th>
      <th>Date</th>
      <th v-if="admin">Email</th>
      <th>Sample Name</th>
      <th>Tumor type</th>
      <th>Source</th>
      <th>Status</th>
      <th>Input H5 file</th>
      <th>Input csv file</th>
      <th>Results</th>
    </tr>
    <tr v-for="sample in samples" :key="sample.id">
      <td v-if="admin">{{ sample["id"] }}</td>
      <td>{{ new Date(sample["timestamp"] * 1000).toLocaleDateString() }}</td>
      <td v-if="admin">{{ sample["email"] }}</td>
      <td>{{ sample["name"] }}</td>
      <td>{{ sample["tumor_type"] }}</td>
      <td>{{ sample["source"] }}</td>
      <td>{{ sample["status"] }}</td>
      <td>
        <a
          href=""
          @click.prevent="download_input_h5_file(sample.id, sample.name)"
        >
          input.h5
        </a>
      </td>
      <td>
        <a
          href=""
          @click.prevent="download_input_csv_file(sample.id, sample.name)"
        >
          input.csv
        </a>
      </td>
      <td>
        <template v-if="sample.has_results_zip">
          <a href="" @click.prevent="download_result(sample.id, sample.name)"
            >zip</a
          >
        </template>
        <template v-else> - </template>
      </td>
    </tr>
  </table>
</template>
