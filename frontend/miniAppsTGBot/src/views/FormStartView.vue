<script setup>
import FormStart from '@/components/FormStart.vue';
import { authVerifyTGStore } from '@/stores/authStoreTG';


const authStore = authVerifyTGStore();
</script>

<template>
    <div class="main-start">
        <img class="main-start__avatar" :src="authStore.responseUser.photo" alt="">
        <p class="main-start__hellotext">Привет!</p>
        <FormStart />
    </div>
</template>

<style>
.main-start {
    display: flex;

    justify-content: center;
    align-items: center;
    
    min-height: 100vh;
    box-sizing: border-box;
    padding: 20px;

    flex-direction: column;
    gap: 15px;
}

.main-start__avatar {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    object-fit: cover;
}

.main-start__hellotext {
    font-size: 40px;
}
</style>