import { useStore } from 'vuex';
import {onMounted, ref} from "vue";
import {v4 as uuidv4} from 'uuid';
import axios from "axios";

export function initializeSession() {
    const store = useStore();
    const sessionID = ref(null);

    onMounted(() => {
        // Get the session ID from the cookie
        sessionID.value = store.state.sessionCookie;
        // console.log(sessionID.value)
        // If session ID doesn't exist, generate a new one and store it in the cookie
        if (!sessionID.value) {
            sessionID.value = generateSessionID();
            document.cookie = `sessionID=${sessionID.value}`;
        }

        // Set the session ID as a default header for all API requests
        axios.defaults.headers.common['X-Session-ID'] = sessionID.value;

        // Update the session cookie value in the Vuex store
        store.commit('setSessionCookie', sessionID.value);
    });

    // Other utility functions or variables if needed

    return {
        sessionID,
    };
}

function generateSessionID() {
    return uuidv4();
}