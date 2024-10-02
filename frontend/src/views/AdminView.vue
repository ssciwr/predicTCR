<script setup lang="ts">
import SamplesTable from "@/components/SamplesTable.vue";
import UsersTable from "@/components/UsersTable.vue";
import {
  FwbTimeline,
  FwbTimelineBody,
  FwbTimelineContent,
  FwbTimelineItem,
  FwbTimelinePoint,
  FwbTimelineTitle,
  FwbButton,
} from "flowbite-vue";
import { ref } from "vue";
import type { Sample } from "@/utils/types";
import { apiClient, logout } from "@/utils/api-client";

function generate_api_token() {
  apiClient.get("admin/runner_token").then((response) => {
    navigator.clipboard
      .writeText(response.data.access_token)
      .then(() => {
        console.log("API token copied to clipboard");
      })
      .catch((error) => {
        if (error.response.status > 400) {
          logout();
        }
        console.log("Failed to copy API token to clipboard");
      });
  });
}

const samples = ref([] as Sample[]);

function get_samples() {
  apiClient
    .get("admin/samples")
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

get_samples();
</script>

<template>
  <main>
    <div class="p-4">
      <fwb-timeline>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title>Generate runner API Token</fwb-timeline-title>
            <fwb-timeline-body>
              <p>
                Here you can generate a new runner user with an API token for
                authentication. Note the token should be kept secret! It is
                valid for 6 months, then you will need to generate a new one:
              </p>
              <p>
                <fwb-button @click="generate_api_token">
                  Generate API Token and copy to clipboard
                </fwb-button>
              </p>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title>Runners</fwb-timeline-title>
            <fwb-timeline-body>
              <UsersTable :is_runner="true"></UsersTable>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title>Users</fwb-timeline-title>
            <fwb-timeline-body>
              <UsersTable :is_runner="false"></UsersTable>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title>Samples</fwb-timeline-title>
            <fwb-timeline-body>
              <SamplesTable :samples="samples" :admin="true"></SamplesTable>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
      </fwb-timeline>
    </div>
  </main>
</template>
