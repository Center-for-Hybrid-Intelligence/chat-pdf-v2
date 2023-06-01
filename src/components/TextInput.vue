<template>
  <div class="textInput flex-grow">
    <div v-if="isEditing">
      <label v-if="label" class="mb-2 block text-xs text-gray-500">{{
          label
        }}</label>
      <div class="flex flex-wrap">
      <span
          v-if="iconName"
          class="inline-flex items-center px-1 text-sm border border-gray-200 bg-gray-400 dark:bg-gray-600 dark:border-gray-600"
      >
        <component
            :is="iconName"
            class="relative flex justify-center items-center"
            :size="26"
        ></component>
      </span>
        <input
            type="text"
            class="border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block flex-1 min-w-0 w-full text-sm p-2.5 dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500"
            :placeholder="placeholder"
            :value="value"
            :tabIndex="tabIndex"
            v-bind="$attrs"
            @change="onChange"
            @input="onInput"
            @keypress.esc="onAbort"
            @keypress.enter="onSubmit"
            @keypress.tab="onChange"
            @keydown.tab="onChange"
        />
        <p
            v-if="hint"
            class="w-full pt-1 text-xs text-red-500"
            :class="{ 'ml-0': !icon, 'pl-2': !icon }"
        >
          {{ hint }}
        </p>
      </div>
    </div>
    <div v-else>
      {{ value }}
    </div>
  </div>
</template>

<script>
import {computed, ref} from "vue";

export default {
  name: "TextInput",
  emits: ["change", "input", "submit"],
  props: {
    autocomplete: {
      type: String,
      default: "",
    },
    hint: {
      type: String,
      default: "",
    },
    // isBusy, serverError, ...
    isEditing: {
      type: Boolean,
      default: true,
    },
    label: {
      type: String,
      default: "",
    },
    icon: {
      type: String,
      default: "",
    },
    name: {
      type: String,
      default: "",
    },
    placeholder: {
      type: String,
      default: "Type here",
    },
    resetAfterChange: {
      type: Boolean,
      default: false,
    },
    value: {
      default: "",
    },
    tabIndex: {
      default: -1,
    },
    nextOnTab: {
      type: Boolean,
      default: true
    },
  },
  setup(props, {emit}) {
    const originalValue = ref(props.value ?? "");
    const onAbort = () => emit("change", originalValue.value);
    const onChange = (e) => {
      emit("change", e.target.value);
      if (props.resetAfterChange) e.target.value = "";
    };
    const onSubmit = (e) => {
      onChange(e)
      emit("submit");
    };
    const onInput = (e) => emit("input", e.target.value);
    const iconName = computed(() => {
      let name = "";
      return name;
    });

    return {
      iconName,
      onAbort,
      onChange,
      onInput,
      onSubmit,
    };
  },
};
</script>
