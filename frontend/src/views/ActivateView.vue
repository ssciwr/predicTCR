<script setup lang="ts">
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
import CardComponent from "@/components/CardComponent.vue";
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
    title.value =
      "Email validation successful - after an administrator enables your account you will be able to log in and submit samples.";
  })
  .catch((error) => {
    if (error.response != null) {
      message.value = error.response.data.message;
    } else {
      message.value = "Cannot connect to server.";
    }
    icon.value = "bi-person-exclamation";
    title.value = "Account Activation Failed.";
  });
</script>

<template>
  <main class="flex flex-col items-center justify-center">
    <CardComponent :title="title">
      <p>{{ message }}</p>
      <p>Go to <RouterLink to="/login">login</RouterLink> page.</p>
    </CardComponent>
  </main>
</template>
