<template>
  <div class="page-header">
    <div class="page-header-main">
      <h1 class="page-header-title">{{ title }}</h1>
      <span v-if="subtitle" class="page-header-subtitle">{{ subtitle }}</span>
    </div>
    <div class="page-header-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--qms-primary);
}

.page-header-main {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.page-header-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--qms-text-primary);
  margin: 0;
}

.page-header-subtitle {
  font-size: 12px;
  color: var(--qms-text-secondary);
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
