<template>
  <el-container class="app-container">
    <el-aside width="200px">
      <div class="logo-area">DocuMind</div>
      <el-menu router :default-active="$route.path" class="el-menu-vertical">
        <el-menu-item index="/documents">
          <el-icon><document /></el-icon>
          <span>文档管理</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><chat-dot-round /></el-icon>
          <span>研讨对话</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { Document, ChatDotRound } from '@element-plus/icons-vue'
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
.app-container {
  height: 100vh;
}
.el-menu-vertical {
  height: calc(100% - 60px);
}
.logo-area {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-weight: bold;
  font-size: 20px;
  border-bottom: 1px solid #eee;
  border-right: 1px solid #dcdfe6;
}
</style>
