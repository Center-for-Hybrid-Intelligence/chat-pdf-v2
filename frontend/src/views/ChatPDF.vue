<template>
  <!--select or drop single or multiple files form using tailwindcss and compositionAPI-->
  <div class="flex flex-col items-center justify-center w-screen mt-32"
  >
    <div class="flex flex-col gap-8 items-center ">

      <label class="block text-7xl font-bold text-gray-700" for="files">
        Upload PDF File
      </label>

      <div
          class="flex gap-4 flex-col justify-center border-4 border-transparent p-8 bg-white rounded-xl shadow-gray-300 shadow-2xl w-4/5"
          @dragenter="handleDragEnter"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
          :class="{ 'border-blue-500 bg-blue-100 border-4 border-dashed border-gray-400 rounded-lg p-8': isDragging }"
      >
        <div
            class="flex  flex-col justify-center"
            :class="{ 'opacity-50': isDragging }"
        >
          <label class="flex gap-4 flex-col justify-center items-center">

            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3.5" stroke=" #bfbfbf"
                 class="w-12 h-12 opacity-60">
              <path stroke-linecap="round" stroke-linejoin="round"
                    d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/>
            </svg>
            <span
                class="flex m-4 gap-2 bg-blue-600 hover:bg-blue-800 transition-all duration-300 text-white justify-center font-extrabold text-lg p-4 px-12 rounded-full color cursor-pointer">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3.0"
               stroke="currentColor" class="w-6 h-6"> <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/> </svg>
          Upload PDF

        </span>
            <input type="file"
                   id="files"
                   name="files"
                   accept="pdf/*"
                   class="hidden"
                   v-on:change="onFileChange"
                   multiple>
          </label>

          <div class="flex justify-center">


            <div v-if="isDragging">
              Drop the PDF file here
            </div>
            <div v-else>
              Or drop a PDF file
            </div>
          </div>
        </div>
      </div>

    </div>
    <transition-group name="list" class="mt-3 flex flex-wrap justify-center gap-4" tag="div">
      <div v-for="(file, index) in files" :key="index" class="mb-4 w-5/12 min-w-full ">
        <div class="flex my-2 gap-4 justify-between m-5 p-4 shadow-2xl w-full shadow-gray-300 rounded-xl ">
          <img src="pdf-placeholder.png" class="h-full w-16 object-contain place-self-center"/>
          <div class="flex flex-col w-full ">
            <h1 class="text-start self-start pb-2" style="
                display: -webkit-box;
                -webkit-line-clamp: 1;
                -webkit-box-orient: vertical;
                overflow: hidden;
                text-overflow: ellipsis;
"

            >
              {{ file.name }}
            </h1>
            <div class="flex align-middle h-full gap-2 ">
              <!--              <h1 class="text-mg font-bold place-self-center  ">
                                Author:
                            </h1>-->
              <input
                  v-model="file.author"
                  type="text"
                  class="mt-1 w-full px-2 py-1 border-gray-300 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                  placeholder="Author's Name"
              />
            </div>
          </div>
          <button
              class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded max-h-12 self-center place-self-center"
              @click="deleteFile(index)">
            Delete
          </button>
        </div>
      </div>
    </transition-group>

    <div class="flex justify-center m-12" v-if="files.length > 0">
      <input
          v-model="inputFieldValue"
          type="text"
          placeholder="Enter Namespace"
          class="px-2 py-1 border border-gray-400 rounded-l focus:outline-none"
      />
      <button @click="onsubmit()" :disabled="inputFieldValue === ''"
              :class="{ 'bg-green-300 text-black/20': inputFieldValue === '',
               'bg-green-500 text-white': inputFieldValue !== ''}"
              class="p-2 px-6 text-xl font-bold self-center rounded-r-lg transition-all duration-300">
        Submit
      </button>

    </div>
  </div>

</template>

<script>
import {computed, ref} from "vue";
import axios from "axios";
import router from "@/router";

export default {
  name: "FileUpload",
  components: {
  },
  props: {
    value: {
      type: Array,
      default: () => []
    }
  },
  emits: ["update:modelValue"],
  setup(props, {emit}) {
    const files = ref(props.value);
    const isDragging = ref(false);
    const inputFieldValue = ref('');

    const handleDragEnter = (e) => {
      e.preventDefault();
      isDragging.value = true;
    };

    const handleDragOver = (e) => {
      e.preventDefault();
      isDragging.value = true;
    };

    const handleDragLeave = () => {
      isDragging.value = false;
    };

    const handleDrop = (e) => {
      e.preventDefault();
      isDragging.value = false;

      const droppedFiles = e.dataTransfer.files;
      for (let i = 0; i < droppedFiles.length; i++) {
        const file = droppedFiles[i];
        if (file.type === "application/pdf") {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("name", file.name);
          formData.append("documentId", parseInt(Date.now().toString(36) + Math.random().toString(36).substr(2, 5), 36));
          files.value.push({formData: formData, author: ""})
          console.log(file.name, "file");
          console.log(files, "files");
        }

        emit("update:modelValue", files);
      }
    }

    const settings = {
      hostName: 'hybridintelligence.eu',
      apiPath: '/api/api',
      basePath: '/chat-pdf',

      debugLevels: false,
      PRODUCTION_ORIGIN_PATTERN: '^.*$',
    }
    const baseUrl = computed(() => {
      return `https://${settings.hostName}${settings.basePath}${settings.apiPath}`
    })

    const onFileChange = (e) => {
      const selectedFiles = e.target.files;
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        if (file.type === "application/pdf") {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("name", file.name);
          formData.append("documentId", parseInt(Date.now().toString(36) + Math.random().toString(36).substr(2, 5), 36));
          files.value.push({formData: formData, author: ""})
          console.log(file.name, "file");
          console.log(files, "files");
        }

        emit("update:modelValue", files);
      }
    }


    const onsubmit = async () => {
      const formDataList = [];

      for (let i = 0; i < files.value.length; i++) {
        const formData = files.value[i].formData;
        const author = files.value[i].author;

        formData.append("author", JSON.stringify(author));
        formData.append("namespace", JSON.stringify(inputFieldValue.value));


        formDataList.push(formData);
      }
      // const fileObject = { [inputFieldValue.value]: files.value };
      console.log(inputFieldValue.value, "inputFieldValue");

      const uploadPromises = formDataList.map(formData => {
        console.log(baseUrl.value + "/load-pdf/")
        return axios.post(baseUrl.value + "/load-pdf/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
      });

      try {
        const responses = await Promise.all(uploadPromises);
        console.log(responses);
      } catch (error) {
        console.error(error);
      }
      router.push({name: "promptPDF", params: { namespace: inputFieldValue.value }});
    };

    const deleteFile = (index) => {
      files.value.splice(index, 1);
      emit("update:modelValue", files.value);
    };
    return {
      files,
      onFileChange,
      deleteFile,
      isDragging,
      handleDragEnter,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      onsubmit,
      inputFieldValue
    }
  }
}
</script>

<style scoped>
.list-enter-active {
  transition: all 1s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(50px);
}

</style>
