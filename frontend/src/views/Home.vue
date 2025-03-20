/* eslint-disable */
<template>
  <div class="home">
    <!-- 用户信息 -->
    <div class="user-info" v-if="isLoggedIn">
      <span>欢迎回来，{{ username }} </span>
      <el-button type="danger" size="small" @click="handleLogout">注销</el-button>
    </div>
    <el-container>
      <el-aside width="700px" class="custom-aside">
        <!-- 编辑按钮 -->
        <div class="preview-container">
          <el-button type="primary" @click="showConfigDialog" class="edit-button">
          模型编辑
        </el-button>
        <div class="preview-buttons"> 
              <el-button type="primary" class="edit-button" @click="handleReadDocument">读取文档</el-button>
        </div>
        </div>
        <!-- 文件上传区域 -->
        <el-upload
          class="upload-area"
          drag
          :action="$axios.defaults.baseURL + '/api/upload'"
          :headers="uploadHeaders"
          :before-upload="beforeUpload"
          :on-exceed="handleExceed"
          :on-error="handleUploadError"
          :on-success="handleUploadSuccess"
          accept=".docx"
          :limit="1"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 docx 文件
            </div>
          </template>
        </el-upload>

        <!-- 测试规则区域 -->
        <div class="test-rules">
          <div class="header-row">
            <h3>测试规范</h3>
            <div class="test-buttons">
              <el-button type="primary" size="normal" @click="showAddRuleDialog" class="add-rule-btn">添加规范</el-button>
              <el-button type="primary" size="normal" @click="handleStartConversion" class="start-conversion-btn">
              开始转换
             </el-button>
            </div>
          </div>
          <div class="test-rules-controls">
            <el-button size="small" @click="selectAllRules">全选</el-button>
            <el-button size="small" @click="unselectAllRules">全关</el-button>
          </div>
          <el-row :gutter="20" class="test-rules-grid">
            <el-col :span="12" v-for="(rule, index) in testRules" :key="index">
              <div class="test-rule-item">
                <span class="rule-name">{{ rule.name }}</span>
                <div class="rule-controls">
                  <el-button 
                    type="primary" 
                    :icon="Edit" 
                    @click="editRule(index)" 
                    class="start-conversion-btn"
                    v-if="!rule.enabled"
                  ></el-button>
                  <el-button 
                    type="danger" 
                    :icon="Delete" 
                    @click="deleteRule(index)"
                    v-if="!rule.enabled"
                  ></el-button>
                  <el-switch v-model="rule.enabled" @change="() => updateRuleStatus(rule)" style="margin-left: 10px"/>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-aside>

      <el-main>
        <!-- 日志展示区域 -->
        <div class="log-area">
        <div class="preview-container">
          <h3>日志</h3>
          <div class="preview-buttons"> 
            <el-button type="primary" class="edit-button" @click="handleClearLogs">日志清空</el-button>
          </div>
          </div>
          <el-scrollbar height="200px">
            <div v-if="logs.length === 0" class="empty-state">暂无日志记录</div>
            <div v-else v-for="(log, index) in logs" :key="index" class="log-item">
              <span class="log-time">{{ log.time }}</span>
              <span :class="['log-content', log.type]">{{ log.content }}</span>
            </div>
          </el-scrollbar>
        </div>

        <!-- XMind预览区域 -->
        <div class="preview-area">
          <div class="preview-container">
            <h3>XMind预览</h3>
            <div class="preview-buttons"> 
              <el-button type="primary" @click="showDemoDialog" class="edit-button">预览</el-button>
            </div>
          </div>
          
          <div class="preview-content">
            <div v-if="!previewData || !previewData.length" class="empty-state">暂无预览内容</div>
            <div v-else class="mindmap-container">
              <mindmap
                v-model="previewData"
                class="mindmap"
              />
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="warning" @click="handleRetry" v-if="showRetry">重试</el-button>
          <el-button type="primary" @click="handleDownload" v-if="canDownload">下载</el-button>
        </div>
      </el-main>
    </el-container>

    <!-- API配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      title="API配置"
      width="50%"
    >
      <div class="config-list">
        <div class="model-section">
          <h3>普通模型 (normal)</h3>
          <div class="config-item">
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.normal.api_key" placeholder="API Key" />
            </div>
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.normal.api_url" placeholder="API URL" />
            </div>
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.normal.model" placeholder="模型名称" />
            </div>
          </div>
        </div>
        <div class="model-section">
          <h3>文件上传模型 (file)</h3>
          <div class="config-item">
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.fileUpload.api_key" placeholder="API Key" />
            </div>
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.fileUpload.api_url" placeholder="API URL" />
            </div>
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.fileUpload.model" placeholder="模型名称" />
            </div>
          </div>
        </div>
        <div class="model-section">
          <h3>图像识别模型 (vision)</h3>
          <div class="config-item">
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.imageRecognition.api_key" placeholder="API Key" />
            </div>
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.imageRecognition.api_url" placeholder="API URL" />
            </div>
            <div class="input-with-label">
              <span class="required-field">*</span>
              <el-input v-model="modelConfigs.imageRecognition.model" placeholder="模型名称" />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="configDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConfigs">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加规范对话框 -->
    <el-dialog
      v-model="ruleDialogVisible"
      :title="editingRule ? '编辑规范' : '添加规范'"
      width="50%"
    >
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="规范名称" required>
          <el-input v-model="ruleForm.name" placeholder="请输入规范名称" />
        </el-form-item>
        <el-form-item label="规范内容" required>
          <el-input
            v-model="ruleForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入规范内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ruleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRule">保存</el-button>
        </span>
      </template>
    </el-dialog>


  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import axios from 'axios'
