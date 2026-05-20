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
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--fiori-blue);
}

.page-header-main {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-header-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--fiori-text);
  margin: 0;
}

.page-header-subtitle {
  font-size: 14px;
  color: var(--fiori-text-light);
}

.page-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
