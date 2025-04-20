<template>
  <div
    class="flex flex-col items-center justify-center bg-surface-50 dark:bg-surface-950 px-6 py-20 md:px-12 lg:px-20 h-dvh"
  >
    <div
      class="flex flex-col items-center justify-center bg-surface-0 dark:bg-surface-900 p-6 shadow rounded-border w-full lg:w-6/12 mx-auto"
    >
      <div class="text-center mb-4">
        <svg
          class="mb-4 mx-auto fill-surface-600 dark:fill-surface-200 h-16"
          viewBox="0 0 30 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M20.7207 6.18211L14.9944 3.11148L3.46855 9.28678L0.579749 7.73444L14.9944 0L23.6242 4.62977L20.7207 6.18211ZM14.9996 12.3574L26.5182 6.1821L29.4216 7.73443L14.9996 15.4621L6.37724 10.8391L9.27337 9.28677L14.9996 12.3574ZM2.89613 16.572L0 15.0196V24.2656L14.4147 32V28.8953L2.89613 22.7132V16.572ZM11.5185 18.09L0 11.9147V8.81001L14.4147 16.5376V25.7904L11.5185 24.2312V18.09ZM24.2086 15.0194V11.9147L15.5788 16.5377V31.9998L18.475 30.4474V18.09L24.2086 15.0194ZM27.0969 22.7129V10.3623L30.0004 8.81V24.2653L21.3706 28.895V25.7904L27.0969 22.7129Z"
          />
        </svg>

        <div class="text-surface-900 dark:text-surface-0 text-3xl font-medium mb-4">
          Bine ai venit!
        </div>
        <span class="text-surface-600 dark:text-surface-200 font-medium leading-normal"
          >Nu ai un cont creat?</span
        >
        <Button
          label="Fa-ti unul acum!"
          variant="text"
          to="/register"
          as="router-link"
          class="p-0 pl-1"
        />
        <h2 v-if="wrongPassword" class="text-rose-600 text-sm text-center">
            {{ wrongPassword }}
        </h2>
        <Message v-if="loginError" severity="error" class="mt-3 w-full">
          {{ loginError }}
        </Message>
      </div>

      <Form
        v-slot="$form"
        :initialValues
        :resolver
        @submit="onFormSubmit"
        class="flex flex-col gap-4 w-full sm:w-60"
      >
        <div class="flex flex-col gap-1">
          <InputText name="email" type="text" placeholder="Adresa email" fluid />
          <Message
            v-if="$form.email?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
            >{{ $form.email.error.message }}</Message
          >
        </div>
        <div class="flex flex-col gap-1">
          <Password name="password" placeholder="Parola" :feedback="false" toggleMask fluid />
          <Message
            v-if="$form.password?.invalid"
            severity="error"
            size="small"
            variant="simple"
            class="text-rose-600 text-sm"
          >
            {{ $form.password.error.message }}</Message
          >
        </div>
        <Button 
          type="submit" 
          severity="secondary" 
          label="Autentificare" 
          :loading="isLoading" 
          :disabled="isLoading" 
        />
      </Form>

      <div class="flex flex-col items-center my-3">
        <div class="flex items-center">
        </div>
        <a class="font-medium no-underline ml-2 mt-3 mb-0 text-primary text-right cursor-pointer"
          >Ai uitat parola?</a
        >
      </div>
    </div>
  </div>
</template>

<script setup>
/** 
 * @file LoginView.vue
 * @description This file contains the LoginView component, which is responsible for rendering the login form and handling user authentication.
 */
import api from '../services/api'
import { ref } from 'vue'
import router from '@/router'

const wrongPassword = ref(null)
const loginError = ref(null)
const isLoading = ref(false)
const initialValues = ref({
  email: '',
  password: '',
})

/**
 * @description The resolver function is used to validate the form values before submission.
 * @param {Object} values - The form values to validate. 
 * @returns {Object} An object containing any validation errors and the form values.
 */
const resolver = ({ values }) => {
  const errors = {}
  if (!values.email) {
    errors.email = [{ message: 'Adresa de email este obligatorie' }]
  }

  if (!values.password) {
    errors.password = [{ message: 'Parola este obligatorie' }]
  }

  return {
    errors,
    values,
  }
}

/**
 * @description The login function is used to authenticate the user with the provided credentials.
 * @param {Object} credentials - The user's email and password.
 * @returns {Promise<void>} A promise that resolves when the login is successful.
 */
async function login(credentials) {
  isLoading.value = true
  loginError.value = null
  wrongPassword.value = null
  
  try {
    await api.post('/login', {
      email: credentials.email,
      password: credentials.password,
    })
    router.push('/dashboard')
  } catch (error) {
    console.error('Error logging in: ', error)
    
    // Handle error scenarios
    if (!error.response) {
      loginError.value = 'Nu s-a putut conecta la server. Verificați conexiunea la internet.'
    } else {
      const status = error.response.status
      
      if (status === 401) {
        wrongPassword.value = 'Email sau parolă incorectă'
      } else if (status >= 500) {
        loginError.value = 'Serviciul este momentan indisponibil. Vă rugăm să încercați mai târziu.'
      } else {
        loginError.value = error.response.data?.detail || 'A apărut o eroare la autentificare.'
      }
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * @description Handles form submission, validates the form and calls the login function.
 * @param {Object} e - The form submission event with form data and validation state.
 */
const onFormSubmit = (e) => {
  // e.originalEvent: Represents the native form submit event.
  // e.valid: A boolean that indicates whether the form is valid or not.
  // e.states: Contains the current state of each form field, including validity status.
  // e.errors: An object that holds any validation errors for the invalid fields in the form.
  // e.values: An object containing the current values of all form fields.
  // e.reset: A function that resets the form to its initial state.

  if (!e.valid) {
    console.log('Error validating form: ', e.errors)
    return
  }

  login(e.values)
}
</script>
