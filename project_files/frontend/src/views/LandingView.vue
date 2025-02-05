<template>
  <Menubar :model="items" class="rounded-none">
    <!-- Will contain logo, and links to various sections of the landing page -->
    <template #item="{ item, props }">
      <router-link v-if="item.route" :to="item.route" v-slot="{ navigate, href }" custom>
        <a v-ripple v-bind="props.action" :href="href" @click="navigate">
          <span>{{ item.label }}</span>
        </a>
      </router-link>
      <a v-else v-ripple v-bind="props.action" :href="item.url" :target="item.target">
        <span>{{ item.label }}</span>
      </a>
    </template>
    <template #end>
      <Button
        label="Toggle Dark Mode"
        @click="toggleDarkMode()"
        variant="text"
        raise
        class="flex items-center p-2"
      >
        <span :class="[isDarkMode ? 'pi pi-moon' : 'pi pi-sun']" />
      </Button>
    </template>
  </Menubar>

  <!-- Main area -->
  <div class="flex lg:flex-row flex-col gap-4 bg-surface-0 dark:bg-surface-900">
    <div class="flex-1 flex items-center justify-center">
      <div class="p-6 pt-12 lg:p-12">
        <h1
          class="text-3xl lg:text-5xl font-bold text-surface-900 dark:text-surface-0 mb-4 lg:leading-normal text-center lg:text-left"
        >
          Cu MedArhiv <br /><span class="text-primary"> ai un istoric definitiv!</span>
        </h1>
        <p
          class="text-surface-700 dark:text-surface-200 leading-normal mb-8 text-center lg:text-left"
        >
          MedArhiv iti ofera posibilitatea de a-ti pastra istoricul medical intr-un singur loc,
          sigur si usor de accesat.
        </p>
        <div class="flex flex-col items-center justify-center gap-6">
          <h2
            class="text-xl lg:text-2xl font-bold text-center text-surface-900 dark:text-surface-0"
          >
            Utilizator existent?
          </h2>
          <Button as="router-link" label="Autentificare" type="button" to="/login" class="w-1/2" />

          <h2
            class="text-xl lg:text-2xl font-bold text-center text-surface-900 dark:text-surface-0"
          >
            Utilizator nou?
          </h2>
          <Button
            as="router-link"
            label="Inregistrare"
            type="button"
            outlined
            to="/register"
            class="w-1/2"
          />
        </div>
      </div>
    </div>
    <div class="flex-1 overflow-hidden">
      <img
        src="https://cdn.pixabay.com/photo/2023/09/07/16/15/ai-generated-8239428_1280.jpg"
        alt="hero-1"
        class="h-full w-full object-cover lg:[clip-path:polygon(12%_0,100%_0%,100%_100%,0_100%)]"
      />
    </div>
  </div>

  <!-- Features -->
  <section class="landing-features" ref="featuresSection">
    <div class="bg-surface-0 dark:bg-surface-950 px-6 py-20 md:px-12 lg:px-20 text-center">
      <div class="mb-4 font-bold text-3xl">
        <span class="text-surface-900 dark:text-surface-0">O singura aplicatie, </span>
        <span class="text-primary-600 dark:text-primary-400">Toate nevoile asigurate</span>
      </div>
      <div class="text-surface-700 dark:text-surface-0/70 mb-[3rem]">
        MedArhiv iti ofera un sistem complex si sigur de gestionare a datelor medicale, punand
        accentul pe confidentialitate si accesibilitate. Descopera functionalitati adaptate pentru
        toti utilizatorii.
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-x-3.5 gap-y-6">
        <div class="w-full p-4">
          <span
            class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center mx-auto bg-surface-0 dark:bg-surface-800 shadow-[0px_2px_6px_0px_rgba(0,0,0,0.12),0px_0px_2px_0px_rgba(0,0,0,0.06),0px_4px_10px_0px_rgba(0,0,0,0.03)]"
          >
            <i class="pi pi-lock text-2xl lg:text-3xl text-primary-500 dark:text-primary-400" />
          </span>
          <div class="text-surface-900 dark:text-surface-0 text-xl mb-2 font-medium">
            Securitatea in prim plan
          </div>
          <p
            class="text-surface-700 dark:text-surface-0/70 leading-normal max-w-sm mx-auto text-center"
          >
            Aplicatia MedArhiv iti ofera un sistem de securitate complex, care iti protejeaza datele
            personale.
          </p>
        </div>
        <div class="w-full p-4">
          <span
            class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center mx-auto bg-surface-0 dark:bg-surface-800 shadow-[0px_2px_6px_0px_rgba(0,0,0,0.12),0px_0px_2px_0px_rgba(0,0,0,0.06),0px_4px_10px_0px_rgba(0,0,0,0.03)]"
          >
            <i class="pi pi-globe text-2xl lg:text-3xl text-primary-500 dark:text-primary-400" />
          </span>
          <div class="text-surface-900 dark:text-surface-0 text-xl mb-2 font-medium">
            Aplicatie web
          </div>
          <p
            class="text-surface-700 dark:text-surface-0/70 leading-normal max-w-sm mx-auto text-center"
          >
            Poate fi accesata de pe orice dispozitiv, de oriunde, in orice moment, folosind doar un
            browser web.
          </p>
        </div>
        <div class="w-full p-4">
          <span
            class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center mx-auto bg-surface-0 dark:bg-surface-800 shadow-[0px_2px_6px_0px_rgba(0,0,0,0.12),0px_0px_2px_0px_rgba(0,0,0,0.06),0px_4px_10px_0px_rgba(0,0,0,0.03)]"
          >
            <i
              class="pi pi-check-circle text-2xl lg:text-3xl text-primary-500 dark:text-primary-400"
            />
          </span>
          <div class="text-surface-900 dark:text-surface-0 text-xl mb-2 font-medium">
            Usor de folosit
          </div>
          <p
            class="text-surface-700 dark:text-surface-0/70 leading-normal max-w-sm mx-auto text-center"
          >
            MedArhiv a fost creat pentru a fi usor de folosit, indiferent de varsta sau experienta
            in utilizarea aplicatiilor web.
          </p>
        </div>
        <div class="w-full p-4">
          <span
            class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center mx-auto bg-surface-0 dark:bg-surface-800 shadow-[0px_2px_6px_0px_rgba(0,0,0,0.12),0px_0px_2px_0px_rgba(0,0,0,0.06),0px_4px_10px_0px_rgba(0,0,0,0.03)]"
          >
            <i class="pi pi-desktop text-2xl lg:text-3xl text-primary-500 dark:text-primary-400" />
          </span>
          <div class="text-surface-900 dark:text-surface-0 text-xl mb-2 font-medium">
            Medicii nu necesita inregistrare
          </div>
          <p
            class="text-surface-700 dark:text-surface-0/70 leading-normal max-w-sm mx-auto text-center"
          >
            Arhiva pacientilor poate fi accesata de catre medici fara a fi nevoie de inregistrare,
            pentru a facilita procesul de diagnosticare.
          </p>
        </div>
        <div class="w-full p-4">
          <span
            class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center mx-auto bg-surface-0 dark:bg-surface-800 shadow-[0px_2px_6px_0px_rgba(0,0,0,0.12),0px_0px_2px_0px_rgba(0,0,0,0.06),0px_4px_10px_0px_rgba(0,0,0,0.03)]"
          >
            <i class="pi pi-github text-2xl lg:text-3xl text-primary-500 dark:text-primary-400" />
          </span>
          <div class="text-surface-900 dark:text-surface-0 text-xl mb-2 font-medium">
            Open Source
          </div>
          <p
            class="text-surface-700 dark:text-surface-0/70 leading-normal max-w-sm mx-auto text-center"
          >
            Codul MedArhiv este open source, astfel incat oricine poate contribui la imbunatatirea
            aplicatiei. Accesati codul sursa
            <Button as="router-link" label="aici." variant="text" to="/" class="p-0 border-0" />
          </p>
        </div>
        <div class="w-full p-4">
          <span
            class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center mx-auto bg-surface-0 dark:bg-surface-800 shadow-[0px_2px_6px_0px_rgba(0,0,0,0.12),0px_0px_2px_0px_rgba(0,0,0,0.06),0px_4px_10px_0px_rgba(0,0,0,0.03)]"
          >
            <i class="pi pi-shield text-2xl lg:text-3xl text-primary-500 dark:text-primary-400" />
          </span>
          <div class="text-surface-900 dark:text-surface-0 text-xl mb-2 font-medium">
            Recomandat de medici
          </div>
          <p
            class="text-surface-700 dark:text-surface-0/70 leading-normal max-w-sm mx-auto text-center"
          >
            9 din 10 medici recomanda MedArhiv pentru a elimina durerea de cap lucrand cu arhiva
            medicala
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- About the team -->
  <section class="landing-about" ref="aboutSection">
    <div class="flex lg:flex-row flex-col gap-4 bg-surface-0 dark:bg-surface-900">
      <div class="flex-1 overflow-hidden">
        <img
          src="https://cdn.pixabay.com/photo/2023/09/07/16/15/ai-generated-8239428_1280.jpg"
          alt="hero-1"
          class="h-full w-full object-cover lg:[clip-path:polygon(0%_0,100%_0%,100%_100%,0_100%)]"
        />
      </div>

      <div class="flex-1 flex items-center justify-center">
        <div class="p-6 pt-12 lg:p-12">
          <h1
            class="text-3xl lg:text-5xl font-bold text-surface-900 dark:text-surface-0 mb-4 lg:leading-normal text-center lg:text-left"
          >
            Echipa MedArhiv
          </h1>
          <p
            class="text-surface-700 dark:text-surface-200 leading-normal mb-8 text-center lg:text-left"
          >
            MedArhiv este dezvoltat de un student,
            <span class="text-primary font-bold"> Calin Corcimaru</span>, in cadrul proiectului de
            licenta la universitatea Loughborough din Marea Britanie.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Contact section -->
  <section
    class="p-10 flex flex-col items-center justify-center bg-surface-0 dark:bg-surface-900"
    ref="contactSection"
  >
    <h1 class="text-5xl font-bold text-center text-surface-900 dark:text-surface-0 mb-4 p-2">
      Contacteaza-ne
    </h1>
    <div class="card flex justify-center">
      <Form
        v-slot="$form"
        :initialValues
        :resolver
        :validateOnValueUpdate="false"
        :validateOnBlur="true"
        :validateOnMount="['firstName']"
        @submit="onFormSubmit"
        class="flex flex-col gap-4 w-full sm:w-96"
      >
        <div class="flex flex-col gap-1">
          <InputText name="Nume" type="text" placeholder="Nume" fluid />
          <Message v-if="$form.name?.invalid" severity="error" size="small" variant="simple">{{
            $form.name.error.message
          }}</Message>
        </div>
        <div class="flex flex-col gap-1">
          <InputText
            name="Email"
            type="email"
            placeholder="Adresa de email"
            fluid
            :formControl="{ validateOnValueUpdate: true }"
          />
          <Message v-if="$form.email?.invalid" severity="error" size="small" variant="simple">{{
            $form.email.error.message
          }}</Message>
        </div>
        <div class="flex flex-col gap-1">
          <Textarea name="Mesajul tau" type="text" placeholder="Mesaj" fluid class="resize-y" />
          <Message v-if="$form.message?.invalid" severity="error" size="small" variant="simple">{{
            $form.message.error.message
          }}</Message>
        </div>
        <Button type="submit" severity="secondary" label="Submit" />
      </Form>
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <div
      class="bg-surface-0 dark:bg-surface-900 text-surface-700 dark:text-surface-200 text-center py-4"
    >
      <span>© 2025 MedArhiv. All rights reserved.</span>
    </div>
  </footer>
