<script setup>
import { onMounted, provide } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useMiniApp } from 'vue-tg';
import { authVerifyTGStore } from './stores/authStoreTG';


const route = useRoute()
const VerifyTG = authVerifyTGStore()

const miniApp = useMiniApp()
const initData = miniApp.initData

onMounted(async () => {
  await VerifyTG.authUserTG(initData)
})
</script>

<template>
  <div class="wrapper">
      <div class="content">
        <RouterView />
      </div>
  </div>
  
</template>

<style>

</style>