import { ref } from "vue";
import type { Settings } from "@/utils/types";
import { defineStore } from "pinia";
import { apiClient, logout } from "@/utils/api-client";

export const useSettingsStore = defineStore("settings", () => {
  const settings = ref({
    id: 1,
    default_personal_submission_quota: 1,
    default_personal_submission_interval_mins: 1,
    global_quota: 1,
    tumor_types: "",
    sources: "",
    platforms: "",
    csv_required_columns: "",
    runner_job_timeout_mins: 1,
    about_md: "",
    max_filesize_h5_mb: 1,
    max_filesize_csv_mb: 1,
    news_items_json: "[]",
  } as Settings);

  function refresh() {
    apiClient
      .get("settings")
      .then((response) => {
        settings.value = response.data as Settings;
      })
      .catch((error) => {
        console.log(error);
      });
  }

  function saveChanges() {
    apiClient
      .post("admin/settings", settings.value)
      .then(() => {
        console.log("Settings updated");
      })
      .catch((error) => {
        if (error.response?.status > 400) {
          logout();
        }
        console.log(error);
      });
  }

  return { settings, refresh, saveChanges };
});
