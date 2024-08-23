<script setup lang="ts">
import ListItem from "@/components/ListItem.vue";
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
const remaining = ref(0);
const remaining_message = ref("");
apiClient
  .get("remaining")
  .then((response) => {
    remaining.value = response.data.remaining;
    remaining_message.value = response.data.message;
  })
  .catch((error) => {
    remaining_message.value = "Could not connect to server.";
  });
</script>

<template>
  <main>
    <ListItem title="About" icon="bi-lightbulb">
      <p v-if="remaining_message">{{ remaining_message }}</p>
      <p v-else>Remaining available samples this week: {{ remaining }}.</p>
    </ListItem>
    <ListItem title="Feedback" icon="bi-chat">
      Questions or feedback about this service are welcome at
      <a href="mailto:e.green@dkfz.de?subject=predicTCR">e.green@dkfz.de</a>
    </ListItem>
    <ListItem title="References" icon="bi-book">
      <p>
        The Sample Flow
        <a href="https://github.com/ssciwr/predicTCR">web service</a> was
        developed by the
        <a href="https://ssc.iwr.uni-heidelberg.de/"
          >Scientific Software Center</a
        >
        of Heidelberg University.
      </p>
    </ListItem>
    <ListItem title="Funding" icon="bi-info-circle">
      This work was funded by the
      <a href="https://www.health-life-sciences.de/?lang=de"
        >Heidelberg Mannheim Life Sciences alliance</a
      >
      through an 'Explore!Tech' grant awarded to Drs Ed Green, Liam Keegan and
      Kim Remans.
    </ListItem>
  </main>
</template>
