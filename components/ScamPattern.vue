<script setup lang="ts">
withDefaults(defineProps<{
  // Number of revealed steps (0–4); pass `$clicks` from the slide
  step?: number
}>(), {
  step: 0,
})

const steps = [
  { icon: 'i-twemoji-star-struck', title: 'Famous face', sub: 'Leader / celebrity (often deepfaked)' },
  { icon: 'i-twemoji-money-bag', title: 'Free money', sub: '"Aid", "investment", "guaranteed returns"' },
  { icon: 'i-mdi-whatsapp', title: 'WhatsApp number', sub: '"Contact my admin to claim"' },
]
</script>

<template>
  <div class="flex items-center justify-center gap-3">
    <template v-for="(s, i) in steps" :key="s.title">
      <div class="step" :class="{ on: step > i }">
        <span :class="s.icon" class="text-5xl" />
        <div class="font-bold text-2xl mt-2">{{ s.title }}</div>
        <div class="text-base opacity-75 mt-1 leading-snug">{{ s.sub }}</div>
      </div>
      <div class="op" :class="{ on: step > i + 1 || (i === 2 && step > 3) }">
        {{ i < 2 ? '+' : '=' }}
      </div>
    </template>
    <div class="step scam" :class="{ on: step > 3 }">
      <span class="i-twemoji-stop-sign text-5xl" />
      <div class="font-black text-4xl mt-2 tracking-wider">SCAM</div>
      <div class="text-base mt-1">Every single time</div>
    </div>
  </div>
</template>

<style scoped>
.step {
  width: 12rem;
  min-height: 13rem;
  padding: 1rem;
  border-radius: 1rem;
  border: 2px dashed var(--ss-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  opacity: 0.15;
  transform: translateY(16px) scale(0.95);
  transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.step.on {
  opacity: 1;
  transform: none;
  border-style: solid;
  border-color: var(--ss-pause);
  background: var(--ss-card);
}
.step.scam.on {
  border-color: var(--ss-fake);
  background: var(--ss-fake);
  color: #fff;
  box-shadow: 0 0 40px rgba(239, 68, 68, 0.5);
  animation: pulse 1.2s ease-in-out 2;
}
.op {
  font-size: 3rem;
  font-weight: 800;
  opacity: 0.15;
  transition: opacity 0.4s;
}
.op.on {
  opacity: 1;
}
@keyframes pulse {
  50% { transform: scale(1.06); }
}
</style>
