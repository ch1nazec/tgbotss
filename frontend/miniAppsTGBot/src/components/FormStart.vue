<script setup>
import Field from '@/components/Field.vue';
import { ref } from 'vue';
import { authVerifyTGStore } from '@/stores/authStoreTG';


const verifyTgStore = authVerifyTGStore()

const emit = defineEmits(['submit'])

const last_name = ref('')
const first_name = ref('')
const third_name = ref('')


const onSubmit = () => {
    emit('submit', {
        last_name: last_name.value,
        first_name: first_name.value,
        third_name: third_name.value,
        telegram_id: verifyTgStore.responseUser?.telegram_id
    })
}
</script>

<template>
    <form @submit.prevent="onSubmit" class="formstartget">
        <Field v-model="last_name" placeholder="Фамилия"></Field>
        <Field v-model="first_name" placeholder="Имя"></Field>
        <Field v-model="third_name" placeholder="Отчество (при наличии)"></Field>

        <button class="button-next" type="submit">Продолжить</button>  
    </form>
</template>

<style>
.formstartget {
    width: 60%;
    height: 60%;
    
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 5px;
}



.button-next {
    border: 0px;
    cursor: pointer;

    padding: 10px 15px;

    transition: background-color 0.3s ease, transform 0.2s ease;
    &:hover {
        background-color: #7aff8a;}
}
</style>