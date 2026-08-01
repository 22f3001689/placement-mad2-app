<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  defaultOpen: { type: Boolean, default: true },
})

const open = ref(props.defaultOpen)
</script>

<template>
  <div class="card mb-3">
    <div
      class="card-header d-flex justify-content-between align-items-center"
      style="cursor: pointer"
      @click="open = !open"
    >
      <strong>{{ title }}</strong>
      <span>{{ open ? '▲' : '▼' }}</span>
    </div>
    <div class="card-body" v-show="open">
      <slot />
    </div>
  </div>
</template>
