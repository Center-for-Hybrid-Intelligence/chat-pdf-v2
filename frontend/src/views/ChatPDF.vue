<template>
  <!--select or drop single or multiple files form using tailwindcss and compositionAPI-->
  <div
      class="bg-gradient-to-b to-gray-50 min-h-screen from-blue-200 flex flex-col items-center pt-24  max-w-screen ">
    <div class="max-w-6xl w-full">
      <div class="flex flex-col gap-8 items-center transition-all w-full  ">
        <h1 class="block text-3xl h8:text-5xl k15:text-6xl font-bold transition-all text-gray-700 px-10 " for="files">
          Chat with your PDFs
        </h1>
        <p class="block max-w-xl k1:text-2xl text-md px-10 text-gray-500 transition-all " for="files">
          Get quick answers and uncover insights from your documents with the magic of AI.
        </p>
        <div
            class="flex gap-2 flex-col justify-center border-4 border-transparent p-2 bg-white rounded-xl shadow-gray-300 shadow-2xl w-4/5"
            @dragenter="handleDragEnter"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @drop="handleDrop"
        >
          <label for="files">
            <div
                class="flex border p-6 py-12 hover:border-blue-500 group  hover:bg-slate-100 transition-all duration-300 border-dotted bg-slate-50 rounded-lg flex-col justify-center"
                :class="{ 'opacity-50 border-blue-500 bg-slate-200' : isDragging }"
            >
              <div class="flex gap-6 flex-col justify-center items-center">
                <svg class="w-10 h-10 text-blue-500 dark:text-white" aria-hidden="true"
                     xmlns="http://www.w3.org/2000/svg"
                     fill="none" viewBox="0 0 18 18">
                  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M1 10h3.439a.991.991 0 0 1 .908.6 3.978 3.978 0 0 0 7.306 0 .99.99 0 0 1 .908-.6H17M1 10v6a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-6M1 10l2-9h12l2 9"/>
                </svg>
                <span
                    class="flex gap-2 bg-blue-600 group-hover:bg-blue-800 transition-all duration-300 text-white justify-center font-extrabold k1:text-lg text-xs p-4 k1:px-12 px-6 rounded-full color cursor-pointer">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3.0"
               stroke="currentColor" class="k1:w-6 k1:h-6 w-3 h-3"> <path stroke-linecap="round" stroke-linejoin="round"
                                                                          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/> </svg>
          Upload PDFs

                </span>
                <input type="file"
                       id="files"
                       name="files"
                       accept="pdf/*"
                       class="hidden"
                       v-on:change="onFileChange"
                       multiple>
              </div>

              <div class="flex justify-center">
                <!--            <div v-if="isDragging">-->
                <!--              Drop the PDF files here-->
                <!--            </div>-->
                <div>
                  Or drop your PDF files here
                </div>
              </div>
            </div>
          </label>
        </div>
      </div>
      <div class="flex items-center justify-center w-full">
        <transition-group name="list" class="grid grid-cols-3 justify-center gap-4 py-6 w-4/5" tag="div">
          <div v-for="(file, index) in files" :key="index"
               class="pdf-preview relative bg-slate-50 shadow-md px-2 pb-2 rounded-lg">
            <div
                class="flex  gap-2 rounded-lg absolute left-0 w-full  bg-slate-50 rounded-t-lg"   >
              <div class="flex justify-between p-2 gap-2 break-all w-full whitespace-pre-wrap items-start">
                <h2 class="text-sm">{{ file.name }}</h2>
                <button
                    class="bg-red-500 hover:bg-red-700  text-white font-bold py-1 px-2 rounded max-h-12 "
                    @click="deleteFile(index)">
                  <svg class="w-4 h-4 text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
                       viewBox="0 0 18 20">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M1 5h16M7 8v8m4-8v8M7 1h4a1 1 0 0 1 1 1v3H6V2a1 1 0 0 1 1-1ZM3 5h12v13a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5Z"/>
                  </svg>
                </button>
              </div>
            </div>
            <iframe :src="file.previewURL" width="100%" height="400"></iframe>


