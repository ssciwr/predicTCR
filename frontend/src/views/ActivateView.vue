<script setup lang="ts">
import ListItem from "@/components/ListItem.vue";
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
const props = defineProps({ activation_token: String });

const title = ref("");
const message = ref("");
const icon = ref("bi-person-exclamation");

apiClient
  .get(`activate/${props.activation_token}`)
  .then((response) => {
    console.log(response);
    message.value = response.data.message;
    icon.value = "bi-person-check";
    title.value = "Account Activation Successful";
  })
  .catch((error) => {
    if (error.response != null) {
      message.value = error.response.data.message;
    } else {
      message.value = "Cannot connect to server.";
    }
    icon.value = "bi-person-exclamation";
    title.value = "Account Activation Failed";
  });
</script>

<template>
  <main>
    <ListItem :title="title" :icon="icon">
      <p>{{ message }}</p>
      <p>Go to <RouterLink to="/login">login / signup</RouterLink> page.</p>
    </ListItem>
  </main>
</template>
