<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title">{{ isLogin ? '登录' : '注册' }}</h2>
      <form @submit.prevent="isLogin ? handleLogin() : handleRegister()">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            :placeholder="'请输入用户名'"
          >
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            :placeholder="'请输入密码'"
            @input="checkPasswordStrength"
          >
          <div v-if="!isLogin" class="password-strength" :class="strengthClass">
            密码强度: {{ passwordStrength }}
            <div class="strength-tips">密码至少包含8个字符，包括大小写字母、数字和特殊字符</div>
          </div>
        </div>
        <div v-if="!isLogin" class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            required
            placeholder="请再次输入密码"
          >
          <div v-if="!passwordsMatch && confirmPassword" class="password-mismatch">
            两次输入的密码不一致
          </div>
        </div>
        <button type="submit" :disabled="loading || (!isLogin && !canSubmit)">
          {{ loading ? (isLogin ? '登录中...' : '注册中...') : (isLogin ? '登录' : '注册') }}
        </button>
        <div class="switch-form">
          <a href="#" @click.prevent="toggleForm">{{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}</a>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      isLogin: true,
      username: '',
      password: '',
      confirmPassword: '',
      loading: false,
      passwordStrength: '弱',
      strengthClass: 'weak'
    }
  },
  computed: {
    passwordsMatch() {
      return this.password === this.confirmPassword
    },
    canSubmit() {
      return this.username && 
             this.password && 
             this.confirmPassword && 
             this.passwordsMatch && 
             this.strengthClass !== 'weak'
    }
  },
  methods: {
    checkPasswordStrength() {
      const password = this.password
      let strength = 0
      
      if (password.length >= 8) strength++
      if (/[A-Z]/.test(password)) strength++
      if (/[a-z]/.test(password)) strength++
      if (/[0-9]/.test(password)) strength++
      if (/[^A-Za-z0-9]/.test(password)) strength++

      if (strength <= 2) {
        this.passwordStrength = '弱'
        this.strengthClass = 'weak'
      } else if (strength <= 4) {
        this.passwordStrength = '中'
        this.strengthClass = 'medium'
      } else {
        this.passwordStrength = '强'
        this.strengthClass = 'strong'
      }
    },
    toggleForm() {
      this.isLogin = !this.isLogin
      this.username = ''
      this.password = ''
      this.confirmPassword = ''
    },
    async handleLogin() {
      if (this.loading) return
      
      this.loading = true
      try {
        const response = await this.$axios.post('/api/login', {
          username: this.username,
          password: this.password
        })

        const data = response.data
        
        if (data.success) {
          localStorage.setItem('token', data.token)
          localStorage.setItem('user', JSON.stringify(data.user))
          this.$router.push('/')
        } else {
          alert(data.message)
        }
      } catch (error) {
        alert('登录失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    async handleRegister() {
      if (this.loading) return
      
      this.loading = true
      try {
        const response = await this.$axios.post('/api/register', {
          username: this.username,
          password: this.password
        })

        const data = response.data
        
        if (data.success) {
          // 注册成功后切换到登录状态
          this.isLogin = true
          this.password = ''
          alert('注册成功，请登录')
        } else {
          alert(data.message || '注册失败，请稍后重试')
        }
      } catch (error) {
        console.error('注册失败:', error)
        let errorMessage = '注册失败，请稍后重试'
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message
        }
        alert(errorMessage)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 87.44959185vh;
  background-color: #f5f5f5;
  overflow: auto;
  padding: 20px 0;
  box-sizing: border-box;
}

.login-box {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 360px;
}

.form-group {
  margin-bottom: 0.75rem;
}

label {
  display: block;
  margin-bottom: 0.3rem;
  color: #333;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  height: 36px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 0.6rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.3s;
  height: 40px;
}

button:hover {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.login-title {
  margin-top: 0;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 1.5rem;
  color: #333;
}

.switch-form {
  text-align: center;
  margin-top: 1rem;
}

.switch-form a {
  color: #409EFF;
  text-decoration: none;
}

.switch-form a:hover {
  text-decoration: underline;
}

.password-strength {
  margin-top: 0.5rem;
  font-size: 0.8rem;
}

.strength-tips {
  color: #666;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.weak {
  color: #ff4949;
}

.medium {
  color: #f7ba2a;
}

.strong {
  color: #13ce66;
}

.password-mismatch {
  color: #ff4949;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}
</style>