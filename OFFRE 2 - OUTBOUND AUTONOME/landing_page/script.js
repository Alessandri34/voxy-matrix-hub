document.addEventListener("DOMContentLoaded", () => {

    // Parallax logic for glowing background
    const glow = document.querySelector('.hero-bg-glow');
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;

        glow.style.transform = `translate(-50%, -50%) translate(${x * 40}px, ${y * 40}px)`;
    });

    // Smooth Scroll for UX
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

    // Console Animation Restart Loop (Optional feature to keep terminal active)
    const consoleLines = document.querySelectorAll('.typing-text');
    setInterval(() => {
        // Reset animation
        consoleLines.forEach(line => {
            line.style.animation = 'none';
            line.offsetHeight; /* trigger reflow */
            line.style.animation = null;
        });
    }, 12000); // loops every 12 seconds
});
