<template>
  <div class="flex flex-col items-center justify-center w-screen mt-32"
  >
    <div class="flex flex-col gap-8 items-center ">

      <label  class="block text-7xl font-bold text-gray-700">
          Write your question
      </label>
    <TextInput @input="onChange" class=""></TextInput>
    <div class="flex flex-row gap-4">
      <Button class="button primary" @click="sendRequest">
        <template #right>Submit</template>
      </Button>
    </div>

    {{ answer.result }}
  </div>
</div>
</template>

<script>
import TextInput from "@/components/TextInput.vue";
import Button from "@/components/forms/Button.vue";
import {ref} from "vue";
import {computed} from "vue";
import axios from "axios";
import { onBeforeUnmount } from 'vue';

export default {
  name: "PromptPDf",
  components: {TextInput, Button},
  setup() {
    const query = ref('')
    const has_answer = ref(false)
    const loading_answer = ref(false)
    const answer = ref('')

    const settings = {
      hostName: 'hybridintelligence.eu',
      apiPath: '/api',
      basePath: '/chat-pdf',

      debugLevels: false,
      PRODUCTION_ORIGIN_PATTERN: '^.*$',
    }
    const baseUrl = computed(() => {
      return `https://${settings.hostName}${settings.basePath}${settings.apiPath}`
    })

    // const baseUrl = computed(() => {
    //   return `http://localhost:5000/api`
    // })

    const onChange = (value) => {
      query.value = value
    }

    const sendRequest = async () => {
      const request_data = {
        query: query.value,
      };
      loading_answer.value = true;
      has_answer.value = true;
      axios.post(baseUrl.value + '/api/ask-query/', request_data, {
              headers: {
                "Content-Type": "application/json",
              },
            })
          .then((response) => {
            answer.value = response.data;
            loading_answer.value = false;
            console.log(response.data);
          })
          .catch((error) => {
            console.log(error);
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
        await axios.get(baseUrl.value + '/api/erase-all/');
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
      onChange
    }
  }
}
</script>

<style scoped>

</style>