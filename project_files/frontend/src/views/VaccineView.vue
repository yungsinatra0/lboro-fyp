<template>
  <NavBar />

  <div class="flex items-center justify-between">  
    <h1 class="text-2xl font-bold p-3 md:text-4xl md:p-5">Vaccinele mele</h1>
    <Button label="Adauga vaccin" icon="pi pi-plus" class="p-button-outlined mr-2" />
  </div>
<VaccineCard 
    :name="'COVID-19'" 
    :date-received="new Date(2024,0,10).toLocaleDateString('ro-RO')" 
    :provider="'Pfizer'" 
/>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import VaccineCard from '@/components/VaccineCard.vue'
import Button from 'primevue/button'
</script>
