document.addEventListener("DOMContentLoaded", () => {

    const filterForm =
        document.querySelector(".midnight-filter-bar");

    const filterButton =
        document.querySelector(".filter-button");

    const cards =
        document.querySelectorAll(".midnight-card");


    // ==========================================
    // FILTER FORM
    // ==========================================

    if (filterForm) {

        filterForm.addEventListener("submit", () => {

            if (filterButton) {

                filterButton.disabled = true;

                filterButton.textContent = "Loading...";

            }

        });

    }


    // ==========================================
    // IMAGE FALLBACK
    // ==========================================

    const images =
        document.querySelectorAll(".midnight-poster img");

    images.forEach((image) => {

        image.addEventListener("error", () => {

            image.style.display = "none";

            const parent =
                image.closest(".midnight-poster");

            if (!parent) {
                return;
            }

            const placeholder =
                document.createElement("div");

            placeholder.className =
                "poster-placeholder";

            placeholder.textContent =
                "No Poster";

            parent.insertBefore(
                placeholder,
                image
            );

        });

    });


    // ==========================================
    // CARD KEYBOARD ACCESS
    // ==========================================

    cards.forEach((card) => {

        const link =
            card.querySelector(".midnight-card-link");

        if (!link) {
            return;
        }

        link.addEventListener("keydown", (event) => {

            if (event.key === "Enter") {

                link.click();

            }

        });

    });


    // ==========================================
    // SCROLL POSITION
    // ==========================================

    /*
     * When navigating pagination, keep the user
     * near the catalog instead of the very top.
     */

    const pagination =
        document.querySelector(".midnight-pagination");

    if (pagination) {

        const currentPage =
            pagination.querySelector(".page-number.active");

        if (currentPage) {

            currentPage.setAttribute(
                "aria-current",
                "page"
            );

        }

    }


    // ==========================================
    // ESCAPE KEY
    // ==========================================

    document.addEventListener("keydown", (event) => {

        if (event.key !== "Escape") {
            return;
        }

        const activeElement =
            document.activeElement;

        if (
            activeElement &&
            activeElement.tagName === "SELECT"
        ) {

            activeElement.blur();

        }

    });

});