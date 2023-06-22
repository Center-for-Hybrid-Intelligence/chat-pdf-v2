<template>
  <!--select or drop single or multiple files form using tailwindcss and compositionAPI-->
  <div class="flex flex-col items-center justify-center w-screen mt-32"
  >
    <div class="flex flex-col gap-8 items-center w-full k1:w-1/2">

      <label class="block text-4xl h8:text-5xl k15:text-7xl font-bold text-gray-700" for="files">
        ChatPDF
      </label>

      <div
          class="flex gap-2 flex-col justify-center border-4 border-transparent p-8 bg-white rounded-xl shadow-gray-300 shadow-2xl w-4/5"
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
               stroke="currentColor" class="w-6 h-6"> <path stroke-linecap="round" stroke-linejoin="round"
                                                            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/> </svg>
          Upload PDF's

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
              Drop the PDF files here
            </div>
            <div v-else>
              Or drop your PDF files here
            </div>
          </div>
        </div>

      </div>
    </div>
    <transition-group name="list" class="w-full flex flex-wrap justify-center gap-4 my-8" tag="div">
      <div v-for="(file, index) in files" :key="index" class=" w-11/12 k1:w-5/12  ">
        <div class="flex gap-4 justify-between p-4 shadow-2xl shadow-gray-300 rounded-xl ">
          <img src="pdf-placeholder.png" class="h-full w-16 object-contain "/>
          <div class="flex flex-col w-full  ">
            <h1 class="text-start self-start pb-2" style="
                display: -webkit-box;
                -webkit-line-clamp: 1;
                -webkit-box-orient: vertical;
                overflow: hidden;
                text-overflow: ellipsis;"
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
              class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded max-h-12 self-end place-self-center"
              @click="deleteFile(index)">
            Delete
          </button>
        </div>
      </div>
    </transition-group>

    <div class="border-4  w-4/5 k1:w-3/5 flex-col gap-2 border-transparent p-8 bg-white rounded-xl shadow-gray-300 shadow-2xl"
         v-if="files.length > 0">
      <h1 class="heading2">
        Customize your request
      </h1>
      <h1 class="heading4 flex">
        Chunk size (
        <div class="w-10 heading4">{{ settings.chunk_size || 2.5 }}</div>
        / 800)
      </h1>
      <h1 class="normalText">Average length in tokens of the pieces of text that will be extracted and retrieve from
        your document. small sentences: less than 30, big paragraphs: 400</h1>
      <input min="10" max="800" step="1" type="range" :value="settings.chunk_size" @input="event => updateSettingsValue('chunk_size', event.target.value)"
             class="slider  mt-4"
             id="weightSlider">
      <h1 class="heading4 flex">
        Chunk overlap (
        <div class="w-10 heading4">{{ settings.chunk_overlap || 2.5 }}</div>
        / 80)
      </h1>
      <h1 class="normalText">overlap in tokens between the piece of text extracted from your document</h1>
      <input min="0" max="80" step="1" type="range" :value="settings.chunk_overlap" @input="event => updateSettingsValue('chunk_overlap', event.target.value)"
             class="slider  mt-4"
             id="weightSlider">
      <div class=""  v-if="files.length > 0">
        <h1 class="heading4 flex">
          Your namespace
        </h1>
        <h1 class="normalText">Please enter your namespace if you want to continue your work. If you want to start new process you can generate and click to copy it so you can come back to your progress later!</h1>
        <div class="flex flex-col gap-2 h8:gap-0 h8:flex-row h8:justify-center">
          <Button class="button bg-gray-800 rounded rounded-2xl rounded-r-none p-2 px-6 text-xl font-bold h8:self-center transition-all duration-300"  @click="generateAndCopyToClipboard">
            <template #right>
              {{generated ? 'Copied' : 'Generate & Copy'}}
            </template>
          </Button>

        <input
            :value="nameSpaceRender"
            @change="event => nameSpaceRender = event.target.value"
            type="text"
            placeholder="Enter Namespace"
            class="px-2 py-1 h8:flex-grow h8:flex-1 w-max border border-gray-400 w-max focus:outline-none"
        />
        <Button @click="onsubmit" :isDisabled="nameSpaceRender === '' || loading"
                :class="{ 'text-black/20': nameSpaceRender === '',
               ' text-white': nameSpaceRender !== ''}"
                class="button flex-0 p-2 px-6 text-xl font-bold h8:self-center rounded-r-lg rounded-l-none transition-all duration-300">
          <template #right>
            <div v-if="loading">Loading</div>
            <div v-else>Submit</div>
          </template>
        </Button>


        </div>
        <div v-if="uploadFailed">
          {{ errorMessage }}
        </div>
      </div>
    </div>

  </div>

