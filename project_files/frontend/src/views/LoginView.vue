<template>
  <div
    class="flex flex-col items-center justify-center bg-surface-50 dark:bg-surface-950 px-6 py-20 md:px-12 lg:px-20 h-dvh"
  >
    <div
      class="flex flex-col items-center justify-center bg-surface-0 dark:bg-surface-900 p-6 shadow rounded-border w-full lg:w-6/12 mx-auto"
    >
      <div class="text-center mb-8">
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
        <Button type="submit" severity="secondary" label="Autentificare" />
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
import { Form } from '@primevue/forms'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import api from '../services/api'
import { ref } from 'vue'
import router from '@/router'
import Message from 'primevue/message'


const initialValues = ref({
  email: '',
  password: '',
})

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

async function login(credentials) {
  try {
    await api.post('/login', {
      email: credentials.email,
      password: credentials.password,
    })
    router.push('/dashboard')
  } catch {
    console.log('Login failed')
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
    console.log('Error adding vaccine: ', e.errors)
    return
  }

  login(e.values)
}
</script>
