import { createStore } from 'vuex';

const store = createStore({
  state() {
    return {
      sessionCookie: null,
    };
  },
  mutations: {
    setSessionCookie(state, cookie) {
      state.sessionCookie = cookie;
    },
  },
});

export default store;