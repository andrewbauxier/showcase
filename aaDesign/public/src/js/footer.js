// project: aaDesign
// module: footer.js
// author: andrew b. auxier

function loadFooter() {
    console.log('Loading footer...');
    return fetch('./footer.html') // Ensure correct path for footer.html
        .then((response) => {
            if (!response.ok) throw new Error(`FAILED TO LOAD footer.html: ${response.statusText}`);
            return response.text();
        })
        .then((data) => {
            document.querySelector('footer').innerHTML = data;
        })
        .catch((error) => {
            console.error('ERROR LOADING FOOTER:', error);
        });
}
