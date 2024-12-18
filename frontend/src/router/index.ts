import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import HomeView from "@/views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/about",
      name: "about",
      component: () => import("../views/AboutView.vue"),
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/activate/:activation_token",
      name: "activate",
      component: () => import("../views/ActivateView.vue"),
      props: true,
    },
    {
      path: "/reset_password/:reset_token",
      name: "reset_password",
      component: () => import("../views/ResetPasswordView.vue"),
      props: true,
    },
    {
      path: "/samples",
      name: "samples",
      component: () => import("../views/SamplesView.vue"),
      beforeEnter: (to, from) => {
        const userStore = useUserStore();
        if (userStore.user === null && to.name !== "login") {
          return { name: "login" };
        }
      },
    },
    {
      path: "/admin",
      name: "admin",
      component: () => import("../views/AdminView.vue"),
      beforeEnter: (to, from) => {
        const userStore = useUserStore();
        if (
          (userStore.user === null || !userStore.user.is_admin) &&
          to.name !== "login"
        ) {
          return { name: "login" };
        }
      },
    },
  ],
});

export default router;