import { Delete, Edit, UploadFilled } from '@element-plus/icons-vue'
import mindmap from 'vue3-mindmap'
import 'vue3-mindmap/dist/style.css'
export default {
  name: 'Home',
  components: {
    UploadFilled,
    mindmap
  },
  setup() {
    const router = useRouter()
    // 用户状态
    const isLoggedIn = ref(false)
    const username = ref('')

    // 检查登录状态
    const checkLoginStatus = () => {
      const user = localStorage.getItem('user')
      if (user) {
        const userData = JSON.parse(user)
        isLoggedIn.value = true
        username.value = userData.username
      } else {
        isLoggedIn.value = false
        username.value = ''
      }
    }

    // 注销方法
    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      isLoggedIn.value = false
      username.value = ''
      ElMessage.success('注销成功')
      router.push('/login')
    }

    onMounted(() => {
      loadConfigs()
      checkLoginStatus()
      window.addEventListener('storage', checkLoginStatus)
    })

    onUnmounted(() => {
      window.removeEventListener('storage', checkLoginStatus)
    })
    // 状态变量
    const configDialogVisible = ref(false)
    const demoDialogVisible = ref(false)
    const demoFiles = ref([])
    const ruleDialogVisible = ref(false)
    const editingRule = ref(null)
    const ruleForm = ref({
      name: '',
      content: ''
    })
    const editIndex = ref(0)
    const modelConfigs = ref({
      fileUpload: {
        api_key: '',
        api_url: '',
        model: '',
        type: 'file'
      },
      imageRecognition: {
        api_key: '',
        api_url: '',
        model: '',
        type: 'vision'
      },
      normal: {
        api_key: '',
        api_url: '',
        model: '',
        type: 'normal'
      }
    })
    const testRules = ref([])
    const logs = ref([])
    const previewData = ref([])
    const currentFile = ref(null)
    const showRetry = ref(false)
    const canDownload = ref(false)
    const scale = ref(1)
    const testResults = ref([])
    const outputFile = ref(null)
    // 加载测试规范
    const loadTestRules = async () => {
      try {
        const response = await axios.get('/api/test-rules')
        // 保持原有规范的enabled状态
        const oldRules = testRules.value
        testRules.value = response.data.map(newRule => {
          const oldRule = oldRules.find(r => r.id === newRule.id)
          return oldRule ? { ...newRule, enabled: oldRule.enabled } : newRule
        })
      } catch (error) {
        console.error('加载测试规范失败:', error)
        ElMessage.error('加载测试规范失败')
      }
    }

    // 保存测试规范
    const saveTestRule = async () => {
      try {
        if (!ruleForm.value.name.trim()) {
          ElMessage.warning('请输入规范名称')
          return
        }

        const ruleData = {
          name: ruleForm.value.name.trim(),
          content: ruleForm.value.content,
          enabled: editingRule.value ? editingRule.value.enabled : true
        }

        if (editingRule.value) {
          ruleData.id = editingRule.value.id
        }

        await axios.post('/api/test-rules', ruleData)
        await loadTestRules()
        ruleDialogVisible.value = false
        ruleForm.value = { name: '', content: '' }
        editingRule.value = null
        ElMessage.success('规范保存成功')
      } catch (error) {
        console.error('保存规范失败:', error)
        ElMessage.error('保存规范失败')
      }
    }

    // 删除测试规范
    const deleteTestRule = async (ruleId) => {
      try {
        await axios.delete('/api/test-rules', { data: { id: ruleId } })
        await loadTestRules()
        ElMessage.success('规范删除成功')
      } catch (error) {
        console.error('删除规范失败:', error)
        ElMessage.error('删除规范失败')
      }
    }

    // 显示添加规范对话框
    const showAddRuleDialog = () => {
      editingRule.value = null
      ruleForm.value = { name: '', content: '' }
      ruleDialogVisible.value = true
    }

    // 编辑规范
    const editRule = async (index) => {
      const rule = testRules.value[index]
      editingRule.value = rule
      ruleForm.value = { 
        name: rule.name, 
        content: rule.content || ''
      }
      ruleDialogVisible.value = true
    }

    // 删除规范
    const deleteRule = async (index) => {
      const rule = testRules.value[index]
      try {
        await ElMessageBox.confirm('确定要删除该规范吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deleteTestRule(rule.id)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除规范失败:', error)
        }
      }
    }

    // 更新规范状态
    const updateRuleStatus = async (rule) => {
      try {
        await axios.post('/api/test-rules', {
          id: rule.id,
          name: rule.name,
          enabled: rule.enabled
        })
      } catch (error) {
        console.error('更新规范状态失败:', error)
        ElMessage.error('更新规范状态失败')
        // 恢复状态
        rule.enabled = !rule.enabled
      }
    }

    // 组件挂载时加载测试规范
    onMounted(() => {
      loadTestRules()
    })

    // 加载API配置
    const loadConfigs = async () => {
      try {
        const response = await axios.get('/api/configs')
        if (response.data && response.data.length > 0) {
          // 尝试将配置映射到对应的模型类型
          response.data.forEach(config => {
            if (config.type === 'file') {
              modelConfigs.value.fileUpload = config;
            } else if (config.type === 'vision') {
              modelConfigs.value.imageRecognition = config;
            } else if (config.type === 'normal') {
              modelConfigs.value.normal = config;
            }
          });
        }
      } catch (error) {
        ElMessage.error('加载配置失败')
      }
    }

    // 保存API配置
    const saveConfigs = async () => {
      // 创建配置数组
      const configs = [
        { ...modelConfigs.value.fileUpload, type: 'file' },
        { ...modelConfigs.value.imageRecognition, type: 'vision' },
        { ...modelConfigs.value.normal, type: 'normal' }
      ];
      
      // 过滤掉空值配置项
      const validConfigs = configs.filter(config => {
        return config.api_key && config.api_key.trim() && 
               config.api_url && config.api_url.trim() && 
               config.model && config.model.trim();
      });
      
      if (validConfigs.length === 0) {
        ElMessage.warning('请至少添加一个有效的API配置')
        return
      }

      try {
        await axios.post('/api/configs', validConfigs)
        configDialogVisible.value = false
        ElMessage.success('配置已保存')
      } catch (error) {
        ElMessage.error('保存配置失败')
      }
    }

    // 文件上传相关
    const beforeUpload = (file) => {
      addLog(`文件: ${file.name} 上传成功`, 'info')
      const isDocx = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      if (!isDocx) {
        addLog(`文件类型错误: ${file.name} 不是docx文件`, 'error')
        ElMessage({
          message: '只能上传 docx 文件!',
          type: 'error',
          duration: 3000,
          showClose: true
        })
        return false
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        addLog(`文件大小超过限制: ${file.name} 大于10MB`, 'error')
        ElMessage({
          message: '文件大小不能超过 10MB!',
          type: 'error',
          duration: 3000,
          showClose: true
        })
        return false
      }
      
      return true
    }
    
    const handleExceed = () => {
      ElMessage({
        message: '最多只能上传1个文件!',
        type: 'warning',
        duration: 3000,
        showClose: true
      })
    }

    const handleUploadSuccess = (response) => {
      if (response.success) {
        currentFile.value = response.filename
        addLog(`${response.filename} 文件上传成功，已加入转换队列`, 'success')
      } else {
        addLog(`文件上传失败: ${response.message}`, 'error')
        ElMessage.error(response.message)
      }
    }

    const handleUploadError = (error) => {
      let message = '上传失败';
      if (error.response && error.response.data && error.response.data.message) {
        message = `${message}: ${error.response.data.message}`;
      } else if (error.message) {
        message = `${message}: ${error.message}`;
      }
      addLog(message, 'error')
      ElMessage({
        message: message,
        type: 'error',
        duration: 5000,
        showClose: true
      })
    }

    // 测试规则相关
    const selectAllRules = () => {
      testRules.value.forEach(rule => rule.enabled = true)
    }

    const unselectAllRules = () => {
      testRules.value.forEach(rule => rule.enabled = false)
    }

    // 运行测试
    const runTests = async () => {
      try {
        addLog('开始执行测试规范检查...', 'info')
        const enabledRules = testRules.value.filter(rule => rule.enabled)
        if (enabledRules.length === 0) {
          addLog('未选择任何测试规范', 'warning')
          ElMessage.warning('请至少选择一个测试规范')
          return false
        }

        const response = await axios.post('/api/readdocxfile', {
          test_rules: enabledRules
        })

        const results = response.data.results
        let successCount = 0
        let failCount = 0

        results.forEach(result => {
          if (result.success) {
            successCount++
          } else {
            failCount++
          }
          addLog(`${result.rule}: ${result.message}`, result.success ? 'success' : 'error')
        })

        addLog(`测试完成: ${successCount}个通过, ${failCount}个失败`, successCount === results.length ? 'success' : 'warning')
        return response.data.success
      } catch (error) {
        const errorMsg = error.response?.data?.message || '测试执行失败'
        addLog(errorMsg, 'error')
        ElMessage.error(errorMsg)
        return false
      }
    }

    // 转换文件
    const convertFile = async () => {
      try {
        if (!currentFile.value) {
          addLog('请先上传文件', 'warning')
          ElMessage.warning('请先上传文件')
          return
        }

        addLog('开始转换文件...', 'info')
        const response = await axios.post('/api/convert', {
          filename: currentFile.value,
          test_results: testResults.value
        })

        if (response.data.success) {
          outputFile.value = response.data.output_filename
          addLog(`文件转换成功：${response.data.output_filename}`, 'success')
          await loadPreview(outputFile.value)
          canDownload.value = true
          ElMessage.success('文件转换成功')
        } else {
          const errorMsg = response.data.message || '转换失败'
          addLog(errorMsg, 'error')
          ElMessage.error(errorMsg)
          showRetry.value = true
        }
      } catch (error) {
        const errorMsg = error.response?.data?.message || '文件转换失败'
        addLog(errorMsg, 'error')
        ElMessage.error(errorMsg)
        showRetry.value = true
      }
    }

    // 预览相关
    const loadPreview = async (filename) => {
      try {
        addLog(`正在加载预览: ${filename}`, 'info')
        const response = await fetch(`/api/preview/${filename}`)
        const data = await response.json()
        if (data.success && data.preview_data) {
          if (data.preview_data.nodes && data.preview_data.nodes.length > 0) {
            const convertNode = (node) => {
              return {
                name: node.text || '',
                children: node.children ? node.children.map(child => convertNode(child)) : []
              }
            }
            
            const rootNode = data.preview_data.nodes[0];
            previewData.value = [convertNode(rootNode)];
            addLog('预览数据加载成功', 'success')
            console.log('预览数据:', previewData.value)
          } else {
            addLog('预览数据格式不正确：缺少节点数据', 'error')
            ElMessage.warning('预览数据格式不正确：缺少节点数据')
          }
        } else {
          const errorMsg = data.message || '预览数据格式不正确'
          addLog(errorMsg, 'error')
          ElMessage.warning(errorMsg)
        }
      } catch (error) {
        const errorMsg = `预览加载失败: ${error.message || '未知错误'}`
        addLog(errorMsg, 'error')
        console.error('预览加载错误:', error)
        ElMessage.error(errorMsg)
      }
    }

    const zoomIn = () => {
      scale.value = Math.min(scale.value + 0.1, 2)
    }

    const zoomOut = () => {
      scale.value = Math.max(scale.value - 0.1, 0.5)
    }

    // 操作按钮相关
    const handleCancel = () => {
      currentFile.value = null
      previewData.value = null
      showRetry.value = false
      canDownload.value = false
      logs.value = []
    }

    const handleRetry = () => {
      runTests()
    }

    const handleDownload = async () => {
      if (!currentFile.value) return
      
      try {
        // 从原始文件名中提取基本名称（不包含扩展名）
        const baseName = currentFile.value.replace(/\.docx$/i, '')
        const filename = `${baseName}.xmind`
        
        // 对文件名进行编码，确保特殊字符能够正确传输
        const encodedFilename = encodeURIComponent(filename)
        window.location.href = `/api/download/${encodedFilename}`
        
        addLog(`正在下载: ${filename}`, 'success')
      } catch (error) {
        console.error('下载错误:', error)
        ElMessage.error('下载失败')
      }
    }

    // 日志相关
    const addLog = (content, type = 'info') => {
      // 确保日志内容是字符串
      const logContent = typeof content === 'string' ? content : JSON.stringify(content)
      
      logs.value.push({
        time: new Date().toLocaleTimeString(),
        content: logContent,
        type
      })
      // 在控制台也输出日志，方便调试
      console.log(`[${type.toUpperCase()}] ${logContent}`)
    }
    // 日志清空方法
    const handleClearLogs = () => {
      logs.value = []
      previewData.value = null
      // addLog('日志已清空', 'info')
    }

    // 生命周期钩子
    onMounted(() => {
      loadConfigs()
    })

    // 添加handleReadDocument方法
    const handleReadDocument = async () => {
      if (!currentFile.value) {
        ElMessage.warning('请先上传文件')
        return
      }
      const loading = ElLoading.service({
        lock: true,
        text: '文档读取处理中...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      try {
        addLog('开始读取文档...', 'info')
        const response = await axios.post('/api/readdocxfile', {})
        if (response.data.success) {
          addLog('文档读取成功', 'success')
          ElMessage.success('文档读取成功')
        } else {
          const errorMsg = response.data.message || '读取失败'
          addLog(errorMsg, 'error')
          ElMessage.error(errorMsg)
        }
      } catch (error) {
        const errorMsg = error.response?.data?.message || '读取文档失败'
        addLog(errorMsg, 'error')
        ElMessage.error(errorMsg)
      } finally {
        loading.close()
      }
    }

    // 添加handleStartConversion方法
    const handleStartConversion = async () => {
      if (!currentFile.value) {
        ElMessage.warning('请先上传文件')
        return
      }
      try {
        addLog('开始执行测试规范检查...', 'info')
        const testSuccess = await runTests()
        if (!testSuccess) {
          addLog('测试规范检查未通过，请修正后重试', 'error')
          ElMessage.error('测试规范检查未通过，请修正后重试')
          return
        }
        await convertFile()
      } catch (error) {
        const errorMsg = error.response?.data?.message || '转换失败'
        addLog(errorMsg, 'error')
        ElMessage.error(errorMsg)
      }
    }

    // 添加上传请求头
    const uploadHeaders = computed(() => {
      const token = localStorage.getItem('token')
      return {
        Authorization: `Bearer ${token}`
      }
    })

    return {
      isLoggedIn,
      username,
      handleLogout,
      configDialogVisible,
      demoDialogVisible,
      demoFiles,
      ruleDialogVisible,
      ruleForm,
      editingRule,
      editIndex,
      showAddRuleDialog,
      saveRule: saveTestRule,
      modelConfigs,
      testRules,
      logs,
      previewData,
      currentFile,
      showRetry,
      canDownload,
      scale,
      updateRuleStatus,
      showConfigDialog: () => configDialogVisible.value = true,
      showDemoDialog: async () => {
        try {
          const response = await axios.get('/api/preview/中心主题.xmind')
          if (response.data.success && response.data.preview_data) {
            if (response.data.preview_data.nodes && response.data.preview_data.nodes.length > 0) {
              const convertNode = (node) => {
                return {
                  name: node.text || '',
                  children: node.children ? node.children.map(child => convertNode(child)) : []
                }
              }
              
              const rootNode = response.data.preview_data.nodes[0];
              previewData.value = [convertNode(rootNode)];
              console.log('Demo预览数据:', previewData.value)
            } else {
              ElMessage.error('加载Demo预览失败：无预览数据')
            }
          } else {
            ElMessage.error('加载Demo预览失败：无预览数据')
          }
        } catch (error) {
          console.error('加载Demo预览失败:', error)
          ElMessage.error(`加载Demo预览失败: ${error.message || '未知错误'}`)
        }
      },
      saveConfigs,
      beforeUpload,
      handleUploadSuccess,
      handleUploadError,
      handleExceed,
      selectAllRules,
      unselectAllRules,
      handleCancel,
      handleRetry,
      handleDownload,
      zoomIn,
      zoomOut,
      Delete,
      Edit,
      handleStartConversion,
      convertFile,
      editRule,
      deleteRule,
      saveTestRule,
      UploadFilled,
      uploadHeaders,
      handleClearLogs,
      handleReadDocument
    }
  }
}
</script>

