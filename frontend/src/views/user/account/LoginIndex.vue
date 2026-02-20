<script setup>
import { ref } from 'vue';
import { useUserStore } from "@/stores/user";
import { useRouter } from "vue-router";
import api from "@/js/http/api.js";

const username = ref('')
const password = ref('')
const errInfo = ref('')

const user = useUserStore()
const router = useRouter()

// 处理登录函数
async function handleLogin() {
  errInfo.value = ''
  if (!username.value.trim()) {
    errInfo.value = '请输入用户名'
  } else if (!password.value.trim()) {
    errInfo.value = '请输入密码'
  } else {
    try {
      const response = await api.post('/api/user/account/login/', {
        username: username.value,
        password: password.value
      })
      const data = response.data
      if (data.result === 'success') {
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        await router.push({ name: 'homepage-index' })
      }
      else {
        errInfo.value = data.result || '登录失败，请稍后再试'
      }
    } catch (error) {
      console.error('登录请求失败:', error)
    }
  }
}

</script>

<template>
  <div class="flex justify-center mt-30">
    <form @submit.prevent="handleLogin" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <label class="label">用户名</label>
      <input v-model="username" type="text" class="input" placeholder="用户名" />

      <label class="label">密码</label>
      <input v-model="password" type="password" class="input" placeholder="密码" />

      <p v-if="errInfo" class="text-sm text-red-500 mt-1">{{ errInfo }}</p>
      <button class="btn btn-neutral mt-4">登录</button>
      <div class="flex justify-end">
        <RouterLink :to="{name: 'user-account-register-index'}" class="btn btn-sm btn-ghost text-gray-500">
          注册
        </RouterLink>
      </div>
    </form>
  </div>

</template>

<style scoped>

</style>