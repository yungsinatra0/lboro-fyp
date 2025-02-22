<template>
  <Menubar :model="items" class="rounded-none">
    <template #start> </template>
    <template #item="{ item, props, hasSubmenu, root }">
      <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
        <a v-ripple class="flex items-center" v-bind="props.action" :href="href" @click="navigate">
          <span>{{ item.label }}</span>
          <i
            v-if="hasSubmenu"
            :class="[
              'pi pi-angle-down ml-auto',
              { 'pi-angle-down': root, 'pi-angle-right': !root },
            ]"
          ></i>
        </a>
      </router-link>
      <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
        <span>{{ item.label }}</span>
        <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
      </a>
    </template>
    <template #end>
      <div class="flex items-center justify-center md:gap-2">
        <!-- <Button icon="pi pi-bell" class="p-button-rounded p-button-text p-button-plain" /> -->
       
        <Button
          label="Toggle Dark Mode"
          @click="toggleDarkMode()"
          variant="text"
          raise
          class="p-button-rounded p-button-text p-button-plain"
        >
          <span :class="[isDarkMode ? 'pi pi-moon' : 'pi pi-sun']" />
        </Button>
        <Button icon="pi pi-cog" class="p-button-rounded p-button-text p-button-plain" />
        <Button icon="pi pi-sign-out" class="p-button-rounded p-button-text p-button-plain" @click="logout" />
        <RouterLink to="/dashboard" class="flex items-center justify-center">
          <Avatar :label="C" shape="circle" />
        </RouterLink>
      </div>
    </template>
  </Menubar>
</template>

<script setup>
import { ref } from 'vue'
import Menubar from 'primevue/menubar'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import { useDarkMode } from '../composables/useDarkMode'
import api from '../services/api'
import router from '../router'

const { isDarkMode, toggleDarkMode } = useDarkMode()

const items = ref([
  {
    label: 'Pagina principala',
    // icon: 'pi pi-home',
    route: '/dashboard',
  },
  {
    label: 'Istoricul medical',
    // icon: 'pi pi-file',
    // route: '/dashboard',
    items: [
      {
        label: 'Vizite medici',
        // icon: 'pi pi-calendar',
        route: '/dashboard',
      },
      {
        label: 'Analize laborator',
        // icon: 'pi pi-chart-bar',
        route: '/dashboard',
      },
    ],
  },
  {
    label: 'Cabinetul personal',
    // icon: 'pi-user',
    // route: '/dashboard',
    items: [
      {
        label: 'Vaccine',
        // icon: 'pi pi-syringe',
        route: '/vaccine',
      },
      {
        label: 'Medicamente',
        // icon: 'pi pi-tablet',
        route: '/medicamente',
      },
      {
        label: 'Alergii',
        // icon: 'pi pi-ban',
        route: '/dashboard',
      },
      {
        label: 'Semne vitale',
        // icon: 'pi pi-wave-pulse',
        route: '/dashboard',
      },
    ],
  },
])

async function logout() {
  try {
    await api.post('/logout')
    router.push('/login')
  } catch {
    console.error('Logout failed')
  }
}
</script>
