// project: aaDesign
// module: contact.js
// author: andrew b. auxier

// Contact form handling
const contactForm = document.querySelector('.contact');

contactForm.addEventListener('contact-submit-button', (e) => {
    e.preventDefault();
    console.log('submit clicked');
});
