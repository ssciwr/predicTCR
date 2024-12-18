<script setup lang="ts">
import { FwbA, FwbButton, FwbModal } from "flowbite-vue";
import { ref } from "vue";
import HeadingComponent from "@/components/HeadingComponent.vue";
import ListComponent from "@/components/ListComponent.vue";
import ListItem from "@/components/ListItem.vue";
import LoginComponent from "@/components/LoginComponent.vue";
import SignupComponent from "@/components/SignupComponent.vue";
import { RouterLink } from "vue-router";
import CarouselComponent from "@/components/CarouselComponent.vue";
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
  <main class="flex flex-col items-center justify-center">
    <HeadingComponent>
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
      <CarouselComponent class="mt-4" />
    </HeadingComponent>
    <div class="p-4">
      <ListComponent>
        <ListItem title="About">
          Based on code from the
          <fwb-a href="https://www.dkfz.de/" target="_blank">DKFZ</fwb-a>. Read
          our paper at
          <fwb-a
            href="https://www.nature.com/articles/s41587-024-02161-y"
            target="_blank"
            >Nature Biotechnology</fwb-a
          >
        </ListItem>
        <ListItem title="Feedback">
          Questions or feedback about this service are welcome at
          <fwb-a href="mailto:predictcr@dkfz.de">predictcr@dkfz.de</fwb-a>
        </ListItem>
        <ListItem title="References">
          The
          <fwb-a href="https://github.com/ssciwr/predicTCR"
            >predicTCR web service</fwb-a
          >
          was developed by the
          <fwb-a href="https://ssc.iwr.uni-heidelberg.de/"
            >Scientific Software Center</fwb-a
          >
          of Heidelberg University.
        </ListItem>
        <ListItem title="Funding">
          <div class="flex flex-col md:flex-row">
            <a href="https://dktk.dkfz.de/"
              ><img class="h-8 m-2 md:pr-5" src="/dktk.jpg" alt="DKTK"
            /></a>
            <a href="https://www.dkfz.de/"
              ><img class="h-8 m-2" src="/dkfz.png" alt="DKFZ"
            /></a>
          </div>
        </ListItem>
      </ListComponent>
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
