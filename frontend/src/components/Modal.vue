<script setup>
import { onUnmounted, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, required: true },
  title: { type: String, required: true },
  size: { type: String, default: '' }, // '' | 'lg' | 'xl'
})
const emit = defineEmits(['close'])

function onKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

watch(
  () => props.show,
  (isShown) => {
    if (isShown) {
      window.addEventListener('keydown', onKeydown)
    } else {
      window.removeEventListener('keydown', onKeydown)
    }
  }
)

onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div v-if="show" class="modal d-block" tabindex="-1" style="background: rgba(0, 0, 0, 0.5)">
    <div
      class="modal-dialog modal-dialog-scrollable"
      :class="size ? `modal-${size}` : ''"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ title }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Go back</button>
        </div>
      </div>
    </div>
  </div>
</template>
