document.addEventListener("DOMContentLoaded", () => {

    const heroTrack = document.getElementById("heroTrack");
    const heroSlides = document.querySelectorAll(".hero-slide");

    const heroPrev = document.getElementById("heroPrev");
    const heroNext = document.getElementById("heroNext");

    const heroCurrent = document.getElementById("heroCurrent");
    const heroProgress = document.getElementById("heroProgress");

    const heroSlider = document.getElementById("heroSlider");

    if (!heroTrack || heroSlides.length === 0) {
        return;
    }

    let currentSlide = 0;

    const totalSlides = heroSlides.length;
    const slideDuration = 6000;

    let autoplayTimer = null;
    let progressTimer = null;

    let progressStartTime = null;
    let progressElapsed = 0;

    let isPaused = false;


    // ==========================================
    // UPDATE SLIDER
    // ==========================================

    function updateSlider() {

        heroTrack.style.transform =
            `translateX(-${currentSlide * 100}%)`;

        heroSlides.forEach((slide, index) => {

            slide.classList.toggle(
                "active",
                index === currentSlide
            );

        });


        // Update number

        if (heroCurrent) {

            heroCurrent.textContent =
                String(currentSlide + 1).padStart(2, "0");

        }


        // Reset progress

        resetProgress();

    }


    // ==========================================
    // NEXT SLIDE
    // ==========================================

    function nextSlide() {

        currentSlide++;

        if (currentSlide >= totalSlides) {
            currentSlide = 0;
        }

        updateSlider();

        if (!isPaused) {
            startAutoplay();
        }

    }


    // ==========================================
    // PREVIOUS SLIDE
    // ==========================================

    function previousSlide() {

        currentSlide--;

        if (currentSlide < 0) {
            currentSlide = totalSlides - 1;
        }

        updateSlider();

        if (!isPaused) {
            startAutoplay();
        }

    }


    // ==========================================
    // AUTOPLAY
    // ==========================================

    function startAutoplay() {

        clearTimeout(autoplayTimer);

        if (isPaused) {
            return;
        }

        autoplayTimer = setTimeout(() => {

            nextSlide();

        }, slideDuration - progressElapsed);

    }


    function stopAutoplay() {

        clearTimeout(autoplayTimer);

        autoplayTimer = null;

    }


    // ==========================================
    // PROGRESS BAR
    // ==========================================

    function startProgress() {

        if (!heroProgress) {
            return;
        }

        clearInterval(progressTimer);

        progressStartTime =
            Date.now() - progressElapsed;

        progressTimer = setInterval(() => {

            if (isPaused) {
                return;
            }

            const elapsed =
                Date.now() - progressStartTime;

            progressElapsed =
                Math.min(elapsed, slideDuration);

            const percentage =
                (progressElapsed / slideDuration) * 100;

            heroProgress.style.width =
                `${percentage}%`;


            if (progressElapsed >= slideDuration) {

                clearInterval(progressTimer);

            }

        }, 50);

    }


    function stopProgress() {

        clearInterval(progressTimer);

        progressTimer = null;

    }


    function resetProgress() {

        stopProgress();

        progressElapsed = 0;

        if (heroProgress) {
            heroProgress.style.width = "0%";
        }

        if (!isPaused) {
            startProgress();
        }

    }


    // ==========================================
    // MOUSE ENTER
    // ==========================================

    if (heroSlider) {

        heroSlider.addEventListener(
            "mouseenter",
            () => {

                isPaused = true;

                stopAutoplay();
                stopProgress();

            }
        );


        // ==========================================
        // MOUSE LEAVE
        // ==========================================

        heroSlider.addEventListener(
            "mouseleave",
            () => {

                isPaused = false;

                // Continue progress from where it stopped

                startProgress();

                // Continue autoplay from where it stopped

                startAutoplay();

            }
        );

    }


    // ==========================================
    // BUTTONS
    // ==========================================

    if (heroNext) {

        heroNext.addEventListener(
            "click",
            () => {

                nextSlide();

            }
        );

    }


    if (heroPrev) {

        heroPrev.addEventListener(
            "click",
            () => {

                previousSlide();

            }
        );

    }


    // ==========================================
    // KEYBOARD
    // ==========================================

    document.addEventListener(
        "keydown",
        (event) => {

            if (event.key === "ArrowRight") {

                nextSlide();

            }

            if (event.key === "ArrowLeft") {

                previousSlide();

            }

        }
    );


    // ==========================================
    // INITIALIZE
    // ==========================================

    updateSlider();

    startAutoplay();

});