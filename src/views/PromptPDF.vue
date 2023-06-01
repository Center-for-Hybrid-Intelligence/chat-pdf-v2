<template>
  <div class="flex flex-col items-center justify-center w-screen mt-32"
  >
    <div class="flex flex-col gap-8 items-center ">

      <label  class="block text-7xl font-bold text-gray-700">
          Write your question
      </label>
    <TextInput v-model="prompt" class=""></TextInput>
    <div class="flex flex-row gap-4">
      <Button class="button primary" @click="sendRequest">
        <template #right>Submit</template>
      </Button>
      <p> {{ answer.answer}}</p>
    </div>

  </div>
</div>
</template>

<script>
import TextInput from "@/components/TextInput.vue";
import Button from "@/components/forms/Button.vue";
import {ref} from "vue";
import parameters from "@/data/axes.json";
import {computed} from "vue";

export default {
  name: "PromptPDf",
  components: {TextInput, Button},
  setup() {
    const prompt = ref('')
    const has_prompt = ref(false)
    const has_answer = ref(false)
    const loading_answer = ref(false)
    const axes = ref(parameters)

    // const settings = {
    //   hostName: 'hybridintelligence.eu',
    //   apiPath: '/api/api',
    //   basePath: '/gpt-public',
    //
    //   debugLevels: false,
    //   PRODUCTION_ORIGIN_PATTERN: '^.*$',
    // }
    // const baseUrl = computed(() => {
    //   return `https://${settings.hostName}${settings.basePath}${settings.apiPath}`
    // })

    const baseUrl = computed(() => {
      return `http://localhost:5000/api`
    })

    const answer = ref({
      answer: '',
    })

    const sendRequest = async () => {
      prompt.value = "What is the meaning of life?"

      const request_data = {
        prompt: prompt.value,
      };
      loading_answer.value = true;
      has_answer.value = true;
      try {
        const res = await fetch(baseUrl.value + '/send-request/', {
          method: 'POST',
          body: JSON.stringify(request_data),
          headers: {
            'Content-Type': 'application/json'
          }
        });

        loading_answer.value = false;
        has_answer.value = true;

        // Create a readable stream from the response data
        const readableStream = res.body;

        // Create a TextDecoder to decode the streamed data
        const decoder = new TextDecoder();

        // Read the streamed data in chunks as it arrives
        const reader = readableStream.getReader();
        let result = '';

        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            break;
          }
          const chunk = decoder.decode(value, { stream: true });
          result += chunk;
          // Update UI with the streamed data in real time
          answer.value.answer = result;
        }
      } catch (error) {
        console.error(error);
      }
    };
    return {
      answer,
      axes,
      has_prompt,
      has_answer,
      prompt,
      sendRequest,};
  },
}
</script>

<style scoped>

</style>