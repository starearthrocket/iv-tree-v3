const navToggle = document.querySelector(".nav-toggle");
const mainNav = document.querySelector(".main-nav");

if (navToggle && mainNav) {
    navToggle.addEventListener("click", () => {
        const isOpen = mainNav.classList.toggle("is-open");
        let navigationLabel = "Open navigation menu";

        if (isOpen) {
            navigationLabel = "Close navigation menu";
        }

        navToggle.setAttribute(
            "aria-expanded",
            isOpen.toString()
        );

        navToggle.setAttribute(
            "aria-label",
            navigationLabel
        );
    });
}