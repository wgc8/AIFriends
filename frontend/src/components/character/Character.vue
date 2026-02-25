<script setup>
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import { useRouter } from "vue-router";

import {useUserStore} from "@/stores/user.js";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import ChatField from "@/components/character/chat_field/ChatField.vue";

const props = defineProps(['character', 'canEdit', 'canRemoveFriend', 'friendId'])
const emit = defineEmits(['remove'])
const isHover = ref(false)
const user = useUserStore()
const router = useRouter()

async function handleRemoveCharacter() {
  try {
    const res = await api.post('/api/create/character/remove/', {
      character_id: props.character.id,
    })
    if (res.data.result === 'success') {
      emit('remove', props.character.id)
    }
  } catch (err) {
  }
}

const chatFieldRef = useTemplateRef('chat-field-ref')
const friend = ref(null)

async function openChatField() {
  if (!user.isLogin()) {
    await router.push({
      name: 'user-account-login-index'
    })
  } else {
    try {
      const res = await api.post('/api/friend/get_or_create/', {
        character_id: props.character.id,
      })
      const date = res.data
      if (date.result === 'success') {
        friend.value = date.friend
        chatFieldRef.value.showModal()
      }
    } catch (err) {
      console.error(err)
    }
  }
}

async function handleRemoveFriend() {
  try {
    const res = await api.post('/api/friend/remove/', {
      friend_id: props.friendId,
    })
    if (res.data.result === 'success') {
      emit('remove', props.friendId)
    }
  } catch (err) {
  }
}
</script>

<template>
  <div>
    <div class="avatar cursor-pointer" @click="openChatField" @mouseover="isHover=true" @mouseout="isHover=false">
      <div class="w-60 h-100 rounded-2xl relative">
        <img :src="character.background_image" class="transition-transform duration-300" :class="{'scale-120': isHover}" alt="">
        <div class="absolute left-0 top-50 w-60 h-50 bg-linear-to-t from-black/40 to-transparent"></div>

        <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-0 top-50">
          <RouterLink @click.stop :to="{name: 'update-character', params: {character_id: character.id}}" class="btn btn-circle btn-ghost bg-transparent">
            <UpdateIcon />
          </RouterLink>
          <!-- 删除角色 -->
          <button @click.stop="handleRemoveCharacter" class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon />
          </button>
        </div>
        <!-- 删除好友关系 -->
        <div v-if="canRemoveFriend" class="absolute right-0 top-50">
          <!-- click.stop 不再往父组件传递点击事件，避免触发打开聊天框的事件 -->
          <button @click.stop="handleRemoveFriend" class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon />
          </button>
        </div>

        <div class="absolute left-4 top-54 avatar">
          <div class="w-16 rounded-full ring-3 ring-white">
            <img :src="character.photo" alt="">
          </div>
        </div>
        <div class="absolute left-24 right-4 top-58 text-white font-bold line-clamp-1 break-all">
          {{ character.name }}
        </div>
        <div class="absolute left-4 right-4 top-72 text-white line-clamp-4 break-all">
          {{ character.profile }}
        </div>
      </div>
    </div>
    <RouterLink :to="{name: 'user-space-index', params: {user_id: character.author.user_id}}" class="flex items-center mt-4 gap-2 w-60">
      <div class="avatar">
        <div class="w-7 rounded-full">
          <img :src="character.author.photo" alt="">
        </div>
      </div>
      <div class="text-sm line-clamp-1 break-all">{{ character.author.username }}</div>
    </RouterLink>
    <ChatField ref="chat-field-ref" :friend="friend" />
  </div>
</template>

<style scoped>

</style>