<style>
.user-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  border-radius: 4px;
}
.user-info span {
  color: #606266;
  font-size: 14px;
}
.preview-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  align-items: baseline;
}
.preview-buttons {
  display: flex;
  flex-direction: row-reverse;
}

</style>

<style scoped>

.mindmap-container {
  width: 100%;
  height: 600px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.model-section {
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  background-color: #f8f8f8;
}

.model-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.mindmap {
  width: 100%;
  height: 100%;
}

.home {
  padding: 20px;
}

.custom-aside {
  overflow-x: hidden;
  padding-right: 10px;
}

.edit-button {
  margin-bottom: 20px;
}

.upload-area {
  margin-bottom: 20px;
}

.test-rules {
  margin-top: 20px;
}

.test-rules-controls {
  margin-bottom: 10px;
}

.test-rules-grid {
  margin-top: 10px;
  max-height: 650px;
  overflow-y: auto;
}

.test-rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 5px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.rule-name {
  font-size: 14px;
}

.log-area {
  margin-bottom: 20px;
}

.log-item {
  margin-bottom: 5px;
}

.log-time {
  color: #999;
  margin-right: 10px;
}

.log-content {
  font-family: monospace;
}

.log-content.success {
  color: #67C23A;
}

.log-content.error {
  color: #F56C6C;
}

.preview-area {
  margin-bottom: 20px;
}

.preview-controls {
  margin-bottom: 10px;
}

.preview-content {
  border: 1px solid #eee;
  padding: 10px;
  min-height: 600px;
  position: relative;
  overflow: hidden;
}

.zoom-controls {
  position: absolute;
  bottom: 10px;
  right: 10px;
}

.vertical-buttons {
  display: flex;
  flex-direction: column;
}

.vertical-buttons .el-button {
  margin-left: 0;
  margin-bottom: 5px;
}

.vertical-buttons .el-button:last-child {
  margin-bottom: 0;
}

.action-buttons {
  text-align: right;
}

.config-list {
  margin-bottom: 20px;
}

.config-item {
  display: flex;
  flex-direction: row;
  gap: 10px;
  width: 100%;
  flex-wrap: nowrap;
}

.empty-state {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 14px;
}
.test-rules .header-row {
  display: flex;
  justify-content: space-between;
}
.test-rules .test-buttons {
  display: flex;
  justify-content: space-around;
  align-items: center;
}
.demo-files {
  max-height: 400px;
  overflow-y: auto;
}

.demo-file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.file-name {
  font-size: 14px;
  color: #606266;
}

.required-field {
  color: #F56C6C;
  margin-right: 2px;
}

.input-with-label {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  margin-right: 5px;
}

.input-with-label:last-child {
  margin-right: 0;
}
</style>