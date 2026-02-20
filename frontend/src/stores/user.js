import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore('user', () => {
  const id = ref(0)
  const username = ref('')
  const photo = ref('')
  const profile = ref('')
  const accessToken = ref('')
  const hasPulledUserInfo = ref(false)  // 是否已经从后端拉取过用户信息了

  function isLogin() {
    return !!accessToken.value  // 必须带value!!!!!!!!!
  }

  function setAccessToken(token) {
    accessToken.value = token
  }

  function setUserInfo(data) {
    id.value = data.user_id
    username.value = data.username
    photo.value = data.photo
    profile.value = data.profile
  }

  function logout() {
    id.value = 0
    username.value = ''
    photo.value = ''
    profile.value = ''
    accessToken.value = ''
  }

  function setHasPulledUserInfo(value) {
    hasPulledUserInfo.value = value
  }

  return {
    id,
    username,
    photo,
    profile,
    accessToken,  // 千万不要忘了！！！！
    hasPulledUserInfo,
    isLogin,
    setAccessToken,
    setUserInfo,
    logout,
    setHasPulledUserInfo,
  }
})
