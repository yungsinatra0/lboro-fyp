import { createPinia } from 'pinia'
import { createApp } from 'vue'
import ConfirmationService from 'primevue/confirmationservice'
import Primevue from 'primevue/config'
import Tooltip from 'primevue/tooltip'
import App from './App.vue'
import router from './router'
import "./base.css";

const pinia = createPinia();

const app = createApp(App);
app.use(pinia);
app.use(router);
app.use(Primevue, {
    theme: 'none',
    ripple: true,
});
app.use(ConfirmationService);
app.directive('tooltip', Tooltip);
app.mount('#app')
