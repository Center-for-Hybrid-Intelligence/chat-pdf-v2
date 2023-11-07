const express = require('express');
const app = express();
const path = require('path');

app.use(express.static(path.join(__dirname, 'dist')));

const productionClientPath = path.join(__dirname, 'dist')
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist/index.html'));
});

const port = process.env.PORT || 3051;
app.listen(port, () => {
    console.log(`Server is running on port ${port}.`);
    if (process.env.NODE_ENV !== 'development') console.log('Production client files at:', productionClientPath)
});
