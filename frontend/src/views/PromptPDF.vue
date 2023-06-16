<template>
  <div class="flex flex-col items-center justify-center w-screen mt-32"
  >
    <div class="flex flex-col gap-8 items-center">

      <label class="block text-7xl font-bold text-gray-700">
        Write your question
      </label>
      <TextArea @input="onChange" class="h-64"></TextArea>
      <div class="flex flex-row gap-4">
        <Button :isDisabled="loading" class="button primary" @click="sendRequest">
          <template #right>Submit</template>
        </Button>
        {{loading}}
      </div>
      <div v-for="(question, index) in questionList.questions.reverse()" :key="index">
        <div class="flex flex-col gap-4 items-center border-2 border-green-600 max-w-screen-h4 h8:max-w-2xl break-words rounded-s p-6" v-if="answer.result" >
          <div class="block text-xs text-start font-medium text-gray-700">
            <h1 class="heading2"> {{ question }} </h1>
             {{questionList.answers[index]}}
            <div class="text-blue-950">
              <h1 class="heading2"> Source documents </h1>
              <div
              style="white-space: pre-wrap"
              >
                {{ answer.source_documents }}
              </div></div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import TextArea from "@/components/forms/TextArea.vue";
import Button from "@/components/forms/Button.vue";
import {ref, reactive} from "vue";
import { onBeforeUnmount } from 'vue';
import { authService } from "@/api";

export default {
  name: "PromptPDf",
  components: {Button, TextArea},
  setup() {
    const query = ref('')
    const has_answer = ref(false)
    const loading_answer = ref(false)
    const answer = ref('')

    const questionList = reactive({
      questions: [],
      answers: [],
      sourceDocuments: [],
    });

    const loading = ref(false);

    const onChange = (value) => {
      query.value = value
    }

    const sendRequest = async () => {
      loading.value = true;
      questionList.questions.push(query.value);
      const request_data = {
        query: query.value,
      };
      loading_answer.value = true;
      has_answer.value = true;
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
      loading
    }
  }
}
</script>

<style scoped>

</style>