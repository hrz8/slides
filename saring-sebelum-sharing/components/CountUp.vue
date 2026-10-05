<script setup lang="ts">
import { onSlideEnter, onSlideLeave, useSlideContext } from '@slidev/client'
import { computed, onMounted, ref } from 'vue'

const props = withDefaults(defineProps<{
  to: number
  duration?: number
  suffix?: string
  prefix?: string
}>(), {
  duration: 2000,
  suffix: '',
  prefix: '',
})

const { $renderContext } = useSlideContext()
const value = ref(0)
let raf = 0

// Only animate in the live slide view; print/overview/export show the final number
const animated = computed(() => ['slide', 'presenter'].includes($renderContext.value))

function run() {
  cancelAnimationFrame(raf)
  if (!animated.value) {
    value.value = props.to
    return
  }
  const start = performance.now()
  const tick = (now: number) => {
    const t = Math.min((now - start) / props.duration, 1)
    const eased = 1 - (1 - t) ** 3
    value.value = Math.round(props.to * eased)
    if (t < 1)
      raf = requestAnimationFrame(tick)
  }
  value.value = 0
  raf = requestAnimationFrame(tick)
}

onMounted(() => {
  if (!animated.value)
    value.value = props.to
})
onSlideEnter(run)
onSlideLeave(() => cancelAnimationFrame(raf))

const display = computed(() => `${props.prefix}${value.value.toLocaleString('en-US')}${props.suffix}`)
</script>

<template>
  <span class="tabular-nums">{{ display }}</span>
</template>
