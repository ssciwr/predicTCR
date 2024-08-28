<script setup lang="ts">
import ListItem from "@/components/ListItem.vue";
</script>

<template>
  <main>
    <ListItem title="About" icon="bi-lightbulb">
      <p>
        Based on code from the
        <a href="https://www.dkfz.de/" target="_blank">DKFZ</a>. Read our paper
        at
        <a
          href="https://www.nature.com/articles/s41587-024-02161-y"
          target="_blank"
          >Nature Biotechnology</a
        >
      </p>
    </ListItem>
    <ListItem title="Feedback" icon="bi-chat">
      Questions or feedback about this service are welcome at
      <a href="mailto:e.green@dkfz.de?subject=predicTCR">e.green@dkfz.de</a>
    </ListItem>
    <ListItem title="References" icon="bi-book">
      <p>
        The predicTCR
        <a href="https://github.com/ssciwr/predicTCR">web service</a> was
        developed by the
        <a href="https://ssc.iwr.uni-heidelberg.de/"
          >Scientific Software Center</a
        >
        of Heidelberg University.
      </p>
    </ListItem>
    <ListItem title="Funding" icon="bi-info-circle"> Funding info? </ListItem>
  </main>
</template>
