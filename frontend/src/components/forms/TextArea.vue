<template>
  <div class="textArea w-full h-full">
    <label
        v-if="label"
        class="mb-2 block text-sm font-medium"
    >{{ label }}</label>
    <textarea
        ref="input"
        class="textArea
          block
          p-2.5
          w-full
          h-full
          text-lg
          text-gray-500 dark:text-white
          bg-gray-50 dark:bg-gray-700
          rounded-lg border border-cvblue
          dark:border-gray-600
          dark:placeholder-gray-400
          focus:ring-indigo-500 dark:focus:ring-indigo-500
          focus:border-blue-500 dark:focus:border-blue-500"
        :id="inputId"
        :style="textareaStyle"
        :value="value"
        :placeholder="placeholder"
        autofocus
        :tabindex="tabIndex"
        @change="onChange"
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
        @keydown.esc="onAbort"
        @keydown.tab="onTab"
        @keydown="onKeydown"
    ></textarea>
    <p
        v-if="hint"
        class="w-full pt-1 pl-2 text-xs text-red-500"
    >{{ hint }}</p>
  </div>
</template>

<script>
import { computed, nextTick, ref, watch } from 'vue'
import {isNumber} from "@/lib/getVariableType";
import {getDOMElementHeight} from "@/lib/getDOMElementHeight";

export default {
  name: 'TextArea',
  emits: ['abort', 'change', 'input', 'delete'],
  props: {
    minLines: {
      type: Number,
      default: 3,
      validate: newValue => isNumber(newValue) && newValue > 0
    },
    isFocused: {
      type: Boolean,
      default: false
    },
    label: {
      type: String,
      default: ''
    },
    tabIndex: {
      type: Number,
      default: 1
    },
    hint: {
      type: String,
      default: ''
    },
    inputId: {
      type: String,
      default: ''
    },
    value: {
      default: ''
    },
    nextOnTab: {
      type: Boolean,
      default: true
    },
    placeholder: {
      type: String,
      default: ''
    },
  },
  setup(props, { emit }) {
    const isFocused = computed(() => props.isFocused)
    const input = ref(null)
    const originalValue = ref(props.value)
    const inputValue = computed(() => input.value?.value)
    const textareaStyle = computed(() => ({ minHeight: `${ props.minLines || 1 }rem` }))

    const onAbort = () => {
      emit('abort', originalValue.value)
      resize()
    }
    const onBlur = e => {
      emit('change', e.target.value)
      resize()
    }
    const onChange = e => {
      emit('change', e.target.value)
      resize()
    }
    const onFocus = () => {
      // emit('focus')
      resize()
    }
    const onInput = e => {
      emit('input', e.target.value)
      resize()
    }
    const onTab = e => {
      if (props.nextOnTab) return
      e.preventDefault()
      const el = input.value
      let start = el.selectionStart
      let end = el.selectionEnd
      el.value = el.value.substring(0, start) + '\t' + el.value.substring(end)
      el.selectionEnd = el.selectionStart = start + 1
    }

    const resize = () => {
      const textarea = input.value
      if (textarea) {
        const height = getDOMElementHeight(textarea, { borders: true })
        textarea.style.height = `${ height }px`
      }
    }

    watch(inputValue, () => resize(), { immediate: true })
    watch(isFocused, value => {
      if (input.value) {
        if (value) {
          nextTick(() => {
            input.value.focus()
            resize()
          })
        }
      }
    }, { immediate: true })

    const onKeydown = e => {
      const isDeleteKey = e.key === 'Backspace' || e.keyCode === 8 || e.code === 'Backspace'
      const isEmpty = e.target.value === ''
      if (isDeleteKey && isEmpty) emit('delete')
    }

    return {
      input,
      onAbort,
      onBlur,
      onChange,
      onFocus,
      onInput,
      onKeydown,
      onTab,
      textareaStyle,
    }
  },
}
</script>

<style scoped>
.markdownInput {
  resize: vertical !important;
  min-height: 1rem;
  min-width: 100%;
  border-radius: 4px;
  white-space: pre-wrap;
  text-wrap: normal;
  overflow: hidden;
}

textarea:focus-visible {
  outline: none;
}
</style>
