<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from "vue-router";
import { computed } from "vue";
import {
  FwbNavbar,
  FwbNavbarCollapse,
  FwbNavbarLink,
  FwbNavbarLogo,
} from "flowbite-vue";
import { useUserStore } from "@/stores/user";
const userStore = useUserStore();
const login_title = computed(() => {
  if (userStore.user !== null) {
    return userStore.user.email;
  }
  return "Login";
});
</script>

<template>
  <fwb-navbar>
    <template #logo>
      <fwb-navbar-logo alt="predicTCR v2" image-url="/logo.png" link="#">
        predicTCR v2
      </fwb-navbar-logo>
    </template>
    <template #default="{ isShowMenu }">
      <fwb-navbar-collapse :is-show-menu="isShowMenu">
        <fwb-navbar-link link="#">
          <RouterLink to="/">About</RouterLink>
        </fwb-navbar-link>
        <fwb-navbar-link link="#">
          <RouterLink to="/samples">My samples</RouterLink>
        </fwb-navbar-link>
        <fwb-navbar-link
          link="#"
          v-if="userStore.user !== null && userStore.user.is_admin"
        >
          <RouterLink to="/admin">Admin</RouterLink>
        </fwb-navbar-link>
        <fwb-navbar-link link="#">
          <RouterLink to="/login">{{ login_title }}</RouterLink>
        </fwb-navbar-link>
      </fwb-navbar-collapse>
    </template>
  </fwb-navbar>
  <div class="flex flex-col items-center justify-center">
    <RouterView />
  </div>
</template>
