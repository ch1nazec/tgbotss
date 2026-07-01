<script setup>
import { onMounted, ref } from 'vue';
import { authVerifyTGStore } from '@/stores/authStoreTG';
import { useMiniApp } from 'vue-tg/latest';

const miniApp = useMiniApp()
const authenticatedUser = ref(null);

const authStore = authVerifyTGStore();

onMounted(async () => {

    if (miniApp.initData) {
      const data = miniApp.initData
      await authStore.authUserTG(data);}

      authenticatedUser.value = authStore;
  }
);
</script>

<template>
  <main>
    <div v-if="!authenticatedUser">Загрузка...</div>
    <div v-else>
      {{ authStore.responseUser }}
    </div>
  </main>
</template>