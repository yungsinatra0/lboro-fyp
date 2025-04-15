<template>
  <div class="flex justify-between items-center mb-4">
    <div>
      <h2>Date pacient</h2>
      <span> {{ shareData?.patient.name }} </span> <span> {{ shareData?.patient.dob }} </span>
    </div>
    <div>
        <h2> Link-ul expira la </h2>
        <span> {{ shareData?.expiration_time }} </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  shareData: Object,
})
</script>
