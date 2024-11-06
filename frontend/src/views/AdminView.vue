<script setup lang="ts">
import SamplesTable from "@/components/SamplesTable.vue";
import SettingsTable from "@/components/SettingsTable.vue";
import UsersTable from "@/components/UsersTable.vue";
import ListComponent from "@/components/ListComponent.vue";
import JobsTable from "@/components/JobsTable.vue";
import ListItem from "@/components/ListItem.vue";
import { FwbButton, FwbTab, FwbTabs } from "flowbite-vue";
import { onUnmounted, ref } from "vue";
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

const activeTab = ref("samples");
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

let update_data_handle = setTimeout(function update_data() {
  get_samples();
  update_data_handle = setTimeout(update_data, 30000);
});

onUnmounted(() => {
  clearTimeout(update_data_handle);
});
</script>

<template>
  <main>
    <div class="p-4">
      <fwb-tabs v-model="activeTab" variant="underline" class="p-5">
        <fwb-tab name="samples" title="Samples">
          <ListComponent>
            <ListItem title="Samples">
              <SamplesTable
                :samples="samples"
                :admin="true"
                @samples-modified="get_samples"
              ></SamplesTable>
            </ListItem>
          </ListComponent>
        </fwb-tab>
        <fwb-tab name="users" title="Users">
          <ListComponent>
            <ListItem title="Users">
              <UsersTable :is_runner="false"></UsersTable>
            </ListItem>
          </ListComponent>
        </fwb-tab>
        <fwb-tab name="runners" title="Runners">
          <ListComponent>
            <ListItem title="Generate runner API Token">
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
            </ListItem>
            <ListItem title="Runners">
              <UsersTable :is_runner="true"></UsersTable>
            </ListItem>
            <ListItem title="Runner Jobs">
              <JobsTable />
            </ListItem>
          </ListComponent>
        </fwb-tab>
        <fwb-tab name="settings" title="Settings">
          <ListComponent>
            <ListItem title="Settings">
              <SettingsTable />
            </ListItem>
          </ListComponent>
        </fwb-tab>
      </fwb-tabs>
    </div>
  </main>
</template>
