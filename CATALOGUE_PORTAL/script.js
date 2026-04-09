/* ================================================================
   VOXY MATRIX — CATALOGUE PORTAL
   JS Ethereal / Awwwards-Tier
   ================================================================ */

document.addEventListener("DOMContentLoaded", () => {

    // 1. ETHEREAL SCROLL REVEAL (IntersectionObserver)
    const revealElements = document.querySelectorAll('.ethereal-reveal');

    const revealOptions = {
        root: null,
        rootMargin: '0px 0px -100px 0px',
        threshold: 0.1
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, revealOptions);

    revealElements.forEach(el => revealObserver.observe(el));

    // 2. FAQ EDITORIAL ACCORDION
    const faqRows = document.querySelectorAll('.faq-row');

    faqRows.forEach(row => {
        const btn = row.querySelector('.faq-btn');
        const answer = row.querySelector('.faq-answer');

        btn.addEventListener('click', () => {
            const isActive = row.classList.contains('active');

            // Close all
            faqRows.forEach(r => {
                r.classList.remove('active');
                const a = r.querySelector('.faq-answer');
                if (a) a.style.maxHeight = '0';
            });

            // Open clicked if it wasn't active
            if (!isActive) {
                row.classList.add('active');
                answer.style.maxHeight = answer.scrollHeight + 100 + 'px'; // +100px for padding compensation
            }
        });
    });

});
