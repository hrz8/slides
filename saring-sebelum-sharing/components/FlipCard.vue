<script setup lang="ts">
import { computed, ref } from 'vue'

const props = withDefaults(defineProps<{
  label: string
  verdict: 'REAL' | 'FAKE'
  reason?: string
  kind?: string
  flag?: 'my' | 'id'
  // Front visual (the item as it circulated) and back visual (fact-check proof)
  image?: string
  // Blur the front image (px), e.g. to hide a fact-checker's verdict stamp
  imageBlur?: number
  // Show a ▶ overlay on the front image (video items)
  play?: boolean
  backImage?: string
  // Source article, opened from the back of the card
  href?: string
  // The item itself as it circulated, opened from the front (must not reveal the answer)
  viewHref?: string
  // Extra link on the back, e.g. the original footage a deepfake was cut from
  extraHref?: string
  extraLabel?: string
  // Driven by slide clicks so presenter + audience windows stay in sync
  flipped?: boolean
}>(), {
  reason: '',
  kind: '',
  flipped: false,
})

// Root-relative paths ("/assets/...") need the deploy base, e.g. /slides/<deck>/ on GitHub Pages
const base = import.meta.env.BASE_URL.replace(/\/$/, '')
const withBase = (url?: string) => (url?.startsWith('/') && !url.startsWith('//') ? base + url : url)
const img = computed(() => withBase(props.image))
const backImg = computed(() => withBase(props.backImage))
const link = computed(() => withBase(props.href))
const viewLink = computed(() => withBase(props.viewHref))
const extraLink = computed(() => withBase(props.extraHref))

// Manual click toggles locally (handy when rehearsing)
const manual = ref(false)
const isFlipped = computed(() => props.flipped !== manual.value)
const isReal = computed(() => props.verdict === 'REAL')
</script>

<template>
  <div class="flip-card" :class="{ flipped: isFlipped }" @click="manual = !manual">
    <div class="flip-inner">
      <div class="face front">
        <div class="flex items-center justify-between w-full text-sm opacity-80">
          <span v-if="kind" class="uppercase tracking-wider">{{ kind }}</span>
          <span v-if="flag" :class="flag === 'my' ? 'i-twemoji-flag-malaysia' : 'i-twemoji-flag-indonesia'" class="text-2xl" />
        </div>
        <div v-if="image" class="front-media">
          <img :src="img" alt="" class="front-img" :style="imageBlur ? { filter: `blur(${imageBlur}px) grayscale(1) brightness(0.8)`, transform: 'scale(1.08)' } : undefined">
          <span v-if="play" class="play i-carbon-play-filled-alt" />
        </div>
        <div class="flex-1 flex items-center justify-center text-center leading-snug" :class="{ 'caption': image }">
          <slot>{{ label }}</slot>
        </div>
        <div class="text-sm flex items-center gap-2">
          <span class="opacity-60 flex items-center gap-1"><span class="i-twemoji-thinking-face" /> Real or fake?</span>
          <a v-if="viewHref" :href="viewLink" target="_blank" rel="noopener" class="view" @click.stop>Open ↗</a>
        </div>
      </div>
      <div class="face back" :class="isReal ? 'is-real' : 'is-fake'">
        <div class="verdict">
          <span :class="isReal ? 'i-carbon-checkmark-filled' : 'i-carbon-close-filled'" />
          {{ verdict }}
        </div>
        <a v-if="backImage && href" :href="link" target="_blank" rel="noopener" class="back-link" @click.stop>
          <img :src="backImg" alt="" class="back-img">
        </a>
        <img v-else-if="backImage" :src="backImg" alt="" class="back-img">
        <div class="reason">{{ reason }}</div>
        <div class="flex gap-3">
          <a v-if="href" :href="link" target="_blank" rel="noopener" class="source" @click.stop>Source ↗</a>
          <a v-if="extraHref" :href="extraLink" target="_blank" rel="noopener" class="source" @click.stop>{{ extraLabel || 'More ↗' }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flip-card {
  perspective: 1000px;
  cursor: pointer;
  height: 100%;
  min-height: 15rem;
}
.flip-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.7s cubic-bezier(0.4, 0.2, 0.2, 1);
  transform-style: preserve-3d;
}
.flipped .flip-inner {
  transform: rotateY(180deg);
}
.face {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border-radius: 1rem;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  font-size: 1.25rem;
}
.front {
  background: var(--ss-card);
  border: 2px solid var(--ss-border);
}
.back {
  transform: rotateY(180deg);
  justify-content: center;
  color: #fff;
}
.back.is-real {
  background: linear-gradient(160deg, var(--ss-real), #0f5132);
}
.back.is-fake {
  background: linear-gradient(160deg, var(--ss-fake), #7f1d1d);
}
.front-media {
  position: relative;
  width: 100%;
  flex: 1 1 0;
  min-height: 0;
  overflow: hidden;
  border-radius: 0.6rem;
  margin: 0.5rem 0 0.4rem;
}
.front-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top;
}
.play {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 3rem;
  height: 3rem;
  transform: translate(-50%, -50%);
  color: #fff;
  background-color: #fff;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.6));
}
.caption {
  flex: 0 0 auto;
  font-size: 0.95rem;
  margin-bottom: 0.35rem;
}
.back-img {
  width: 100%;
  height: auto;
  max-height: 48%;
  flex: none;
  object-fit: contain;
  background: #fff;
  border-radius: 0.6rem;
  margin: 0.5rem 0;
  border: 2px solid rgba(255, 255, 255, 0.35);
}
.back-link {
  display: contents;
  border: none !important;
}
.reason {
  font-size: 1rem;
  line-height: 1.3;
  text-align: center;
  margin-top: 0.25rem;
}
.view {
  font-weight: 600;
  color: var(--ss-accent) !important;
  border-bottom: 1px solid currentColor !important;
}
.source {
  margin-top: 0.35rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.6) !important;
}
.verdict {
  font-family: var(--slidev-theme-font-heading, 'Space Grotesk');
  font-size: 2.5rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
