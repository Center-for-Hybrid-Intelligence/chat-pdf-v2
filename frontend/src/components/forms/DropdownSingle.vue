<template>
  <div class="relative">
    <button
      class="dropdown flex flex-1 justify-center border-white border-opacity-10 border rounded-xl font-medium bg-white bg-opacity-10 hover:bg-opacity-100"
        :class="{'toggleButton--active': !!selectedValue()}"
      type="button"
      :key="dropdown"
      @click.stop="toggle($event)"
    >
      {{ selectedValue() || titleOfDropdown ||  "More Options" }}
      <svg
        class=" mt-1 ml-1 w-4 h-4"
        aria-hidden="true"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        ></path>
      </svg>
    </button>
    <!-- Dropdown menu -->
    <div
      v-show="show"
      class="z-10 w-full bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700"
      style="
        position: absolute;
        inset: 0px auto auto 0px;
        margin: 0px;
        transform: translate3d(0px, 44px, 0px);
      "
    >
      <ul class=" text-sm text-gray-700 dark:text-gray-200">
        <li v-for="item in items" :key="item" @click.stop="onClick">
          <div
            :id="item"
            class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
          >
            {{ item }}
          </div>
        </li>
      </ul>

    </div>

  </div>
</template>

<script>
import {ref, onMounted, onBeforeUnmount} from "vue";
import { isString } from "@/lib/getVariableType";
import dropdown from "@/components/forms/Dropdown.vue";

export default {
  name: "DropdownSingle",
  computed: {
    dropdown() {
      return dropdown;
    },
  },
  emits: ["select"],
  props: {
    selected: {
      type: String,
    },
    titleOfDropdown: {
      type: String,
    },
    items: {
      type: Array,
      required: true,
      validator: (v) =>
        Array.isArray(v) &&
        v.reduce((pass, item) => pass && isString(item), true),
    },
    disable: {
      type: Boolean,
    },
  },
  setup(props, { emit }) {
    function selectedValue () {
      return props.selected;
    }
    const show = ref(false);

    const onClick = (e) => {
      e.preventDefault(); // do not bubble to button
      show.value = false;
      console.log("e.target.id", e.target.id)
      emit("select", e.target.id);
    };
    // Add closeDropdown method
    const closeDropdown = () => {
      show.value = false;
    };

    // Add onClickOutside method
    const onClickOutside = (event) => {
      const dropdownElement = event.target.closest(".dropdown.relative");

      if (!dropdownElement) {
        closeDropdown();
      }
    };

    // Add and remove the onClickOutside listener
    onMounted(() => {
      document.addEventListener("click", onClickOutside);
    });

    onBeforeUnmount(() => {
      document.removeEventListener("click", onClickOutside);
    });

    const toggle = () => {
      show.value = !show.value;
    };
    return {
      onClick,
      show,
      toggle,
      selectedValue,
    };
  },
};
</script>

<style scoped></style>
