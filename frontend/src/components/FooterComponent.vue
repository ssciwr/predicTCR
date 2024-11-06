<script setup lang="ts">
import {
  FwbFooter,
  FwbFooterCopyright,
  FwbFooterLinkGroup,
  FwbFooterLink,
  FwbFooterBrand,
} from "flowbite-vue";
</script>

<template>
  <fwb-footer sticky>
    <fwb-footer-copyright
      by="DKFZ"
      href="https://www.dkfz.de/"
      copyright-message="All Rights Reserved."
    />
    <div>predicTCR v2 - beta version</div>
    <fwb-footer-link-group>
      <fwb-footer-link href="mailto:predictcr@dkfz.de">Contact</fwb-footer-link>
      <fwb-footer-link href="https://www.dkfz.de/de/impressum.html"
        >Impressum</fwb-footer-link
      >
    </fwb-footer-link-group>
  </fwb-footer>
</template>