</template>

<script setup>
import Button from 'primevue/button'
import Menubar from 'primevue/menubar'
import { InputText, Textarea } from 'primevue'
import { ref, useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { useDarkMode } from '../composables/useDarkMode'
import { Form } from '@primevue/forms'

const router = useRouter()

const { isDarkMode, toggleDarkMode } = useDarkMode()

const featuresSection = useTemplateRef('featuresSection')
const aboutSection = useTemplateRef('aboutSection')
const contactSection = useTemplateRef('contactSection')

const initialValues = ref({
  name: '',
  email: '',
  message: '',
})

const resolver = ({ values }) => {
  const errors = {}

  if (!values.name) {
    errors.name = [{ message: 'Introdu numele tau' }]
  }

  if (!values.email) {
    errors.email = [{ message: 'Introdu email-ul tau' }]
  }

  if (!values.message) {
    errors.message = [{ message: 'Introdu mesajul tau' }]
  }

  return {
    errors,
  }
}

const onFormSubmit = ({ valid }) => {
  if (valid) {
    console.log('Form submitted')
  }
}

const items = ref([
  {
    label: 'Acasa',
    icon: 'pi pi-home',
    route: '/',
  },
  {
    label: 'Despre MedArhiv',
    command: () => {
      setTimeout(() => {
        featuresSection.value.scrollIntoView({ behavior: 'smooth' }) // This is a horrible hack, but it works (for now)
      }, 1)
    },
  },
  {
    label: 'Despre echipa',
    command: () => {
      setTimeout(() => {
        aboutSection.value.scrollIntoView({ behavior: 'smooth' })
      }, 1)
    },
  },
  {
    label: 'Contacteaza-ne',
    command: () => {
      setTimeout(() => {
        contactSection.value.scrollIntoView({ behavior: 'smooth' })
      }, 1)
    },
  },
])
</script>

<style scope></style>
