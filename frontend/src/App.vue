<template>
  <div class="chat-wrap">
    <h2>✨ GGM's AI Chat</h2>
    <div class="chat-window" ref="chatWindow">
      <div v-for="(msg, idx) in chatHistory" :key="idx" :class="['msg-box', msg.role]">
        <div class="text">{{ msg.text }}</div>
      </div>
    </div>
    <div class="input-wrap">
      <input v-model="userInput" @keyup.enter="send" placeholder="메시지를 입력하세요..." />
      <button @click="send">보내기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const userInput = ref('')
const chatHistory = ref([])
const chatWindow = ref(null) // 자동 스크롤을 위한 참조

// 스크롤을 항상 하단으로 내리는 함수
const scrollToBottom = async () => {
  await nextTick()
  if (chatWindow.value) {
    chatWindow.value.scrollTop = chatWindow.value.scrollHeight
  }
}

const send = async () => {
  if (!userInput.value.trim()) return

  // 1. 내가 보낸 메시지 추가
  const userText = userInput.value
  chatHistory.value.push({ role: 'user', text: userText })
  userInput.value = ''
  scrollToBottom()

  // 2. AI 답변을 담을 '빈' 박스를 미리 하나 만듭니다.
  chatHistory.value.push({ role: 'ai', text: '' })
  const aiMsgIdx = chatHistory.value.length - 1

  try {
    // 3. fetch를 사용하여 백엔드 스트리밍 엔드포인트 호출
    const response = await fetch('http://127.0.0.1:8000/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText })
    })

    if (!response.ok) throw new Error('서버 연결 실패')

    // 4. 스트림 데이터를 읽기 위한 준비
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    // 5. 데이터를 받을 때마다 실시간으로 누적 (reactive proxy를 통해 접근)
    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      for (const line of chunk.split('\n')) {
        if (line.startsWith('data: ') && line !== 'data: [DONE]') {
          chatHistory.value[aiMsgIdx].text += line.slice(6)
        }
      }
      scrollToBottom()
    }
  } catch (error) {
    console.error("Streaming Error:", error)
    chatHistory.value[aiMsgIdx].text = '서버 연결에 실패했어요. 파이썬 서버 상태를 확인하세요!'
  }
}
</script>

<style scoped>
.chat-wrap { max-width: 600px; margin: 50px auto; font-family: sans-serif; }
.chat-window { border: 1px solid #eee; height: 500px; overflow-y: auto; padding: 20px; background: #fcfcfc; display: flex; flex-direction: column; gap: 15px; border-radius: 10px; }
.msg-box { padding: 10px 15px; border-radius: 15px; max-width: 75%; line-height: 1.5; word-break: break-all; }
.user { align-self: flex-end; background: #4f46e5; color: white; }
.ai { align-self: flex-start; background: #e5e7eb; color: #1f2937; }
.input-wrap { display: flex; margin-top: 15px; gap: 10px; }
input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; outline: none; }
button { padding: 10px 25px; background: #4f46e5; color: white; border: none; border-radius: 8px; cursor: pointer; }
</style>