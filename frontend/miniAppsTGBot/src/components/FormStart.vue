<script setup>
import Field from '@/components/Field.vue';
</script>

<template>
    <form action="" class="formstartget">
        <Field placeholder="Фамилия"></Field>
        <Field placeholder="Имя"></Field>
        <Field placeholder="Отчество (при наличии)"></Field>
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
</style>