<script setup lang="ts">
import { useUserStore } from "@/stores/user";
import CardComponent from "@/components/CardComponent.vue";
import LoginComponent from "@/components/LoginComponent.vue";
import AccountComponent from "@/components/AccountComponent.vue";
import ResetComponent from "@/components/ResetComponent.vue";
const userStore = useUserStore();
</script>

<template>
  <main class="flex flex-col items-center justify-center">
    <template v-if="userStore.user !== null">
      <AccountComponent></AccountComponent>
    </template>
    <template v-else>
      <CardComponent title="Login">
        <LoginComponent></LoginComponent>
      </CardComponent>
      <ResetComponent></ResetComponent>
    </template>
  </main>
</template>
