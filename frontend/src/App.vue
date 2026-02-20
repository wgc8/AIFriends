<script setup>
import NavBar from "@/components/navbar/NavBar.vue";
import { onMounted } from "vue";
import { useUserStore } from "@/stores/user.js";
import api from "@/js/http/api";
import { useRoute, useRouter } from "vue-router";

const user = useUserStore()
const route = useRoute()
const router = useRouter()

onMounted(async () => {
    try {
      const res = await api.get('/api/user/account/get_user_info/')
      const data = res.data
      if (data.result === 'success') {
        user.setUserInfo(data)
      }
    } catch (err) {
      console.log(err)
    } finally {
      // 无论成功与否，都将加载状态设为false，以显示页面
      user.setHasPulledUserInfo(true)
      // 如果用户未登录但访问了需要登录的页面，则重定向到登录页
      if (route.meta.needLogin && !user.isLogin()) {
        await router.replace({ name: 'user-account-login-index' })
      }
    } 
})

</script>

<template>
  <NavBar>
    <RouterView />
  </NavBar>
</template>

<style scoped>

</style>
