document.addEventListener("DOMContentLoaded", () => {

    const trailerModal = document.getElementById("trailerModal");
    const trailerFrame = document.getElementById("trailerFrame");

    const openTrailer = document.getElementById("openTrailer");
    const closeTrailer = document.getElementById("closeTrailer");
    const closeTrailerBackdrop = document.getElementById(
        "closeTrailerBackdrop"
    );


    // =====================================================
    // TRAILER
    // =====================================================

    if (
        trailerModal &&
        trailerFrame &&
        openTrailer
    ) {

        const videoKey =
            openTrailer.dataset.videoKey;


        function openTrailerModal() {

            if (!videoKey) return;

            trailerFrame.src =
                `https://www.youtube.com/embed/${videoKey}?autoplay=1&rel=0`;

            trailerModal.classList.add("active");

            trailerModal.setAttribute(
                "aria-hidden",
                "false"
            );

            document.body.style.overflow = "hidden";
        }


        function closeTrailerModal() {

            trailerModal.classList.remove("active");

            trailerModal.setAttribute(
                "aria-hidden",
                "true"
            );

            trailerFrame.src = "";

            document.body.style.overflow = "";
        }


        openTrailer.addEventListener(
            "click",
            openTrailerModal
        );


        if (closeTrailer) {

            closeTrailer.addEventListener(
                "click",
                closeTrailerModal
            );

        }


        if (closeTrailerBackdrop) {

            closeTrailerBackdrop.addEventListener(
                "click",
                closeTrailerModal
            );

        }


        document.addEventListener(
            "keydown",
            (event) => {

                if (
                    event.key === "Escape" &&
                    trailerModal.classList.contains("active")
                ) {

                    closeTrailerModal();

                }

            }
        );

    }


    // =====================================================
    // IMAGE FALLBACK
    // =====================================================

    const images =
        document.querySelectorAll(
            ".movie-detail-page img"
        );


    images.forEach((image) => {

        image.addEventListener(
            "error",
            () => {

                image.style.display = "none";

            }
        );

    });

});