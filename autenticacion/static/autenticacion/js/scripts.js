// Custom JavaScript for DataCore Website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS with custom settings
    AOS.init({
        once: true,           // Animation happens only once
        duration: 800,        // Base duration
        easing: 'ease-in-out' // Smooth animation
    });

    // Get elements for navbar transformation
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');
    const stickyNav = document.querySelector('.sticky-nav');
    const navbarContainer = document.querySelector('.navbar-container');
    const logoContainer = document.querySelector('.logo-container');
    const navbarNav = document.querySelector('.navbar-nav');
    const loginBtn = document.querySelector('.login-btn');
    const loginBtnContainer = document.querySelector('.ms-4');
    
    // Track scroll position and update navbar appearance
    window.addEventListener('scroll', function() {
        let current = '';
        const scrollPosition = window.pageYOffset;
        const homeSection = document.querySelector('#home');
        const homeSectionBottom = homeSection.offsetTop + homeSection.offsetHeight;
        
        // Check if we're past the home section
        if (scrollPosition > homeSectionBottom - 200) {
            // Outside home section - transform to login-only mode
            if (!stickyNav.classList.contains('login-only-mode')) {
                stickyNav.classList.add('login-only-mode');
                
                // Hide logo and navigation elements
                logoContainer.style.display = 'none';
                document.querySelector('.left-aligned-nav').style.display = 'none';
                
                // Style the login button container and navbar
                navbarContainer.style.background = 'transparent';
                navbarContainer.style.boxShadow = 'none';
                navbarContainer.style.padding = '0';
                
                // Add the pill style to login button
                loginBtn.classList.add('login-pill');
            }
        } else {
            // Inside home section - restore normal navigation
            if (stickyNav.classList.contains('login-only-mode')) {
                stickyNav.classList.remove('login-only-mode');
                
                // Show logo and navigation elements
                logoContainer.style.display = 'flex';
                document.querySelector('.left-aligned-nav').style.display = 'flex';
                
                // Restore original navbar styling
                navbarContainer.style.background = '';
                navbarContainer.style.boxShadow = '';
                navbarContainer.style.padding = '';
                
                // Remove pill style from login button
                loginBtn.classList.remove('login-pill');
            }
        }
        
        // Determine which section is currently in view for nav highlighting
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            
            // 200px offset for better user experience
            if (scrollPosition >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        // Update active class on navigation links
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').substring(1) === current) {
                link.classList.add('active');
            }
        });
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            // Smooth scroll to target section
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Logo animation on hover
    const logoImg = document.querySelector('.logo-container img');
    if (logoImg) {
        // Add rotation effect on mouseenter
        logoImg.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(5deg)';
        });
        
        // Reset on mouseleave
        logoImg.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0)';
        });
    }
});

// Clean, consolidated DataCore Website JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize AOS once
    AOS.init({
        once: true,
        duration: 800,
        easing: 'ease-in-out'
    });

    // Direct references to DOM elements
    const stickyNav = document.querySelector('.sticky-nav');
    const navbarContainer = document.querySelector('.navbar-container');
    const logoContainer = document.querySelector('.logo-container');
    const leftAlignedNav = document.querySelector('.left-aligned-nav');
    const loginBtn = document.querySelector('.login-btn');
    const loginBtnContainer = document.querySelector('.ms-4');
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Store the original position of the login button
    let loginBtnRect = null;
    let isTransitioning = false;
    let isInLoginPillMode = false;
    let floatingBtn = null;
    
    // Get the initial position of the login button
    function captureLoginButtonPosition() {
        if (!loginBtn) return null;
        
        const rect = loginBtn.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            right: window.innerWidth - rect.right,
            width: rect.width,
            height: rect.height
        };
    }
    
    // Capture initial position after everything is loaded
    window.addEventListener('load', function() {
        loginBtnRect = captureLoginButtonPosition();
        console.log('Initial button position captured:', loginBtnRect);
    });
    
    // Create the floating login button
    function createFloatingButton() {
        if (floatingBtn) return; // Don't create if it already exists
        
        // Get current position
        const btnPos = loginBtnRect || captureLoginButtonPosition();
        if (!btnPos) return;
        
        console.log('Creating floating button with position:', btnPos);
        
        // Create clone of login button
        floatingBtn = loginBtn.cloneNode(true);
        floatingBtn.classList.add('login-pill', 'scrolling-login-btn');
        
        // Position initially at the same spot as the original button
        floatingBtn.style.position = 'fixed';
        floatingBtn.style.transition = 'none'; // Disable transitions initially
        floatingBtn.style.opacity = '0'; // Hide initially
        floatingBtn.style.top = `${btnPos.top - window.scrollY}px`;
        floatingBtn.style.right = `${btnPos.right}px`;
        
        // Add to the DOM
        stickyNav.appendChild(floatingBtn);
        
        // Force reflow to ensure initial position is set
        floatingBtn.offsetHeight;
        
        // Enable transitions and trigger animation
        setTimeout(() => {
            floatingBtn.style.transition = 'all 0.3s ease';
            floatingBtn.style.opacity = '1';
            floatingBtn.style.top = '20px'; // Final top position
            floatingBtn.style.right = '20px'; // Final right position
        }, 50);
    }
    
    // Remove the floating login button
    function removeFloatingButton() {
        if (!floatingBtn) return;
        
        // Animate out
        floatingBtn.style.opacity = '0';
        
        // Remove after transition
        setTimeout(() => {
            if (floatingBtn && floatingBtn.parentNode) {
                floatingBtn.parentNode.removeChild(floatingBtn);
            }
            floatingBtn = null;
        }, 300);
    }
    
    // Function to toggle navigation mode
    function toggleNavigationMode() {
        if (isTransitioning) return; // Prevent multiple transitions at once
        
        const homeSection = document.getElementById('home');
        if (!homeSection) return;
        
        const scrollPosition = window.scrollY;
        const homeSectionBottom = homeSection.offsetTop + homeSection.offsetHeight;
        const shouldShowLoginPill = scrollPosition > (homeSectionBottom / 2);
        
        // Only proceed if there's a state change
        if (shouldShowLoginPill === isInLoginPillMode) return;
        
        isTransitioning = true;
        isInLoginPillMode = shouldShowLoginPill;
        
        if (shouldShowLoginPill) {
            // Switch to login-only mode
            console.log('Switching to login pill mode');
            
            // Fade out navigation elements
            logoContainer.style.opacity = '0';
            navbarContainer.style.opacity = '0';
            
            // After fade out, hide elements and show pill
            setTimeout(() => {
                logoContainer.style.display = 'none';
                navbarContainer.style.display = 'none';
                stickyNav.classList.add('login-only-mode');
                createFloatingButton();
                isTransitioning = false;
            }, 300);
            
        } else {
            // Switch back to full navigation
            console.log('Switching to full navigation mode');
            
            // Start removing pill while preparing to show navbar
            removeFloatingButton();
            
            // Show navigation elements but keep them transparent
            logoContainer.style.display = '';
            navbarContainer.style.display = '';
            logoContainer.style.opacity = '0';
            navbarContainer.style.opacity = '0';
            
            // After a brief delay, fade them in
            setTimeout(() => {
                stickyNav.classList.remove('login-only-mode');
                logoContainer.style.opacity = '1';
                navbarContainer.style.opacity = '1';
                isTransitioning = false;
            }, 50);
        }
    }
    
    // Throttled scroll event handler
    let scrollTimeout = null;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) return;
        
        scrollTimeout = setTimeout(function() {
            // Toggle navigation mode
            toggleNavigationMode();
            
            // Update active navigation link
            updateActiveNavLink();
            
            scrollTimeout = null;
        }, 10);
    });
    
    // Update active navigation link based on scroll position
    function updateActiveNavLink() {
        const scrollPosition = window.scrollY;
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (scrollPosition >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').substring(1) === current) {
                link.classList.add('active');
            }
        });
    }
    
    // Update on window resize
    window.addEventListener('resize', function() {
        loginBtnRect = captureLoginButtonPosition();
    });
    
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Logo animation
    if (logoContainer) {
        const logoImg = logoContainer.querySelector('img');
        if (logoImg) {
            logoImg.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.1) rotate(5deg)';
            });
            
            logoImg.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1) rotate(0)';
            });
        }
    }
    
    // Initialize navigation state on page load
    toggleNavigationMode();
    updateActiveNavLink();
});

