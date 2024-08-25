import axios from "axios";
import router from "@/router";
import type { AxiosInstance } from "axios";
import { useUserStore } from "@/stores/user";

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_REST_API_LOCATION,
  headers: {
    "Content-type": "application/json",
  },
});

apiClient.interceptors.request.use(function (config) {
  const user = useUserStore();
  config.headers.Authorization = `Bearer ${user.token}`;
  return config;
});

function download_file_from_endpoint(
  endpoint: string,
  json: object,
  filename: string,
) {
  apiClient
    .post(endpoint, json, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      responseType: "blob",
    })
    .then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
    })
    .catch((error) => {
      if (error.response.status > 400) {
        logout();
      }
    });
}

function download_input_file(sample_id: number) {
  download_file_from_endpoint(
    "input_file",
    { sample_id: sample_id },
    `${sample_id}_input_file.zip`,
  );
}

function download_result(sample_id: number) {
  download_file_from_endpoint(
    "result",
    { sample_id: sample_id },
    `${sample_id}.zip`,
  );
}

function logout() {
  const user = useUserStore();
  user.user = null;
  user.token = "";
  router.push({ name: "login" });
}

export { apiClient, logout, download_input_file, download_result };
