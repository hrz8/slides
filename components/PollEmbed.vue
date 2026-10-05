<script setup lang="ts">
import QRCode from 'qrcode'
import { computed, onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{
  url?: string
  title?: string
  // Show only the QR + link (safer on a shared screen / in PDF export)
  qrOnly?: boolean
}>(), {
  url: 'POLL_URL_HERE',
  title: 'Vote now',
  qrOnly: false,
})

const isPlaceholder = computed(() => !props.url || props.url === 'POLL_URL_HERE')
const qr = ref('')

onMounted(async () => {
  if (isPlaceholder.value)
    return
  qr.value = await QRCode.toDataURL(props.url, { margin: 1, width: 320, color: { dark: '#0b1020', light: '#ffffff' } })
})
</script>

<template>
  <div class="grid gap-6 h-full" :class="qrOnly ? 'grid-cols-1 place-items-center' : 'grid-cols-[1fr_auto]'">
    <div v-if="!qrOnly" class="frame">
      <iframe v-if="!isPlaceholder" :src="url" :title="title" class="w-full h-full rounded-xl" allow="clipboard-write" />
      <div v-else class="placeholder">
        [PLACEHOLDER: poll embed — TODO: replace POLL_URL_HERE with Slido/Mentimeter link]
      </div>
    </div>
    <div class="flex flex-col items-center justify-center gap-3 text-center">
      <div class="qr">
        <img v-if="qr" :src="qr" alt="Poll QR code" class="w-full h-full">
        <div v-else class="text-base opacity-70 p-4">QR appears once<br>POLL_URL_HERE is set</div>
      </div>
      <div class="text-lg font-bold">{{ title }}</div>
      <div class="text-sm opacity-70 break-all max-w-56">{{ isPlaceholder ? 'POLL_URL_HERE' : url }}</div>
      <div class="text-sm opacity-70">Remote? Use the link in chat</div>
    </div>
  </div>
</template>

<style scoped>
.frame {
  min-height: 18rem;
  border-radius: 0.75rem;
  overflow: hidden;
  background: var(--ss-card);
}
.placeholder {
  height: 100%;
  min-height: 18rem;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  border: 2px dashed var(--ss-pause);
  border-radius: 0.75rem;
  color: var(--ss-pause);
  font-size: 1.1rem;
}
.qr {
  width: 13rem;
  height: 13rem;
  background: #fff;
  color: #0b1020;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
</style>