document.addEventListener('DOMContentLoaded', function() {
    // Function to adjust vertical centering based on nav height
    function adjustVerticalCenter() {
        const stickyNav = document.querySelector('.sticky-nav');
        const verticalContent = document.querySelector('.vertical-center-content');
        
        if (stickyNav && verticalContent) {
            const navHeight = stickyNav.offsetHeight;
            const topMargin = parseInt(window.getComputedStyle(stickyNav).marginTop);
            
            // Set the content's min-height and margin based on nav dimensions
            verticalContent.style.minHeight = `calc(100vh - ${navHeight + topMargin}px)`;
            verticalContent.style.marginTop = `${navHeight / 2}px`;
        }
    }
    
    // Run on page load
    adjustVerticalCenter();
    
    // Run on window resize
    window.addEventListener('resize', adjustVerticalCenter);
});

document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navbarContainer = document.querySelector('.navbar-container');
    
    if (mobileMenuToggle && navbarContainer) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            navbarContainer.classList.toggle('active');
        });
    }
});

// JavaScript for Mobile Navbar Toggle Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Create mobile menu toggle button
    const navContainer = document.querySelector('.sticky-nav .container .d-flex.align-items-center');
    
    if (navContainer) {
        // Create the toggle button
        const mobileMenuToggle = document.createElement('button');
        mobileMenuToggle.className = 'mobile-menu-toggle';
        mobileMenuToggle.setAttribute('aria-label', 'Toggle navigation menu');
        
        // Add the three bars
        for (let i = 0; i < 3; i++) {
            const bar = document.createElement('span');
            bar.className = 'icon-bar';
            mobileMenuToggle.appendChild(bar);
        }
        
        // Insert the toggle button after the logo container
        const logoContainer = document.querySelector('.logo-container');
        if (logoContainer) {
            logoContainer.parentNode.insertBefore(mobileMenuToggle, logoContainer.nextSibling);
        } else {
            navContainer.prepend(mobileMenuToggle);
        }
        
        // Get the navbar container
        const navbarContainer = document.querySelector('.navbar-container');
        
        // Add click event to toggle
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            navbarContainer.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a navigation link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 991) {
                    mobileMenuToggle.classList.remove('active');
                    navbarContainer.classList.remove('active');
                }
            });
        });
        
        // Close mobile menu when resizing to desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth > 991) {
                mobileMenuToggle.classList.remove('active');
                navbarContainer.classList.remove('active');
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Get the hamburger menu element
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    
    // Function to handle scroll events
    function handleScroll() {
        // Get scroll position
        const scrollPosition = window.scrollY;
        
        // Get the home section element to determine its height
        const homeSection = document.getElementById('home');
        const homeSectionHeight = homeSection.offsetHeight;
        
        // Check if we're scrolled past the home section
        if (scrollPosition > homeSectionHeight - 100) {
            // Hide the hamburger menu
            mobileMenuToggle.style.display = 'none';
        } else {
            // Show the hamburger menu
            mobileMenuToggle.style.display = 'block';
        }
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);
    
    // Call once on page load to set initial state
    handleScroll();
});