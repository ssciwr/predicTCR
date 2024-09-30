<script setup lang="ts">
import { useUserStore } from "@/stores/user";
import ListItem from "@/components/ListItem.vue";
import LoginComponent from "@/components/LoginComponent.vue";
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
      <ListItem title="Login">
        <LoginComponent></LoginComponent>
      </ListItem>
      <ResetComponent></ResetComponent>
    </template>
  </main>
</template>
