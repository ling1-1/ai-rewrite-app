<template>
  <div class="history-edit-dialog">
    <el-dialog v-model="dialogVisible" title="编辑历史记录" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="自定义名称（可选）" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="备注（可选）" />
        </el-form-item>
        <el-form-item label="收藏">
          <el-switch v-model="form.is_favorite" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'

const props = defineProps({
  record: Object
})

const emit = defineEmits(['update', 'close'])

const dialogVisible = ref(true)
const saving = ref(false)

const form = reactive({
  name: props.record?.name || '',
  notes: props.record?.notes || '',
  is_favorite: props.record?.is_favorite || false
})

const handleSave = async () => {
  saving.value = true
  try {
    const response = await http.put(`/history/${props.record.id}`, form)
    ElMessage.success('保存成功')
    emit('update', response.data)
    dialogVisible.value = false
    emit('close')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

watch(dialogVisible, (val) => {
  if (!val) {
    emit('close')
  }
})
</script>

<style scoped>
.history-edit-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}
</style>
