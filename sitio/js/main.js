// Mobile Menu Toggle
const mobileToggle = document.getElementById('mobile-toggle');
const nav = document.getElementById('nav');

mobileToggle.addEventListener('click', () => {
    nav.classList.toggle('active');
    mobileToggle.classList.toggle('active');
});

// Close mobile menu when clicking nav link
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        nav.classList.remove('active');
        mobileToggle.classList.remove('active');
    });
});

// Header scroll effect
const header = document.getElementById('header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        header.style.boxShadow = 'none';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    }
    
    lastScroll = currentScroll;
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const offsetTop = target.offsetTop - 70;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        }
    });
});

// ========================================
// PROTECCIÓN DE IMÁGENES
// ========================================

// Disable right-click on images
const allImages = document.querySelectorAll('img');
allImages.forEach(img => {
    // Prevent right-click
    img.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });
    
    // Prevent drag
    img.addEventListener('dragstart', (e) => {
        e.preventDefault();
        return false;
    });
    
    // Add user-select none
    img.style.userSelect = 'none';
    img.style.webkitUserSelect = 'none';
    img.style.mozUserSelect = 'none';
    img.style.msUserSelect = 'none';
    
    // Prevent selection
    img.setAttribute('draggable', 'false');
});

// Disable right-click on entire document (optional - puedes comentar si es muy restrictivo)
// document.addEventListener('contextmenu', (e) => {
//     if (e.target.tagName === 'IMG') {
//         e.preventDefault();
//         return false;
//     }
// });

// Disable common keyboard shortcuts for saving
document.addEventListener('keydown', (e) => {
    // Ctrl+S or Cmd+S
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        if (document.activeElement.tagName === 'IMG' || 
            e.target.tagName === 'IMG') {
            e.preventDefault();
            return false;
        }
    }
});

// ========================================
// ANIMATIONS
// ========================================

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements with animation classes
document.querySelectorAll('.servicio-card, .location-tag, .galeria-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// ========================================
// LIGHTBOX GALLERY
// ========================================

// Simple lightbox for gallery
const galeriaItems = document.querySelectorAll('.galeria-item');
galeriaItems.forEach(item => {
    item.addEventListener('click', () => {
        const img = item.querySelector('img');
        const lightbox = document.createElement('div');
        lightbox.classList.add('lightbox');
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <img src="${img.src}" alt="${img.alt}" draggable="false">
                <span class="lightbox-close">&times;</span>
            </div>
        `;
        document.body.appendChild(lightbox);
        document.body.style.overflow = 'hidden';
        
        // Protect lightbox image too
        const lightboxImg = lightbox.querySelector('img');
        lightboxImg.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });
        lightboxImg.addEventListener('dragstart', (e) => {
            e.preventDefault();
            return false;
        });
        
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox || e.target.classList.contains('lightbox-close')) {
                lightbox.remove();
                document.body.style.overflow = 'auto';
            }
        });
    });
});

// Lightbox styles (injected via JS)
const lightboxStyles = document.createElement('style');
lightboxStyles.textContent = `
    .lightbox {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.95);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        animation: fadeIn 0.3s ease;
    }
    
    .lightbox-content {
        position: relative;
        max-width: 90%;
        max-height: 90%;
    }
    
    .lightbox img {
        max-width: 100%;
        max-height: 90vh;
        object-fit: contain;
        border-radius: 5px;
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        pointer-events: none;
    }
    
    .lightbox-close {
        position: absolute;
        top: -40px;
        right: 0;
        font-size: 40px;
        color: white;
        cursor: pointer;
        font-weight: 300;
        transition: color 0.3s ease;
        z-index: 10001;
    }
    
    .lightbox-close:hover {
        color: #FF6B35;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(lightboxStyles);

console.log('🚀 Vive Volando Nómade - Landing Page loaded!');
console.log('🔒 Image protection enabled');