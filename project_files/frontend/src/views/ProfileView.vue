<template>
  <NavBar />

  <div class="min-h-screen bg-surface-0 dark:bg-surface-900 flex flex-col">
    <div class="flex flex-col items-center md:flex-row md:justify-between p-3 md:p-5">
      <h1 class="text-xl font-bold p-3 md:text-3xl md:p-5 text-surface-900 dark:text-surface-0">
        Profilul personal
      </h1>
    </div>
    <div class="flex flex-col items-center justify-center gap-4 mx-5">
      <Card :pt="cardStyles" class="w-1/3 flex flex-col">
        <template #title>
          <h2 class="flex text-xl font-bold justify-center">Date personale</h2>
        </template>
        <template #content>
          <p><span class="font-bold"> Numele: </span>{{ userValue?.data?.name }}</p>
          <p><span class="font-bold"> Email: </span>{{ userValue?.data?.email }}</p>
          <p><span class="font-bold"> Data nasterii: </span> {{ userValue?.data?.dob }}</p>
        </template>
      </Card>

      <Card :pt="cardStyles" class="w-1/3 flex flex-col">
        <template #title>
          <h2 class="flex text-xl font-bold justify-center mb-4">Schimba parola</h2>
          
          <!-- Error message -->
          <Message v-if="errorMessage" severity="error" class="w-full mb-4">
            {{ errorMessage }}
          </Message>
        </template>
        <template #content>
          <Form
            v-slot="$form"
            :initialValues
            :resolver="resolver"
            @submit="onFormSubmit"
            class="space-y-6"
          >
            <div class="flex flex-col gap-2">
              <label class="font-bold text-surface-700 dark:text-surface-200"> Parola veche </label>
              <Password
                name="oldPassword"
                :feedback="false"
                placeholder="Introdu parola veche"
                toggleMask
                fluid
              />
              <Message
                v-if="$form.oldPassword?.invalid"
                severity="error"
                size="small"
                variant="simple"
                class="text-rose-600 text-sm mt-1"
                >{{ $form.oldPassword.error.message }}</Message
              >
            </div>

            <div class="flex flex-col gap-2">
              <label class="font-bold text-surface-700 dark:text-surface-200"> Parola noua </label>
              <Password
                name="newPassword"
                :feedback="false"
                placeholder="Introdu parola noua"
                toggleMask
                fluid
              />
              <Message
                v-if="$form.newPassword?.invalid"
                severity="error"
                size="small"
                variant="simple"
                class="text-rose-600 text-sm mt-1"
                >{{ $form.newPassword.error.message }}</Message
              >
            </div>

            <div class="flex flex-col gap-2">
              <label class="font-bold text-surface-700 dark:text-surface-200">
                Confirma parola
              </label>
              <Password
                name="confirmPassword"
                :feedback="false"
                placeholder="Confirma parola noua"
                toggleMask
                fluid
              />
              <Message
                v-if="$form.confirmPassword?.invalid"
                severity="error"
                size="small"
                variant="simple"
                class="text-rose-600 text-sm mt-1"
                >{{ $form.confirmPassword.error.message }}</Message
              >
            </div>

            <div class="flex justify-center mt-6">
              <Button 
                label="Schimba parola" 
                type="submit" 
                class="px-6 py-2" 
                :loading="isLoading"
              />
            </div>
          </Form>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
/**
 * @file ProfileView.vue
 * @description This file contains the ProfileView component, which displays the user's profile information and allows them to change their password.
 */
import NavBar from '../components/NavBar.vue'
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { Form } from '@primevue/forms'
import { z } from 'zod'
import { zodResolver } from '@primevue/forms/resolvers/zod'
import router from '../router'

const userValue = ref(null)
const errorMessage = ref(null)
const isLoading = ref(false)

/**
 * Fetches the current user's data from the API and sets it to the userValue ref.
 */
onMounted(async () => {
  userValue.value = await api.get('/me')
})

const initialValues = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// Zod schema for form validation
const resolver = zodResolver(
  z
    .object({
      oldPassword: z.string('Parola veche este necesara'),
      newPassword: z
        .string()
        .min(8, { message: 'Parola trebuie sa aiba cel putin 8 caractere' })
        .refine((value) => /[A-Z]/.test(value), {
          message: 'Parola trebuie sa contina cel putin o litera mare',
        })
        .refine((value) => /[!@#$%^&*(),.?":{}|<>]/.test(value), {
          message: 'Parola trebuie sa contina cel putin un simbol special',
        })
        .refine((value) => /\d/.test(value), {
          message: 'Parola trebuie sa contina cel putin o cifra',
        }),
      confirmPassword: z.string(),
    })
    .refine((data) => data.newPassword === data.confirmPassword, {
      message: 'Parolele nu coincid',
      path: ['confirmPassword'],
    }),
)

const cardStyles = {
  body: { class: 'px-4 py-1 flex flex-col flex-1' },
  content: { class: 'flex-1 flex flex-col' },
  root: {
    class:
      'bg-surface-0 dark:bg-surface-800 text-surface-700 dark:text-surface-0 dark:border dark:border-surface-700',
  },
  footer: { class: 'flex mt-auto justify-center items-center' },
}
/**
 * @function changePassword
 * @description This function is used to change the user's password. After a successful password change, it logs the user out and redirects them to the login page.
 * @param passwords - Object containing the old and new passwords.
 */
const changePassword = async (passwords) => {
  errorMessage.value = null
  
  try {
    await api.patch('/update/password', {
      current_password: passwords.oldPassword,
      new_password: passwords.newPassword,
    })

    // If successful, logout and redirect
    await api.post('/logout')
    router.push('/login')

  } catch (error) {
    console.error('Error changing password: ', error)
    // Handle basic error display
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'A apărut o eroare la schimbarea parolei. Vă rugăm să încercați din nou.'
    }
  }
}

const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (!e.valid) {
    console.error('Error changing password: ', e.errors)
    return
  }

  changePassword(e.values)
}
</script>
