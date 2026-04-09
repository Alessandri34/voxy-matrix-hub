document.addEventListener("DOMContentLoaded", () => {
    // Basic Smooth Scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Elegant Parallax for Gold/Cyan Fusion Glow
    const glow = document.querySelector('.hero-bg-fusion');
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;

        if (glow) {
            glow.style.transform = `translate(-50%, -50%) translate(${x * 35}px, ${y * 35}px)`;
        }
    });
});
