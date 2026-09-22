

document.addEventListener('DOMContentLoaded', () => {
    
    const yearSpan = document.getElementById('currentYear');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    const typingText = document.getElementById('typing-text');
    if (typingText) {
        const text = "Smarter Libraries. Better Learning.";
        typingText.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                typingText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }

        setTimeout(typeWriter, 500);
    }

    const navbar = document.getElementById('mainNavbar');
    const scrollProgress = document.getElementById('scrollProgress');
    
    window.addEventListener('scroll', () => {
        
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        if (scrollProgress) {
            scrollProgress.style.width = scrolled + "%";
        }
    });

    const revealElements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');
    
    const revealOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };
    
    const revealOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                return;
            } else {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, revealOptions);
    
    revealElements.forEach(el => {
        revealOnScroll.observe(el);
    });

    const counters = document.querySelectorAll('.counter, .counter-float');
    let hasAnimated = false;
    
    const counterOptions = {
        threshold: 0.5
    };
    
    const animateCounters = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasAnimated) {
                hasAnimated = true; 
                
                counters.forEach(counter => {
                    const target = +counter.getAttribute('data-target');
                    const isFloat = counter.classList.contains('counter-float');
                    const duration = 2000; 
                    const stepTime = Math.abs(Math.floor(duration / target)) || 10;
                    
                    let current = 0;
                    
                    const updateCounter = () => {
                        const increment = target / (duration / 20);
                        
                        if (current < target) {
                            current += increment;
                            if (isFloat) {
                                counter.innerText = current.toFixed(1);
                            } else {
                                counter.innerText = Math.ceil(current).toLocaleString();
                            }
                            setTimeout(updateCounter, 20);
                        } else {
                            if (isFloat) {
                                counter.innerText = target.toFixed(1);
                            } else {
                                counter.innerText = target.toLocaleString();
                            }
                        }
                    };
                    
                    updateCounter();
                });
                
                observer.unobserve(entry.target);
            }
        });
    }, counterOptions);
    
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        animateCounters.observe(statsSection);
    }
});
