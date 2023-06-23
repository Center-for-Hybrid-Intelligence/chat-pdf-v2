<template>
  <button
    ref="button"
    class="flex items-center transition duration-150 ease-in-out px-6 py-2"
    :class="buttonClasses"
    :style="buttonStyle"
    v-bind="$attrs"
    @click.prevent.stop="onClick"
    :disabled='isDisabled'
  >
    <div class="w-full flex items-center justify-center">
      <slot name="left"></slot>

      <slot name="center"></slot>

      <slot name="right"></slot>
    </div>
  </button>
</template>

<script>
import { isString } from "@/lib/getVariableType";
import { computed, onMounted, ref } from "vue";

export default {
  // eslint-disable-next-line vue/multi-word-component-names
  name: "Button",
  emits: ["click"],
  props: {
    isInverted: {
      // swap dark mode / light mode styles
      type: Boolean,
      default: false,
    },
    isPrimary: {
      // fx. primary vs. alternative action
      default: false,
    },
    isAlt: {
      default: false,
    },
    isBusy: {
      // waiting for action response
      default: false,
    },
    isSuccess: {
      default: false,
    },
    isDanger: {
      default: false,
    },
    isWarning: {
      default: false,
    },
    isOutline: {
      type: Boolean,
      default: false,
    },
    isDisabled: {
      type: Boolean,
      // action is not ready
      default: false,
    },
    isOptimistic: {
      // waiting for action response, but already applying optimistic result
      default: false,
    },
    isPermitted: {
      // user is authenticated to perform action
      default: true,
    },
    isSmall: {
      default: false,
    },
    serverError: {
      // server error object
      type: Object,
      default: null,
      validator: (value) => {
        let pass = value === null;
        if (!pass) {
          pass =
            isString(value.name) &&
            value.name.length &&
            isString(value.message) &&
            value.message.length;
        }
        return pass;
      },
    },
    drawBorder: {
      // for sizing adjacent buttons
      type: Boolean,
      default: true,
    },
  },
  setup(props, { emit }) {
    const onClick = () => emit("click");
    const button = ref(null);
    const twReady = ref(false);

    const buttonStyle = computed(() => {
      const style = {};
      if (button.value) {
        const cStyle = getComputedStyle(button.value);
        if (cStyle.padding === "0px")
          style.padding = props.isSmall ? "0.5rem 1rem" : "0.75rem 2rem";
      }
      return style;
    });

    const buttonClasses = computed(() => {
      const classes = [];
      const {
        isAlt,
        isOutline,
        isPrimary,
        isSuccess,
        isWarning,
        isDanger,
        isDisabled,
        isSmall,
      } = props;

      if (isDisabled) classes.push("disabled");
      else {
        if (isDanger) classes.push("danger");
        else if (isWarning) classes.push("warning");
        else if (isSuccess) classes.push("success");
        else if (isPrimary) classes.push("primary");
        else if (isOutline) classes.push("outline");
        else if (isAlt) classes.push("alt");
      }

      if (isSmall) classes.push("shadow");
      else classes.push("shadow-lg");

      return classes;
    });

    onMounted(() => {
      twReady.value = true;
    });

    return {
      button,
      buttonClasses,
      buttonStyle,
      onClick,
    };
  },
};
</script>
<style scoped>

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

</style>