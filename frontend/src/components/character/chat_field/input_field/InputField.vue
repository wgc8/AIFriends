<script setup>
import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {useTemplateRef, ref, onMounted} from "vue";
import api from "@/js/http/api.js";
import streamApi from "@/js/http/streamApi.js";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";

const props = defineProps(['friendId'])
const emit = defineEmits(['pushBackMessage', 'addToLastMessage'])
const inputRef = useTemplateRef('input-ref')
const message = ref('')
// 防止重复发送消息
let processId = 0
const showMic = ref(false)


function focus() {
  inputRef.value.focus()
}
// 同步接收消息
async function handleSend(event, audio_msg) {
  let content
  if (audio_msg) {
    content = audio_msg.trim()
  } else {
    content = message.value.trim()
  }
  if (!content) return
  // 实现根据版本号，进行输出打断
  const curId = ++ processId
  message.value = ''
  try {
    const res = await api.post('/api/friend/message/chat/', {
      friend_id: props.friendId,
      message: content,
    })
    console.log(res.data)
  }catch (err) {
    console.log(err)
  }
}

async function handleStreamSend(event, audio_msg) {
  let content
  if (audio_msg) {
    content = audio_msg.trim()
  } else {
    content = message.value.trim()
  }
  if (!content) return
  const curId = ++ processId
  if (isProcessing) return
  message.value = ''
  // 先把用户消息添加到聊天记录中，再发送请求
  emit('pushBackMessage', {role: 'user', content: content, id: crypto.randomUUID()})
  emit('pushBackMessage', {role: 'ai', content: '', id: crypto.randomUUID()})
  try {
    const res = await streamApi('/api/friend/message/chat/', {
      body: {
        friend_id: props.friendId,
        message: content,
      },
       onmessage(data, isDone) {
        // 输出打断
        if (curId !== processId) return

        if (data.content) {
          // 在预生成ai的空消息的基础上追加内容
          emit('addToLastMessage', data.content)
        }
      },
      onerror(err) {
      },
    })
  }catch (err) {
    console.log(err)
  }
}

function close() {
  ++ processId
  showMic.value = false
}

function handleStop() {
  ++ processId
}

defineExpose({
  focus,
  close,
})

</script>

<template>
  <form v-if="!showMic" @submit.prevent="handleStreamSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        ref="input-ref"
        v-model="message"
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
        type="text"
        placeholder="文本输入..."
    >
    <div @click="handleStreamSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon />
    </div>
    <div @click="showMic = true" class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon />
    </div>
  </form>
  <Microphone 
    v-else
    @close="showMic = false"
    @send="handleStreamSend"
    @stop="handleStop"
  />

</template>

<style scoped>

</style>
