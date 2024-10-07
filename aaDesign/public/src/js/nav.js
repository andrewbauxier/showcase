// project: aaDesign
// module: nav.js
// author: andrew b. auxier

function loadNav() {
    console.log('Loading navigation...');
    return fetch('./nav.html') // Ensure correct path for nav.html
        .then((response) => {
            if (!response.ok) throw new Error(`FAILED TO LOAD nav.html: ${response.statusText}`);
            return response.text();
        })
        .then((data) => {
            document.querySelector('nav').innerHTML = data;
        })
        .catch((error) => {
            console.error('ERROR LOADING NAV:', error);
        });
}
