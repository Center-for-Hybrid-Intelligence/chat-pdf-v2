<template>
  <div class="flex flex-col items-center justify-center mt-32"
  >
    <div class="flex flex-col gap-8 items-center w-max">

      <label class="block text-7xl font-bold text-gray-700">
        Write your question
      </label>
      <TextArea ref="question" @input="onChange" class="h-64"></TextArea>


      <div class="w-max flex gap-24 justify-between">
        <div>
        <h1 class="heading2 flex">
          Temperature (
          <div class="w-10 heading2">{{ settings.llm_temperature || 2.5 }}</div>
          / 5)
        </h1>
        <h1 class="normalText">Higher values will make the model more creative but less reliable</h1>
        <input min="0" max="5" step="0.1" type="range" :value="settings.llm_temperature" @input="tempChange" class="slider k1:w-128 w-80 mt-4 self-center"
               id="weightSlider">
        </div>

        <div class="">
          <h1 class="heading2">
            Model
          </h1>
          <DropdownSingle :items="['gpt-3.5-turbo', 'gpt-4']" :selected="settings.llm_model" @select="modelChange"></DropdownSingle>
        </div>
      </div>


      <div class="flex flex-row gap-4">
        <Button :isDisabled="loading" class="button primary" @click="sendRequest">
          <template #right><div v-if="loading">Loading results</div> <div v-else>Submit</div></template>
        </Button>
      </div>

    <div class="mt-8 w-full" v-for="(question, index) in reversedQuestionList" :key="index">
      <div class="flex flex-col gap-4 border-2 border-green-600 w-full	 h8:max-w-2xl break-words rounded-s p-6" v-if="questionList.answers[questionList.questions.length - 1 - index]">
        <div class="block text-xs text-start font-medium text-gray-700">
          <h1 class="heading2"> {{ reversedQuestionList[index] }} </h1>
          {{ questionList.answers[questionList.questions.length - 1 - index] }}
            <h1 class="heading2"> Source documents </h1>
            <div style="white-space: pre-wrap">
              {{ questionList.sourceDocuments[questionList.questions.length - 1 - index] }}
            </div>
        </div>
      </div>
    </div>
    </div>

  </div>
</template>

<script>
import TextArea from "@/components/forms/TextArea.vue";
import Button from "@/components/forms/Button.vue";
import {ref, reactive, computed} from "vue";
import { onBeforeUnmount } from 'vue';
import { authService } from "@/api";
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

    const questionList = reactive({
      questions: [],
      answers: [],
      sourceDocuments: [],
    });

    const settings = ref( {
        llm_temperature: 0,
        llm_model: "gpt-4",
    } )

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

    const reversedQuestionList = computed(() => { // Define computed property
      return questionList.questions.slice().reverse();
    });

    const sendRequest = async () => {
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
            answer.value = response.data;
            loading_answer.value = false;
            questionList.answers.push(answer.value.result);
            questionList.sourceDocuments.push(answer.value.source_documents);
            console.log(response.data);
            loading.value = false;
            ref.question.value = '';
          })
          .catch((error) => {
            console.log(error);
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
      modelChange
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