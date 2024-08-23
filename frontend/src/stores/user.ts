import { ref } from "vue";
import type { User } from "@/utils/types";
import { defineStore } from "pinia";

export const useUserStore = defineStore("user", () => {
  const user = ref(null as User | null);
  const token = ref("");
  return { user, token };
});
