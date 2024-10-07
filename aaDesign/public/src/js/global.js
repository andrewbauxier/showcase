// project: aaDesign
// module: common.js
// author: andrew b. auxier

// Function to initialize the page
function initializeCommonPage() {
    console.log('Initializing common page features...');
    try {
        // Load navigation and footer by calling their respective functions
        Promise.all([loadNav(), loadFooter()])
            .then(() => {
                console.log('Nav and footer loaded. Other features can be initialized...');
            })
            .catch((error) => {
                console.error('ERROR INITIALIZING COMMON PAGE PROMISE:', error);
            });
    } catch (error) {
        console.error('ERROR INITIALIZING COMMON PAGE:', error);
    }
}

// Event listener for DOMContentLoaded
document.addEventListener('DOMContentLoaded', initializeCommonPage);
