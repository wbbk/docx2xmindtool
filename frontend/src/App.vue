<template>
  <div id="app">
    <header class="app-header">
      <div class="header-content">
        <h1>基于AI大模型的需求文档生成测试用例系统</h1>
      </div>
    </header>
    <main>
      <router-view/>
    </main>
    <footer class="app-footer">
      <p>基于AI大模型的需求文档生成测试用例系统 &copy; 2025</p>
      <p>全部由Claude 3.5 Sonnet设计编程实现，感谢Trae支持</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

body {
  margin: 0;
  padding: 0;
}

.app-header {
  background-color: #409EFF;
  color: white;
}

.header-content {
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

main {
  flex: 1;
}

.app-footer {
  background-color: #f8f9fa;
  text-align: center;
  font-size: 14px;
  color: #6c757d;
}
</style>