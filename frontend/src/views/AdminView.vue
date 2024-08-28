<script setup lang="ts">
import ListItem from "@/components/ListItem.vue";
import SamplesTable from "@/components/SamplesTable.vue";
import { ref } from "vue";
import type { Sample, User } from "@/utils/types";
import { apiClient, logout } from "@/utils/api-client";

function generate_api_token() {
  apiClient.get("admin/runner_token").then((response) => {
    navigator.clipboard
      .writeText(response.data.access_token)
      .then(() => {
        get_users();
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

const users = ref([] as User[]);

function get_users() {
  apiClient
    .get("admin/users")
    .then((response) => {
      users.value = response.data.users;
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

get_users();

function enable_user(user_email: string) {
  apiClient
    .post("admin/enable_user", { user_email: user_email })
    .then(() => {
      get_users();
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}

function disable_user(user_email: string) {
  apiClient
    .post("admin/disable_user", { user_email: user_email })
    .then(() => {
      get_users();
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
      console.log(error);
    });
}
</script>

<template>
  <main>
    <ListItem title="Generate runner API Token" icon="bi-gear">
      <p>
        Here you can generate a new runner use with an API token for
        authentication. Note this token should be kept secret! It is valid for 6
        months, then you will need to generate a new one.
      </p>
      <p>
        <button @click="generate_api_token">
          Generate API Token and copy to clipboard
        </button>
      </p>
    </ListItem>
    <ListItem title="Users" icon="bi-gear">
      <p>{{ users.length }} registered users:</p>
      <table class="zebra" aria-label="Registered users">
        <tr>
          <th>Id</th>
          <th>Email</th>
          <th>Activated</th>
          <th>Enabled</th>
          <th>Remaining quota</th>
          <th>Last submission</th>
          <th>Admin</th>
          <th>Runner</th>
          <th>Enable/disable</th>
        </tr>
        <tr
          v-for="user in users"
          :key="user.id"
          :class="{ disabled: !user.enabled }"
        >
          <td>{{ user.id }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.activated }}</td>
          <td>{{ user.enabled }}</td>
          <td>{{ user.quota }}</td>
          <td>
            {{
              new Date(
                user.last_submission_timestamp * 1000,
              ).toLocaleDateString()
            }}
          </td>
          <td>{{ user.is_admin }}</td>
          <td>{{ user.is_runner }}</td>
          <td>
            <template v-if="user.enabled">
              <button @click="disable_user(user.email)">Disable</button>
            </template>
            <template v-else>
              <button @click="enable_user(user.email)">Enable</button>
            </template>
          </td>
        </tr>
      </table>
    </ListItem>
    <ListItem title="Samples" icon="bi-gear">
      <p>{{ samples.length }} samples have been requested so far:</p>
      <SamplesTable :samples="samples" :admin="true"></SamplesTable>
    </ListItem>
  </main>
</template>

<style scoped>
.disabled {
  color: red;
}
</style>
