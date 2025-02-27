<template>
  <NavBar />
  <div class="h-full bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-xl font-bold p-3 md:text-3xl md:p-5 text-surface-900 dark:text-surface-0">
        Bine ai venit, {{ user_data?.data?.name }}!
      </h1>
      <div class="flex flex-col md:flex-row gap-2">
        <Button
          label="Adauga un document nou"
          icon="pi pi-file-plus"
          class="p-button-outlined mr-2"
          @click="showAddDialog"
        />
        <Button
          label="Distribuie codul medicului"
          icon="pi pi-share-alt"
          class="p-button-outlined mr-2"
          @click="showShareDialog"
        />
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-[4fr_3fr_3fr] gap-4 mx-5">

      <Card class="mb-4 md:mb-0 md:h-full md:flex md:flex-col">
        <template #title>
          <h2 class="text-xl font-bold">Istoric medical</h2>
        </template>
        <template #content>
          <p>
            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Asperiores ullam maiores et
            illo omnis? Quasi optio qui, soluta adipisci sed deserunt veniam labore atque
            perspiciatis expedita sapiente quae at deleniti.
          </p>
        </template>
      </Card>
      <Card class="mb-4 md:mb-0 md:h-full md:flex md:flex-col">
        <template #title>
          <h2 class="text-xl font-bold">Semne vitale</h2>
        </template>
        <template #content>
          <p>
            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Asperiores ullam maiores et
            illo omnis? Quasi optio qui, soluta adipisci sed deserunt veniam labore atque
            perspiciatis expedita sapiente quae at deleniti.
          </p>
        </template>
      </Card>

      <RecentMeds :medications="user_data?.data?.medications" class="mb-4 md:mb-0 md:h-full" />

      <Card class="mb-4 md:mb-0 md:h-full md:flex md:flex-col">
        <template #title>
          <h2 class="text-xl font-bold">Analize laborator</h2>
        </template>
        <template #content>
          <p>
            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Asperiores ullam maiores et
            illo omnis? Quasi optio qui, soluta adipisci sed deserunt veniam labore atque
            perspiciatis expedita sapiente quae at deleniti.
          </p>
        </template>
      </Card>

      <RecentVaccines :vaccines="user_data?.data?.vaccines" class="mb-4 md:mb-0 md:h-full" />

      <RecentAllergies :allergies="user_data?.data?.allergies" class="mb-4 md:mb-0 md:h-full" />
    </div>

  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
import Button from 'primevue/button'
import Card from 'primevue/card'
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import RecentVaccines from '@/components/dashboard/RecentVaccines.vue'
import RecentAllergies from '@/components/dashboard/RecentAllergies.vue'
import RecentMeds from '@/components/dashboard/RecentMeds.vue'

const user_data = ref('')

onMounted(async () => {
  user_data.value = await api.get('/dashboard')
  console.log(user_data.value.data)
})
</script>
