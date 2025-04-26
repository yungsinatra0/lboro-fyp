// Basic setup for a Vue.js application using PrimeVue components and Pinia for state management
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import ConfirmationService from 'primevue/confirmationservice'
import Primevue from 'primevue/config'
import Tooltip from 'primevue/tooltip'
import App from './App.vue'
import router from './router'
import "./base.css"

// Importing Primevue components in the main file so they can be used globally
// This is a common practice in Vue.js applications to keep the code organized and maintainable
import Button from 'primevue/button'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Stepper from 'primevue/stepper'
import StepList from 'primevue/steplist'
import StepPanels from 'primevue/steppanels'
import SelectButton from 'primevue/selectbutton'
import Slider from 'primevue/slider'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'
import InputOtp from 'primevue/inputotp'
import Message from 'primevue/message'
import DatePicker from 'primevue/datepicker'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import ProgressSpinner from 'primevue/progressspinner'
import DataView from 'primevue/dataview'
import Select from 'primevue/select'
import Menu from 'primevue/menu'
import MultiSelect from 'primevue/multiselect'
import ConfirmDialog from 'primevue/confirmdialog'
import { Form } from '@primevue/forms'
import Textarea from 'primevue/textarea'
import Image from 'primevue/image'
import Menubar from 'primevue/menubar'
import Password from 'primevue/password'
import FileUpload from 'primevue/fileupload'
import ToggleSwitch from 'primevue/toggleswitch'
import InputNumber from 'primevue/inputnumber'
import IftaLabel from 'primevue/iftalabel'
import RadioButton from 'primevue/radiobutton'
import RadioButtonGroup from 'primevue/radiobuttongroup'
import ToggleButton from 'primevue/togglebutton'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Checkbox from 'primevue/checkbox'
import CheckboxGroup from 'primevue/checkboxgroup'

// Initialising the Pinia store
const pinia = createPinia()

// Creating the Vue application instance
const app = createApp(App)

// Adding the Pinia store, router, Primevue and confirmation service (confirmation pop-ups) to the Vue application
app.use(pinia)
app.use(router)
app.use(Primevue, {
    theme: 'none',
    ripple: true,
})
app.use(ConfirmationService)

// Adding primevue components to the Vue application
// This allows us to use these components in any part of the application without needing to import them in each file
app.component('Button', Button) 
app.component('Card', Card)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Tag', Tag)
app.component('Dialog', Dialog)
app.component('Stepper', Stepper)
app.component('StepList', StepList)
app.component('StepPanels', StepPanels)
app.component('SelectButton', SelectButton)
app.component('Slider', Slider)
app.component('Step', Step)
app.component('StepPanel', StepPanel)
app.component('InputOtp', InputOtp)
app.component('Message', Message)
app.component('DatePicker', DatePicker)
app.component('InputText', InputText)
app.component('IconField', IconField)
app.component('InputIcon', InputIcon)
app.component('ProgressSpinner', ProgressSpinner)
app.component('DataView', DataView)
app.component('Select', Select)
app.component('Menu', Menu)
app.component('MultiSelect', MultiSelect)
app.component('ConfirmDialog', ConfirmDialog)
app.component('Form', Form)
app.component('Textarea', Textarea)
app.component('Image', Image)
app.component('Menubar', Menubar)
app.component('Password', Password)
app.component('FileUpload', FileUpload)
app.component('ToggleSwitch', ToggleSwitch)
app.component('InputNumber', InputNumber)
app.component('IftaLabel', IftaLabel)
app.component('RadioButton', RadioButton)
app.component('RadioButtonGroup', RadioButtonGroup)
app.component('ToggleButton', ToggleButton)
app.component('Tabs', Tabs)
app.component('TabList', TabList)
app.component('Tab', Tab)
app.component('TabPanels', TabPanels)
app.component('TabPanel', TabPanel)
app.component('Checkbox', Checkbox)
app.component('CheckboxGroup', CheckboxGroup)

// Registering the tooltip directive globally
// This allows us to use tooltips in any part of the application
app.directive('tooltip', Tooltip)
app.mount('#app')
