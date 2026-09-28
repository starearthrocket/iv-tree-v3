const navToggle = document.querySelector('.nav-toggle');
const mainNav = document.querySelector('.main-nav');

if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
        const isOpen = mainNav.classList.toggle('is-open');

        navToggle.setAttribute(
            'aria-expanded',
            isOpen.toString()
        );

        navToggle.setAttribute(
            'aria-label',
            isOpen
                ? 'Close navigation menu'
                : 'Open navigation menu'
        );
    });
}
