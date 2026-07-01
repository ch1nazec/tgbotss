import { defineStore } from "pinia";
import api from "@/services/api";
import { ref } from "vue";


export const authVerifyTGStore = defineStore('verifyTg', () => {
    const responseUser = ref(null);
    const isLoading = ref(false);
    
    const authUserTG = async (initData) => {
    try {
      if (responseUser.value) return
      if (isLoading.value) return

      isLoading.value = true
      const response = await api.post(
        '/users/auth/verify/', 
        {},
        {
          headers: {
            'Authorization': `Bearer ${initData}`,
            'Content-Type': 'application/json'}
        });
      
      responseUser.value = response;
    } catch (error) {
      console.error(`Authentication error: ${error.response?.data?.detail || error.message}`);
    }
    finally {
      isLoading.value = false}
}
    return {responseUser, authUserTG, isLoading}
});