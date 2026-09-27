document.addEventListener("DOMContentLoaded", function () {

    const slider = document.querySelector(".hero-slider");
    const track = document.getElementById("heroTrack");
    const slides = document.querySelectorAll(".hero-slide");

    const prevButton = document.getElementById("heroPrev");
    const nextButton = document.getElementById("heroNext");

    const dots = document.querySelectorAll(".hero-dot");

    if (!slider || !track || slides.length === 0) {
        return;
    }


    let currentSlide = 0;

    let autoPlayTimer;

    let touchStartX = 0;
    let touchEndX = 0;


    function updateSlider() {

        track.style.transform =
            `translateX(-${currentSlide * 100}%)`;


        dots.forEach((dot, index) => {

            dot.classList.toggle(
                "active",
                index === currentSlide
            );

        });

    }


    function nextSlide() {

        currentSlide++;

        if (currentSlide >= slides.length) {
            currentSlide = 0;
        }

        updateSlider();

    }


    function previousSlide() {

        currentSlide--;

        if (currentSlide < 0) {
            currentSlide = slides.length - 1;
        }

        updateSlider();

    }


    function goToSlide(index) {

        currentSlide = index;

        updateSlider();

    }


    function startAutoPlay() {

        clearInterval(autoPlayTimer);

        autoPlayTimer = setInterval(
            nextSlide,
            5000
        );

    }


    function stopAutoPlay() {

        clearInterval(autoPlayTimer);

    }


    /* Previous */

    prevButton.addEventListener(
        "click",
        function () {

            previousSlide();

            startAutoPlay();

        }
    );


    /* Next */

    nextButton.addEventListener(
        "click",
        function () {

            nextSlide();

            startAutoPlay();

        }
    );


    /* Dots */

    dots.forEach((dot, index) => {

        dot.addEventListener(
            "click",
            function () {

                goToSlide(index);

                startAutoPlay();

            }
        );

    });


    /* =========================
       TOUCH SWIPE
    ========================= */

    slider.addEventListener(
        "touchstart",
        function (event) {

            touchStartX =
                event.changedTouches[0].screenX;

            stopAutoPlay();

        },
        { passive: true }
    );


    slider.addEventListener(
        "touchend",
        function (event) {

            touchEndX =
                event.changedTouches[0].screenX;

            const swipeDistance =
                touchStartX - touchEndX;


            if (Math.abs(swipeDistance) > 50) {

                if (swipeDistance > 0) {

                    nextSlide();

                } else {

                    previousSlide();

                }

            }

            startAutoPlay();

        },
        { passive: true }
    );


    /* =========================
       MOUSE HOVER
    ========================= */

    slider.addEventListener(
        "mouseenter",
        stopAutoPlay
    );


    slider.addEventListener(
        "mouseleave",
        startAutoPlay
    );


    /* Start */

    updateSlider();

    startAutoPlay();

});