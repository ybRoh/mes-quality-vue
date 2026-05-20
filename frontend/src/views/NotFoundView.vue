<template>
  <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; color: #606266;">
    <h1 style="font-size: 72px; margin: 0; color: #909399;">404</h1>
    <p style="font-size: 18px; margin: 16px 0;">페이지를 찾을 수 없습니다</p>
    <el-button type="primary" @click="$router.push('/')">대시보드로 이동</el-button>
  </div>
</template>
