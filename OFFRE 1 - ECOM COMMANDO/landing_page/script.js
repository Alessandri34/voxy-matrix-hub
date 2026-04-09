document.addEventListener("DOMContentLoaded", () => {
    // Parallax effect on hero background glow
    const glow = document.querySelector('.hero-bg-glow');
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        glow.style.transform = `translate(-50%, -50%) translate(${x * 30}px, ${y * 30}px)`;
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
