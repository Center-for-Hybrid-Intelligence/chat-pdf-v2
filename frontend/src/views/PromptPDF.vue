<template >
  <div class="flex flex-col justify-center mx-12  h6:mx-24 k1:mx-48 k15:mx-96 my-32"
  >
    <div class="flex flex-col gap-8 items-center w-full ">

      <label class="block text-4xl h8:text-5xl k15:text-7xl font-bold text-gray-700">
        Write your question
      </label>

      <TextArea ref="question" :isDisabled="loading" @input="onChange" class="h-64 w-full k15:w-1/2"></TextArea>

      <div class="w-full flex flex-wrap justify-center gap-4 my-8">
        <div v-for="(file, index) in files" :key="index"
             class="w-full k1:w-5/12">
          <div class="flex gap-4  p-4 shadow-2xl shadow-gray-300 rounded-xl ">
            <img src="/pdf-placeholder.png" class="h-full w-8 object-contain "/>
            <div class="flex flex-col justify-center">
              <h1 class="text-start" style="
                display: -webkit-box;
                -webkit-line-clamp: 1;
                -webkit-box-orient: vertical;
                overflow: hidden;
                text-overflow: ellipsis;
"
              >
                {{ file.title }}

              </h1>
              <div v-if="file.author" class="flex align-middle h-full gap-2 ">

                {{ file.author }}

              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex-col gap-6">


        <div class="w-full flex justify-center gap-8">
          <div class="">
            <h1 class="heading2 flex">
              Temperature (
              <div class="w-10">{{ settings.llm_temperature }}</div>
              / 5)
            </h1>
            <h1 class="normalText">The closer it gets to 0 zero the more rational it behaves, the higher the more
              creative it gets. </h1>
            <input min="0" max="5" step="0.1" type="range" :value="settings.llm_temperature" @input="tempChange"
                   class="slider w-full mt-4"
                   id="weightSlider">
          </div>

          <div class="flex-col w-max items-stretch">
            <h1 class="heading2">
              Model used
            </h1>
            <h1 class="normalText">Different models interpret text differently. </h1>

            <DropdownSingle class="mt-4 flex" :items="['gpt-3.5-turbo', 'gpt-4']" :selected="settings.llm_model"
                            @select="modelChange"></DropdownSingle>
          </div>
        </div>
      </div>


      <div class="flex flex-row gap-4">
        <Button :isDisabled="loading" class="button primary" @click="sendRequest">
          <template #right>
            <div v-if="loading">Loading results</div>
            <div v-else>Submit</div>
          </template>
        </Button>
        <h1 class="normalText"> {{ error }} </h1>
      </div>
    <div class="w-full flex flex-wrap justify-center gap-4 my-8" v-for="(question, index) in reversedQuestionList" :key="index">
      <div class="flex flex-col gap-4 border-2 border-green-600 w-full	 h8:max-w-2xl break-words rounded-s p-6" v-if="questionList.answers[questionList.questions.length - 1 - index]">
        <div class="block text-xs text-start font-medium text-gray-700">
          <div class="flex justify-between">
          <h1 class="heading2"> {{ reversedQuestionList[index] }} </h1>
          <div class="flex gap-4">
            <button @click="tabClosed[question] = !tabClosed[question]" class="transition-all flex items-center align-middle duration-200" :class="{'transform ease-in-out rotate-180': tabClosed[question]}">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
            </button>
            <button @click="deleteQuestion(questionList.questions.length - 1 - index)" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded max-h-12 items-center align-middle">Delete</button>
          </div>
          </div>
          <div :class="{'hidden': tabClosed[question]}">
          {{ questionList.answers[questionList.questions.length - 1 - index] }}
            <h1 class="heading2"> Source documents </h1>
            <div style="white-space: pre-wrap">
              <div v-for="(source, index) in questionList.sourceDocuments[questionList.questions.length - 1 - index]"
                   :key="index">
                <h1 class="heading3">Source </h1>
                <div class="mb-4" v-for="(specificSource, index) in source" :key="index">
                  <div v-if="!(index % 2 === 0)"><h1 class="heading4">Found in</h1></div>
                  <span :class="{'text-blue-600': !(index % 2 === 0)}">{{ specificSource }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
    </div>   <div v-if="loading" class="loading">Loading&#8230;</div>
</template>

<script>
import TextArea from "@/components/forms/TextArea.vue";
import Button from "@/components/forms/Button.vue";
import {ref, reactive, computed, onMounted} from "vue";
import {onBeforeUnmount} from 'vue';
import {authService} from "@/api";
import DropdownSingle from "@/components/forms/DropdownSingle.vue";
import {initializeSession} from "@/cookieHandler";


export default {
  name: "PromptPDf",
  components: {DropdownSingle, Button, TextArea},
  setup() {
    initializeSession();
    console.log(document.cookie, 'cookie')
    const query = ref('')
    const has_answer = ref(false)
    const loading_answer = ref(false)
    const answer = ref('')
    const error = ref('')
    const questionList = reactive({
      questions: [],
      answers: [],
      sourceDocuments: [],
    });

    const tabClosed = reactive({})

    let files = ref([])
    onMounted(() => {
      console.log('mounted')
      authService.get('/get-files/', {
        headers: {
          "Content-Type": "application/json",
        },
      })
          .then((response) => {
            files.value = response.data
            console.log(response)
          })
          .catch((error) => {
            console.log(error);
          });
    })

    const settings = ref({
      llm_temperature: 0,
      llm_model: "gpt-4",
    })

    const tempChange = (e) => {
      settings.value.llm_temperature = e.target.value
    }

    const modelChange = value => {
      settings.value.llm_model = value
    }

    const loading = ref(false);

    const onChange = (value) => {
      query.value = value
    }

    const deleteQuestion = (index) => {
      questionList.questions.splice(index, 1);
      questionList.answers.splice(index, 1);
      questionList.sourceDocuments.splice(index, 1);
    }

    document.body.addEventListener('keydown', (event) => {
      if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
        sendRequest();
      }
    });

    const reversedQuestionList = computed(() => { // Define computed property
      return questionList.questions.slice().reverse();
    });

    const sendRequest = async () => {
      if (query.value === '') {

        return;
      }
      loading.value = true;
      questionList.questions.push(query.value);
      const request_data = {
        query: query.value,
        settings: settings.value,
      };
      loading_answer.value = true;
      has_answer.value = true;
      console.log(document.cookie, 'cookie in send request')
      authService.post('/ask-query/', request_data, {
        headers: {
          "Content-Type": "application/json",
        },
      })
          .then((response) => {
            console.log(response)
            answer.value = response.data;
            loading_answer.value = false;
            questionList.answers.push(answer.value.result);
            questionList.sourceDocuments.push(answer.value.source_documents);
            loading.value = false;
            query.value = '';
            ref.question.value = '';
          })
          .catch((error) => {
            error.value = error.response;
            loading.value = false;
          });
    }

    const handleBeforeUnload = () => {
      eraseEntries();
    };

    const handlePopstate = () => {
      eraseEntries();
    };


    // Hook to execute the handleBeforeUnload function when the component is being unmounted
    onBeforeUnmount(() => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    });

    // Attach the event listener to the window's onbeforeunload event
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Hook to execute the handlePopstate function when the component is being unmounted
    onBeforeUnmount(() => {
      window.removeEventListener('popstate', handlePopstate);
    });

    // Attach the event listener to the window's onpopstate event
    window.addEventListener('popstate', handlePopstate);


    const eraseEntries = async () => {
      try {
        await authService.get('/erase-all/');
        console.log('HTTP request sent!');
      } catch (error) {
        console.error('Failed to send HTTP request:', error);
      }
    };

    return {
      answer,
      has_answer,
      query,
      sendRequest,
      onChange,
      questionList,
      loading,
      reversedQuestionList,
      tempChange,
      settings,
      modelChange,
      error,
      files,
      tabClosed,
      deleteQuestion
    }
  }
}
</script>

<style scoped>


.slider:hover {
  opacity: 1;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 1.4rem;
  height: 1.4rem;
  background-color: #4B5563;
  border-radius: 9999px;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 1rem;
  height: 1rem;
  background-color: #4B5563;
  border-radius: 9999px;
  cursor: pointer;
}
</style>