import { createRouter, createWebHistory } from 'vue-router'
import HomepageIndex from '@/views/homepage/HomepageIndex.vue'
import FriendIndex from '@/views/friend/FriendIndex.vue'
import CreateIndex from '@/views/create/CreateIndex.vue'
import NotFoundIndex from '@/views/error/NotFoundIndex.vue'
import LoginIndex from '@/views/user/account/LoginIndex.vue'
import RegisterIndex from '@/views/user/account/RegisterIndex.vue'
import SpaceIndex from '@/views/user/space/SpaceIndex.vue'
import ProfileIndex from '@/views/user/profile/ProfileIndex.vue'
import { useUserStore } from "@/stores/user.js";

import UpdateCharacter from '@/views/create/character/UpdateCharacter.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      paht: '/',
      component: HomepageIndex,
      name: 'homepage-index',
      meta: { needLogin: false },  // 首页不需要登录
    },
    {
      path: '/friend',
      component: FriendIndex,
      name: 'friend-index',
      meta: { needLogin: true },  // 交友页需要登录
    },
    {
      path: '/create',
      component: CreateIndex,
      name: 'create-index',
      meta: { needLogin: true },  // 创建页需要登录
    },
    {
      path: '/create/character/update/:character_id/',
      component: UpdateCharacter,
      name: 'update-character',
      meta: { needLogin: true },  // 创建页需要登录
    },
    {
      path: '/404/',
      component: NotFoundIndex,
      name: '404',
      meta: { needLogin: false },  // 404页不需要登录
    },
    {
      path: '/user/account/login/',
      component: LoginIndex,
      name: 'user-account-login-index',
      meta: { needLogin: false },  // 登录页不需要登录
    },
    {
      path: '/user/account/register/',
      component: RegisterIndex,
      name: 'user-account-register-index',
      meta: { needLogin: false },  // 注册页不需要登录
    },
    {
      path: '/user/space/:user_id/',
      component: SpaceIndex,
      name: 'user-space-index',
      meta: { needLogin: false },  // 个人空间页不需要登录
    },
    {
      path: '/user/profile/',
      component: ProfileIndex,
      name: 'user-profile-index',
      meta: { needLogin: true },  // 编辑资料页需要登录
    },
    {
      path: '/:pathMatch(.*)*',
      component: NotFoundIndex,
      name: 'not-found',
      meta: { needLogin: false },  // 404页不需要登录
    },
  ],
})

// 全局前置守卫：根据路由meta中的needLogin字段来判断是否需要登录
router.beforeEach((to, from) => {
  const user = useUserStore()
  if (to.meta.needLogin && user.hasPulledUserInfo && !user.isLogin()) {
    return { name: 'user-account-login-index' }
  }
  return true
})
export default router