<!--                        <object :data="file.previewURL" type="application/pdf" width="100%" height="400">-->
<!--              <p>This browser does not support PDFs. Please download the PDF to view it.</p>-->
<!--            </object>-->
          </div>
          <!--        <div v-for="(file, index) in files" :key="index" class=" w-11/12 k1:w-5/12  ">-->
          <!--        <div class="flex gap-4 justify-between p-4 shadow-2xl shadow-gray-300 rounded-xl ">-->
          <!--          <img src="pdf-placeholder.png" class="h-full w-16 object-contain "/>-->
          <!--          <div class="flex flex-col w-full  ">-->
          <!--            <h1 class="text-start self-start pb-2" style="-->
          <!--                display: -webkit-box;-->
          <!--                -webkit-line-clamp: 1;-->
          <!--                -webkit-box-orient: vertical;-->
          <!--                overflow: hidden;-->
          <!--                text-overflow: ellipsis;"-->
          <!--            >-->
          <!--              {{ file.name }}-->
          <!--            </h1>-->
          <!--            <div class="flex align-middle h-full gap-2 ">-->
          <!--              <input-->
          <!--                  v-model="file.author"-->
          <!--                  type="text"-->
          <!--                  class="mt-1 w-full px-2 py-1 border-gray-300 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"-->
          <!--                  placeholder="Author's Name"-->
          <!--              />-->
          <!--            </div>-->
          <!--          </div>-->

          <!--        </div>-->
          <!--        </div>-->
        </transition-group>
      </div>

      <div class="flex items-center justify-center w-full">
        <div
            class="border-4  w-4/5 k1:w-3/5 flex-col gap-2 border-transparent p-8 bg-white rounded-xl shadow-gray-300 shadow-2xl"
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
          <input min="10" max="800" step="1" type="range" :value="settings.chunk_size"
                 @input="event => updateSettingsValue('chunk_size', event.target.value)"
                 class="slider  mt-4"
                 id="weightSlider">
          <h1 class="heading4 flex">
            Chunk overlap (
            <div class="w-10 heading4">{{ settings.chunk_overlap || 2.5 }}</div>
            / 80)
          </h1>
          <h1 class="normalText">overlap in tokens between the piece of text extracted from your document</h1>
          <input min="0" max="80" step="1" type="range" :value="settings.chunk_overlap"
                 @input="event => updateSettingsValue('chunk_overlap', event.target.value)"
                 class="slider  mt-4"
                 id="weightSlider">
          <div class="" v-if="files.length > 0">
            <h1 class="heading4 flex">
              Your namespace
            </h1>
            <h1 class="normalText">Please enter your namespace if you want to continue your work. If you want to start
              new
              process you can generate and click to copy it so you can come back to your progress later!</h1>
            <div class="flex flex-col mt-3 h8:mt-0 gap-2 h8:gap-0 h8:flex-row h8:justify-center">
              <Button
                  class="button bg-gray-800 rounded rounded-2xl rounded-r-none p-2 px-6 text-xl font-bold h8:self-center transition-all duration-300"
                  @click="generateAndCopyToClipboard">
                <template #right>
                  {{ generated ? 'Copied' : 'Generate & Copy' }}
                </template>
              </Button>

              <input
                  :value="nameSpaceRender"
                  @input="event => nameSpaceRender = event.target.value"
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

    </div>
    <div v-if="loading" class="loading">Loading&#8230;</div>
  </div>

</template>

<script>
import {ref} from "vue";
import router from "@/router";
import {authService} from '@/api'
import Button from "@/components/forms/Button";
import {initializeSession} from "@/cookieHandler";
import {v4 as uuidv4} from 'uuid';

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
    // console.log(document.cookie)
    const loading = ref(false);
    const files = ref(props.value);
    const isDragging = ref(false);
    const uploadFailed = ref(false);
    const errorMessage = ref('');

    const previewList = ref([]);

    console.log(previewList,)
    const nameSpaceRender = ref('');
    const generated = ref(false);

    const settings = ref({
      chunk_size: 400,
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
        setTimeout(() => {
          generated.value = false
        }, 700)
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
          const blob = new Blob([file], {type: "application/pdf"});
          const previewURL = URL.createObjectURL(blob);
          files.value.push({formData, author: "", name: file.name, previewURL});
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
          const blob = new Blob([file], {type: "application/pdf"});
          const previewURL = URL.createObjectURL(blob);
          files.value.push({formData, author: "", name: file.name, previewURL});
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
      generated,
      previewList
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
