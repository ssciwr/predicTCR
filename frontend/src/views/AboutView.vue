<script setup lang="ts">
import {
  FwbA,
  FwbJumbotron,
  FwbButton,
  FwbTimeline,
  FwbTimelineBody,
  FwbTimelineContent,
  FwbTimelineItem,
  FwbTimelinePoint,
  FwbTimelineTitle,
  FwbModal,
} from "flowbite-vue";
import { ref } from "vue";
import LoginComponent from "@/components/LoginComponent.vue";
import SignupComponent from "@/components/SignupComponent.vue";
import { RouterLink } from "vue-router";
const showModalLogin = ref(false);
function closeModals() {
  showModalSignup.value = false;
  showModalLogin.value = false;
}
function openModalLogin() {
  showModalSignup.value = false;
  showModalLogin.value = true;
}
const showModalSignup = ref(false);
function openModalSignup() {
  showModalLogin.value = false;
  showModalSignup.value = true;
}
</script>

<template>
  <main>
    <fwb-jumbotron
      header-text="predicTCR v2"
      header-classes="text-slate-100"
      sub-text="Prediction of tumor-reactive T cells and TCRs from scRNA-seq data."
      sub-text-classes="text-slate-300"
      class="mb-4 bg-slate-800 bg-splash bg-no-repeat bg-center bg-cover md:rounded-lg"
    >
      <div class="flex flex-row justify-center">
        <fwb-button
          @click="openModalSignup"
          class="mr-4 inline-flex justify-center items-center py-3 px-5 text-base font-medium text-center text-white rounded-lg bg-blue-700 hover:bg-blue-800"
        >
          Sign up
        </fwb-button>
        <fwb-button
          @click="openModalLogin"
          class="mr-2 inline-flex justify-center items-center py-3 px-5 text-base font-medium text-center text-white rounded-lg bg-gray-500 hover:bg-gray-600"
        >
          Log in
        </fwb-button>
      </div>
    </fwb-jumbotron>
    <div class="p-4">
      <fwb-timeline>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title> About </fwb-timeline-title>
            <fwb-timeline-body>
              Based on code from the
              <fwb-a href="https://www.dkfz.de/" target="_blank">DKFZ</fwb-a>.
              Read our paper at
              <fwb-a
                href="https://www.nature.com/articles/s41587-024-02161-y"
                target="_blank"
                >Nature Biotechnology</fwb-a
              >
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title> Feedback </fwb-timeline-title>
            <fwb-timeline-body>
              <p>
                Questions or feedback about this service are welcome at
                <fwb-a href="mailto:predictcr@dkfz.de">predictcr@dkfz.de</fwb-a>
              </p>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title> References </fwb-timeline-title>
            <fwb-timeline-body>
              <p>
                The
                <fwb-a href="https://github.com/ssciwr/predicTCR"
                  >predicTCR web service</fwb-a
                >
                was developed by the
                <fwb-a href="https://ssc.iwr.uni-heidelberg.de/"
                  >Scientific Software Center</fwb-a
                >
                of Heidelberg University.
              </p>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
        <fwb-timeline-item>
          <fwb-timeline-point>
            <img src="/logo.png" />
          </fwb-timeline-point>
          <fwb-timeline-content>
            <fwb-timeline-title> Funding </fwb-timeline-title>
            <fwb-timeline-body>
              <div class="flex flex-col md:flex-row">
                <a href="https://dktk.dkfz.de/"
                  ><img class="h-8 m-2 md:pr-5" src="/dktk.jpg" alt="DKTK"
                /></a>
                <a href="https://www.dkfz.de/"
                  ><img class="h-8 m-2" src="/dkfz.png" alt="DKFZ"
                /></a>
              </div>
            </fwb-timeline-body>
          </fwb-timeline-content>
        </fwb-timeline-item>
      </fwb-timeline>
    </div>
  </main>

  <fwb-modal size="md" v-if="showModalLogin" @close="closeModals">
    <template #header>
      <div class="flex items-center text-lg">Login</div>
    </template>
    <template #body>
      <LoginComponent />
      <RouterLink to="/login">Forgot your password?</RouterLink>
    </template>
  </fwb-modal>

  <fwb-modal size="md" v-if="showModalSignup" @close="closeModals">
    <template #header>
      <div class="flex items-center text-lg">Sign up</div>
    </template>
    <template #body>
      <SignupComponent />
    </template>
  </fwb-modal>
</template>