</template>

<script>
import {ref} from "vue";
import router from "@/router";
import {authService} from '@/api'
import Button from "@/components/forms/Button";
import {initializeSession} from "@/cookieHandler";
import { v4 as uuidv4 } from 'uuid';

export default {
  name: "FileUpload",
  components: {
    Button
  },
  props: {
    value: {
      type: Array,
      default: () => []
    }
  },
  emits: ["update:modelValue"],
  setup(props, {emit}) {
    initializeSession()
    console.log(document.cookie)
    const loading = ref(false);
    const files = ref(props.value);
    const isDragging = ref(false);
    const uploadFailed = ref(false);
    const errorMessage = ref('');

  /*  const testSetup = () => {
      for (let i = 0; i < 3; i++) {
        const formData = new FormData();
        formData.append("documentId", parseInt(Date.now().toString(36) + Math.random().toString(36).substr(2, 5), 36));
        formData.append("file", "testFile");
        formData.append("name", "testName");
        files.value.push({formData: formData, author: ""})
      }
    }
    testSetup()*/

    const nameSpaceRender = ref('')
  const generated = ref(false)

    const settings = ref({
      chunk_size: 200,
      chunk_overlap: 50,
    });

    const updateSettingsValue = (propertyName, value) => {
      settings.value[propertyName] = value;
      console.log(settings.value)
    };
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

    const generateAndCopyToClipboard = () => {
      nameSpaceRender.value = uuidv4()
      copyToClipboard(nameSpaceRender.value)
    }
    const copyToClipboard = async (value) => {
      try {
        await navigator.clipboard.writeText(value);
        setTimeout(()=> {
          generated.value = false
        },700)
        generated.value = true
      } catch (err) {
        nameSpaceRender.value = "Failed to copy text: " + err
      }
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
          formData.append("documentId", uuidv4());
          files.value.push({formData: formData, author: "", name: file.name})
          console.log(file.name, "file");
          console.log(files, "files");
        }

        emit("update:modelValue", files);
      }
    }

    const onFileChange = (e) => {
      const selectedFiles = e.target.files;
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        if (file.type === "application/pdf") {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("name", file.name);
          formData.append("documentId", uuidv4());
          files.value.push({formData: formData, author: "", name: file.name})
          console.log(file.name, "file");
          console.log(files, "files");
        }

        emit("update:modelValue", files);
      }
    }


    const onSubmit = async () => {
      uploadFailed.value = false;
      loading.value = true;
      const formDataList = [];

      for (let i = 0; i < files.value.length; i++) {
        const formData = files.value[i].formData;
        const author = files.value[i].author;

        formData.append("author", author);
        formData.append("namespace", nameSpaceRender.value);
        formData.append("settings", JSON.stringify(settings.value));

        formDataList.push(formData);
      }
      console.log(formDataList);

      try {
        for (const formData of formDataList) {
          await authService.post("/load-pdf/", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
        }
        loading.value = false;
        router.push({name: "promptPDF", params: {namespace: nameSpaceRender.value}});
      } catch (error) {
        console.error(error);
        loading.value = false;
        uploadFailed.value = true;
        errorMessage.value = error.response;
      }
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
      onsubmit: onSubmit,
      loading,
      uploadFailed,
      errorMessage,
      settings,
      updateSettingsValue,
      nameSpaceRender,
      copyToClipboard,
      generateAndCopyToClipboard,
      generated
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
