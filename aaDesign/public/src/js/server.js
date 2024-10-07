
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 5000;

// Log the current directory
console.log("LOG: __dirname is", __dirname);

// Correct the static path by moving up two levels from 'js' to the project root
const staticPath = path.join(__dirname, '..', '..');
console.log("LOG - STATIC PATH: Serving static files from", staticPath);

// Serve static files from the correct 'app/src' directory
app.use(express.static(staticPath + "/src"));
app.use(express.static(staticPath));
app.use("/fonts", express.static(staticPath));


// Correct the path to contact.html by moving up two levels
const contactHtmlPath = path.join(__dirname, '..', '..', 'src', 'contact.html');
console.log("LOG - Path to contact.html:", contactHtmlPath);

// Serve the contact.html file
app.get('/', (req, res) => {
    console.log("LOG: Serving contact.html from", contactHtmlPath);
    res.sendFile(contactHtmlPath);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
