<template>
  <div class="bg-gradient-to-b to-gray-50 min-h-screen  from-blue-200 flex flex-col items-center max-w-screen ">
    <div class="flex gap-2 min-h-screen  h-screen"
    >
      <div class=" p-12">
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
            <div class="w-2/3">
              <h1 class="heading2 flex">
                Temperature (
                <div class="w-10">{{ settings.llm_temperature }}</div>
                / 5)
              </h1>
              <h1 class="normalText">The closer temperature gets to 0 (zero) the more rational the answers will be,
                while the higher the value of the temperature, the more creative they get. </h1>
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
          <button @click="downloadCSV">Download CSV ("|" separator)</button>
          <h1 class="normalText"> {{ error }} </h1>
        </div>
        <div class="w-full flex flex-wrap justify-center gap-4 my-8" v-for="(question, index) in reversedQuestionList"
             :key="index">
          <div class="flex flex-col gap-4 border-2 border-green-600 w-full	 h8:max-w-2xl break-words rounded-s p-6"
               v-if="questionList.answers[questionList.questions.length - 1 - index]">
            <div class="block text-xs text-start font-medium text-gray-700">
              <div class="flex justify-between">
                <h1 class="heading2"> {{ reversedQuestionList[index] }} </h1>
                <div class="flex gap-4">
                  <button @click="tabClosed[question] = !tabClosed[question]"
                          class="transition-all flex items-center align-middle duration-200"
                          :class="{'transform ease-in-out rotate-180': tabClosed[question]}">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                         stroke="currentColor" class="w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/>
                    </svg>
                  </button>
                  <button @click="deleteQuestion(questionList.questions.length - 1 - index)"
                          class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded max-h-12 items-center align-middle">
                    Delete
                  </button>
                </div>
              </div>
              <div :class="{'hidden': tabClosed[question]}">
                {{ questionList.answers[questionList.questions.length - 1 - index] }}
                <h1 class="heading2"> Source documents </h1>
                <div style="white-space: pre-wrap">
                  <div
                      v-for="(source, index) in questionList.sourceDocuments[questionList.questions.length - 1 - index]"
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
      <div class="h-full">
        <!--        <label class="block text-4xl h8:text-5xl k15:text-7xl font-bold text-gray-700">-->
        <!--          Write your question-->
        <!--        </label>-->

        <div class="bg-white w-full rounded-xl h-full flex justify-between flex-col ">
          <div class="">
            <div class=" bg-slate-200 p-2 rounded-t-lg">
              Ask ChatPDF any question
            </div>
            <div class="overflow-y-scroll p-2 ">
              <div class="h-fit max-w-[90%] shadow-md w-fit bg-slate-100 rounded-lg p-2 my-4 text-start">
                <h1>Ask ChatPDF any question about the provided PDF files </h1>
              </div>
              <div
                  class="h-fit ml-auto shadow-md max-w-[90%] bg-blue-500 text-white w-fit bg-slate-200 rounded-lg p-2 my-4 text-start">
                <h1>Here is your question</h1>
              </div>
              <div class="h-fit max-w-[90%] shadow-md w-fit bg-slate-100 rounded-lg p-2 my-4 text-start">
                <h1>This should be the chat bot asnwer.......... ipsumLorem ipsumLorem ipsumLorem ipsumLorem ipsumLorem
                  ipsumLorem ipsumLorem ipsumLorem ipsumLorem ipsum </h1>
              </div>
              <div
                  class="h-fit ml-auto shadow-md max-w-[90%] bg-blue-500 text-white w-fit bg-slate-200 rounded-lg p-2 my-4 text-start">
                <h1>Here is your question</h1>
              </div>
            </div>
          </div>
          <div class="p-2 bg-white flex ">
            <TextArea ref="question" :placeholder="'Write your text here'" :isDisabled="loading" @input="onChange" class=" w-full">
            </TextArea>
            <button class="whitespace-nowrap bg-blue-500 text-white p-2 h-fit mt-auto rounded-r-lg">
              Submit Icon
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
  <div v-if="loading" class="loading">Loading&#8230;</div>

</template>

<script>
import TextArea from "@/components/forms/TextArea.vue";
import Button from "@/components/forms/Button.vue";
import {ref, reactive, computed, onMounted} from "vue";
import {onBeforeUnmount} from 'vue';
import {authService} from "@/api";
import DropdownSingle from "@/components/forms/DropdownSingle.vue";
import {initializeSession} from "@/cookieHandler";
import {saveAs} from 'file-saver';


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
      authors: [],
      titles: [],
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
      // questionList.questions.push(query.value);
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
            console.log(answer.value, 'answer')
            loading_answer.value = false;
            for (let i = 0; i < files.value.length; i++) {
              questionList.questions.push(query.value);
              questionList.answers.push(answer.value[i].result);
              questionList.sourceDocuments.push(answer.value[i].source_documents);
              questionList.authors.push(answer.value[i].author);
              questionList.titles.push(answer.value[i].title);
            }
            loading.value = false;
            query.value = '';
            ref.question.value = '';
            console.log(questionList, 'question list')
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

    function downloadCSV() {
      let data = questionList;

      let flatData = [];

      // Flatten the object
      for (let key in data) {
        data[key].forEach((item, index) => {
          if (flatData[index]) {
            flatData[index][key] = item;
          } else {
            flatData[index] = {[key]: item};
          }
        });
      }

      // Convert the flattened object to CSV
      let csvContent = '';
      let separator = '|';
      let header = Object.keys(flatData[0]).join(separator) + '\r\n';
      csvContent += header;

      flatData.forEach(function (row) {
        let rowData = Object.values(row).join(separator) + '\r\n';
        csvContent += rowData;
      });

      // Create a Blob with the CSV data
      let blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});

      saveAs(blob, "data.csv");
    }


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
      deleteQuestion,
      downloadCSV
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