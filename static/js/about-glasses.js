document.addEventListener('DOMContentLoaded', function() {
    const aboutCards = document.querySelectorAll('.about-glasses-card');
    const dots = document.querySelectorAll('.dot');
    let currentSlide = 0;
    
    
    function showSlide(idx) {
        aboutCards.forEach((card, i) => {
            card.style.display = (i === idx) ? 'block' : 'none';
        });
        
        
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === idx);
        });
    }
    
    
    function nextSlide() {
        currentSlide = (currentSlide + 1) % aboutCards.length;
        showSlide(currentSlide);
    }
    
    
    function prevSlide() {
        currentSlide = (currentSlide - 1 + aboutCards.length) % aboutCards.length;
        showSlide(currentSlide);
    }
    
    
    if (aboutCards.length > 0) {
        showSlide(0);
        
        
        const prevBtn = document.getElementById('about-prev');
        if (prevBtn) {
            prevBtn.addEventListener('click', prevSlide);
        }
        
        
        const nextBtn = document.getElementById('about-next');
        if (nextBtn) {
            nextBtn.addEventListener('click', nextSlide);
        }
        
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', function() {
                currentSlide = index;
                showSlide(currentSlide);
            });
        });
        
        
        let autoSlide = setInterval(nextSlide, 6000);
        
        
        const container = document.querySelector('.about-glasses-container');
        if (container) {
            container.addEventListener('mouseenter', () => {
                clearInterval(autoSlide);
            });
            
            container.addEventListener('mouseleave', () => {
                autoSlide = setInterval(nextSlide, 6000);
            });
        }
        
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                prevSlide();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
            }
        });
    }

    
    document.querySelectorAll('.about-readmore').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    
    document.querySelectorAll('.about-modal .close').forEach(function(btn) {
        btn.addEventListener('click', function() {
            closeModal(this.closest('.about-modal'));
        });
    });
    
    
    document.querySelectorAll('.about-modal .modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function() {
            closeModal(this.closest('.about-modal'));
        });
    });
    
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.about-modal.show').forEach(function(modal) {
                closeModal(modal);
            });
        }
    });
    
    
    function closeModal(modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    document.body.style.overflow = '';
    }
    
    
    window.onclick = function(event) {
        document.querySelectorAll('.about-modal').forEach(function(modal) {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    };
});