<template>
  <div class="dropdown relative">
    <button class="button dropdown" type="button" @click.stop="toggle($event)">
      {{ title || "Select items" }}
      <svg
        class="ml-2 w-4 h-4"
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
      class="z-10 w-56 bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700"
      style="
        position: absolute;
        inset: 0px auto auto 0px;
        margin: 0px;
        transform: translate3d(0px, 44px, 0px);
      "
    >
      <ul class="py-1 text-sm text-gray-700 dark:text-gray-200">
        <li v-for="item in items" :key="item" @click.stop="onClick(item)">
          <div
            :id="item"
            class="flex items-center py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
          >
            <input
              type="checkbox"
              class="rounded text-blue-500 focus:ring-blue-500"
              :value="item"
              v-model="selectedItems"
              :disabled="item === 'All' && selectedItems.includes('All')"
            />
            <span class="ml-2">{{ item.name }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { isString } from "@/lib/getVariableType";

export default {
  // eslint-disable-next-line vue/multi-word-component-names
  name: "Dropdown",
  emits: ["select"],
  props: {
    title: {
      type: String,
    },
    items: {
      // first item is the 'all' option
      type: Array,
      required: true,
      validator: (v) =>
        Array.isArray(v) &&
        v.reduce((pass, item) => pass && isString(item), true),
    },
  },
  setup(props, { emit }) {
    const show = ref(false);
    const selectedItems = ref([]);

    const onClick = (item) => {
      const index = selectedItems.value.indexOf(item);
      if (item === "All") {
        if (index === -1) {
          selectedItems.value = [...props.items];
        } else {
          selectedItems.value = [];
        }
      } else {
        if (index === -1) {
          selectedItems.value.push(item);
        } else {
          selectedItems.value.splice(index, 1);
        }
        const allIndex = selectedItems.value.indexOf("All");
        if (allIndex !== -1) {
          selectedItems.value.splice(allIndex, 1);
        }
      }
      emit("select", selectedItems.value);
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
      selectedItems,
    };
  },
};
</script>

<style scoped></style>
