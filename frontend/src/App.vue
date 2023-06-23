<template >
  <router-view  />
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
scrollbar-gutter: stable both-edges;
  overflow-y: visible;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
/* Customize the width of the scrollbar */
::-webkit-scrollbar {
  width: 5px;
}

/* Customize the background color of the scrollbar track */
::-webkit-scrollbar-track {
  background-color: #f1f1f1;
}

/* Customize the scrollbar thumb (the draggable part) */
::-webkit-scrollbar-thumb {
  background-color: #2c3e50;
}

/* Add a hover effect on the scrollbar thumb */
::-webkit-scrollbar-thumb:hover {
  background-color: #555;
}
</style>
