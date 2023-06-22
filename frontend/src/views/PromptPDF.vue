<template>
  <div class="flex flex-col justify-center mx-12  h6:mx-24 k1:mx-48 k15:mx-96 my-32"
  >
    <div class="flex flex-col gap-8 items-center w-full">

      <label class="block text-7xl font-bold text-gray-700">
        Write your question
      </label>

      <TextArea ref="question" :isDisabled="loading" @input="onChange" class="h-64 w-full k1:w-2/3"></TextArea>
      <div class="flex-col gap-6">


        <div class="w-full flex justify-center gap-8">
        <div class="items-start">
        <h1 class="heading2 flex">
          Temperature (
          <div class="w-10">{{ settings.llm_temperature }}</div>
          / 5)
        </h1>
        <h1 class="normalText">The closer it gets to 0 zero the more rational it behaves, the higher the more creative it gets. </h1>
        <input min="0" max="5" step="0.1" type="range" :value="settings.llm_temperature" @input="tempChange" class="slider w-full mt-4"
               id="weightSlider">
        </div>

        <div class="items-start">
          <h1 class="heading2">
            Model used
          </h1>
          <h1 class="normalText">Different models interpret text differently. </h1>
          <DropdownSingle class="mt-4" :items="['gpt-3.5-turbo', 'gpt-4']" :selected="settings.llm_model" @select="modelChange"></DropdownSingle>
        </div>
      </div>
      </div>


      <div class="flex flex-row gap-4">
        <Button :isDisabled="loading" class="button primary" @click="sendRequest">
          <template #right><div v-if="loading">Loading results</div> <div v-else>Submit</div></template>
        </Button>
        <h1 class="normalText"> {{error}} </h1>
      </div>

    <div class="w-full flex flex-wrap justify-center gap-4 my-8" v-for="(question, index) in reversedQuestionList" :key="index">
      <div class="flex flex-col gap-4 border-2 border-green-600 w-full	 h8:max-w-2xl break-words rounded-s p-6" v-if="questionList.answers[questionList.questions.length - 1 - index]">
        <div class="block text-xs text-start font-medium text-gray-700">
          <h1 class="heading2"> {{ reversedQuestionList[index] }} </h1>
          {{ questionList.answers[questionList.questions.length - 1 - index] }}
            <h1 class="heading2"> Source documents </h1>
            <div style="white-space: pre-wrap">
              <div v-for="(source, index) in questionList.sourceDocuments[questionList.questions.length - 1 - index]" :key="index">
                <h1 class="heading3">Source </h1>
                <div class="mb-4" v-for="(specificSource, index) in source" :key="index">
                  <div v-if="!(index % 2 === 0)"><h1 class="heading4">Found in</h1></div>
                  <span  :class="{'text-blue-600': !(index % 2 === 0)}">{{ specificSource }}</span>
                </div>
              </div>
            </div>
        </div>
      </div>
    </div>
    </div>
  </div>    <div v-if="loading" class="loading">Loading&#8230;</div>

</template>

<script>
import TextArea from "@/components/forms/TextArea.vue";
import Button from "@/components/forms/Button.vue";
import {ref, reactive, computed, onMounted} from "vue";
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
    const error = ref('')
    const questionList = reactive({
      questions: [],
      answers: [],
      sourceDocuments: [],
    });

    onMounted(() => {
      console.log('mounted')
      authService.get('/get-files/', {
              headers: {
                "Content-Type": "application/json",
              },
            })
          .then((response) => {
            console.log(response)
          })
          .catch((error) => {
            console.log(error);
          });
    })

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

    document.body.addEventListener('keydown', (event) => {
      if(event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
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
      error
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
.loading {
  position: fixed;
  z-index: 999;
  height: 2em;
  width: 2em;
  overflow: visible;
  margin: auto;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}

/* Transparent Overlay */
.loading:before {
  content: '';
  display: block;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.3);
}

/* :not(:required) hides these rules from IE9 and below */
.loading:not(:required) {
  /* hide "loading..." text */
  font: 0/0 a;
  color: transparent;
  text-shadow: none;
  background-color: transparent;
  border: 0;
}

.loading:not(:required):after {
  content: '';
  display: block;
  font-size: 10px;
  width: 1em;
  height: 1em;
  margin-top: -0.5em;
  -webkit-animation: spinner 1500ms infinite linear;
  -moz-animation: spinner 1500ms infinite linear;
  -ms-animation: spinner 1500ms infinite linear;
  -o-animation: spinner 1500ms infinite linear;
  animation: spinner 1500ms infinite linear;
  border-radius: 0.5em;
  -webkit-box-shadow: rgba(0, 0, 0, 0.75) 1.5em 0 0 0, rgba(0, 0, 0, 0.75) 1.1em 1.1em 0 0, rgba(0, 0, 0, 0.75) 0 1.5em 0 0, rgba(0, 0, 0, 0.75) -1.1em 1.1em 0 0, rgba(0, 0, 0, 0.5) -1.5em 0 0 0, rgba(0, 0, 0, 0.5) -1.1em -1.1em 0 0, rgba(0, 0, 0, 0.75) 0 -1.5em 0 0, rgba(0, 0, 0, 0.75) 1.1em -1.1em 0 0;
  box-shadow: rgba(0, 0, 0, 0.75) 1.5em 0 0 0, rgba(0, 0, 0, 0.75) 1.1em 1.1em 0 0, rgba(0, 0, 0, 0.75) 0 1.5em 0 0, rgba(0, 0, 0, 0.75) -1.1em 1.1em 0 0, rgba(0, 0, 0, 0.75) -1.5em 0 0 0, rgba(0, 0, 0, 0.75) -1.1em -1.1em 0 0, rgba(0, 0, 0, 0.75) 0 -1.5em 0 0, rgba(0, 0, 0, 0.75) 1.1em -1.1em 0 0;
}

/* Animation */

@-webkit-keyframes spinner {
  0% {
    -webkit-transform: rotate(0deg);
    -moz-transform: rotate(0deg);
    -ms-transform: rotate(0deg);
    -o-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    -moz-transform: rotate(360deg);
    -ms-transform: rotate(360deg);
    -o-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
@-moz-keyframes spinner {
  0% {
    -webkit-transform: rotate(0deg);
    -moz-transform: rotate(0deg);
    -ms-transform: rotate(0deg);
    -o-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    -moz-transform: rotate(360deg);
    -ms-transform: rotate(360deg);
    -o-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
@-o-keyframes spinner {
  0% {
    -webkit-transform: rotate(0deg);
    -moz-transform: rotate(0deg);
    -ms-transform: rotate(0deg);
    -o-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    -moz-transform: rotate(360deg);
    -ms-transform: rotate(360deg);
    -o-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
@keyframes spinner {
  0% {
    -webkit-transform: rotate(0deg);
    -moz-transform: rotate(0deg);
    -ms-transform: rotate(0deg);
    -o-transform: rotate(0deg);
    transform: rotate(0deg);
  }
  100% {
    -webkit-transform: rotate(360deg);
    -moz-transform: rotate(360deg);
    -ms-transform: rotate(360deg);
    -o-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}
</style>