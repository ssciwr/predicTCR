<script setup lang="ts">
import { useUserStore } from "@/stores/user";
import LoginComponent from "@/components/LoginComponent.vue";
import SignupComponent from "@/components/SignupComponent.vue";
import AccountComponent from "@/components/AccountComponent.vue";
import ResetComponent from "@/components/ResetComponent.vue";
const userStore = useUserStore();
</script>

<template>
  <main>
    <template v-if="userStore.user !== null">
      <AccountComponent></AccountComponent>
    </template>
    <template v-else>
      <LoginComponent></LoginComponent>
      <SignupComponent></SignupComponent>
      <ResetComponent></ResetComponent>
    </template>
  </main>
</template>
