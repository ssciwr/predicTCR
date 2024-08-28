<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { computed } from "vue";
import TitleItem from "./components/TitleComponent.vue";
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
  <header>
    <div class="wrapper">
      <TitleItem />
      <nav>
        <RouterLink to="/">About</RouterLink>
        <RouterLink to="/samples">My samples</RouterLink>
        <RouterLink
          v-if="userStore.user !== null && userStore.user.is_admin"
          to="/admin"
          >Admin</RouterLink
        >
        <RouterLink to="/login">{{ login_title }}</RouterLink>
      </nav>
    </div>
  </header>
  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

nav {
  width: 100%;
  font-size: 16px;
  text-align: center;
  margin-top: 2rem;
  margin-bottom: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}
</style>
