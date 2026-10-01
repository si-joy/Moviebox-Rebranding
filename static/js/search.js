document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       ELEMENTS
    ========================================================= */

    const searchInput =
        document.getElementById("searchInput");

    const searchResults =
        document.getElementById("searchResults");

    const mobileSearchToggle =
        document.getElementById("mobileSearchToggle");

    const mobileSearchPanel =
        document.getElementById("mobileSearchPanel");

    const mobileSearchInput =
        document.getElementById("mobileSearchInput");

    const mobileSearchResults =
        document.getElementById("mobileSearchResults");

    const mobileSearchClose =
        document.getElementById("mobileSearchClose");

    const mobileMenuToggle =
        document.getElementById("mobileMenuToggle");

    const mobileMenu =
        document.getElementById("mobileMenu");


    /* =========================================================
       SEARCH TIMERS
    ========================================================= */

    let desktopSearchTimer = null;
    let mobileSearchTimer = null;


    /* =========================================================
       DESKTOP SEARCH
    ========================================================= */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                const query =
                    this.value.trim();

                clearTimeout(
                    desktopSearchTimer
                );


                if (!query) {

                    hideResults(
                        searchResults
                    );

                    return;
                }


                desktopSearchTimer =
                    setTimeout(
                        function () {

                            searchMovies(
                                query,
                                searchResults,
                                false
                            );

                        },
                        300
                    );

            }
        );


        /* Focus */

        searchInput.addEventListener(
            "focus",
            function () {

                const query =
                    this.value.trim();

                if (query) {

                    searchMovies(
                        query,
                        searchResults,
                        false
                    );

                }

            }
        );

    }


    /* =========================================================
       MOBILE SEARCH OPEN / CLOSE
    ========================================================= */

    if (mobileSearchToggle) {

        mobileSearchToggle.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                const isActive =
                    mobileSearchPanel &&
                    mobileSearchPanel.classList.contains(
                        "active"
                    );


                /* Close mobile menu */

                if (mobileMenu) {

                    mobileMenu.classList.remove(
                        "active"
                    );

                }

                if (mobileMenuToggle) {

                    mobileMenuToggle.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }


                /* Toggle search */

                if (mobileSearchPanel) {

                    if (isActive) {

                        closeMobileSearch();

                    } else {

                        mobileSearchPanel.classList.add(
                            "active"
                        );


                        setTimeout(
                            function () {

                                if (mobileSearchInput) {

                                    mobileSearchInput.focus();

                                }

                            },
                            150
                        );

                    }

                }

            }
        );

    }


    /* =========================================================
       MOBILE SEARCH CLOSE BUTTON
    ========================================================= */

    if (mobileSearchClose) {

        mobileSearchClose.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                closeMobileSearch();

            }
        );

    }


    /* =========================================================
       MOBILE SEARCH INPUT
    ========================================================= */

    if (mobileSearchInput) {

        mobileSearchInput.addEventListener(
            "input",
            function () {

                const query =
                    this.value.trim();

                clearTimeout(
                    mobileSearchTimer
                );


                if (!query) {

                    hideResults(
                        mobileSearchResults
                    );

                    return;
                }


                mobileSearchTimer =
                    setTimeout(
                        function () {

                            searchMovies(
                                query,
                                mobileSearchResults,
                                true
                            );

                        },
                        300
                    );

            }
        );

    }


    /* =========================================================
       MOBILE MENU
    ========================================================= */

    if (mobileMenuToggle) {

        mobileMenuToggle.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                const isActive =
                    mobileMenu &&
                    mobileMenu.classList.contains(
                        "active"
                    );


                /* Close search */

                closeMobileSearch();


                /* Toggle menu */

                if (mobileMenu) {

                    if (isActive) {

                        mobileMenu.classList.remove(
                            "active"
                        );

                        mobileMenuToggle.setAttribute(
                            "aria-expanded",
                            "false"
                        );

                    } else {

                        mobileMenu.classList.add(
                            "active"
                        );

                        mobileMenuToggle.setAttribute(
                            "aria-expanded",
                            "true"
                        );

                    }

                }

            }
        );

    }


    /* =========================================================
       SEARCH FUNCTION
    ========================================================= */

    async function searchMovies(
        query,
        resultContainer,
        isMobile
    ) {

        if (!resultContainer) {
            return;
        }


        /*
        Show loading
        */

        resultContainer.style.display =
            "block";


        resultContainer.innerHTML = `
            <div class="search-message">
                Searching...
            </div>
        `;


        try {

            /*
            IMPORTANT:
            This uses your Flask search API.
            */

            const response =
                await fetch(
                    `/api/search?q=${encodeURIComponent(query)}`
                );


            if (!response.ok) {

                throw new Error(
                    "Search request failed"
                );

            }


            const data =
                await response.json();


            /*
            TMDB search response normally contains:
            {
                results: [...]
            }
            */

            const results =
                Array.isArray(data)
                    ? data
                    : (
                        Array.isArray(data.results)
                            ? data.results
                            : []
                    );


            /*
            No results
            */

            if (!results.length) {

                resultContainer.innerHTML = `
                    <div class="search-message">
                        No results found
                    </div>
                `;

                return;
            }


            /*
            Render results
            */

            resultContainer.innerHTML =
                results
                    .slice(0, 10)
                    .map(
                        function (item) {

                            return createSearchResult(
                                item
                            );

                        }
                    )
                    .join("");


        }
        catch (error) {

            console.error(
                "Search error:",
                error
            );


            resultContainer.innerHTML = `
                <div class="search-message">
                    Search failed. Please try again.
                </div>
            `;

        }

    }


    /* =========================================================
       CREATE SEARCH RESULT
    ========================================================= */

    function createSearchResult(item) {

        /*
        Movie:
        item.title

        TV:
        item.name
        */

        const title =
            item.title ||
            item.name ||
            "Unknown";


        /*
        Release date
        */

        const date =
            item.release_date ||
            item.first_air_date ||
            "";


        const year =
            date
                ? date.substring(0, 4)
                : "";


        /*
        Media type
        */

        let mediaType =
            item.media_type;


        /*
        Some backend responses may not include
        media_type.
        */

        if (!mediaType) {

            if (item.first_air_date) {

                mediaType = "tv";

            } else {

                mediaType = "movie";

            }

        }


        const typeText =
            mediaType === "tv"
                ? "TV Series"
                : "Movie";


        /*
        Poster
        */

        const poster =
            item.poster_path
                ? `https://image.tmdb.org/t/p/w185${item.poster_path}`
                : null;


        /*
        Link
        */

        let link = "#";


        if (mediaType === "tv") {

            link =
                `/tv/${item.id}`;

        } else {

            link =
                `/movie/${item.id}`;

        }


        /*
        Rating
        */

        const rating =
            item.vote_average
                ? ` • ★ ${Number(item.vote_average).toFixed(1)}`
                : "";


        /*
        Poster HTML
        */

        const posterHTML =
            poster
                ? `
                    <img
                        src="${poster}"
                        alt="${escapeHTML(title)}"
                        loading="lazy"
                    >
                `
                : `
                    <div class="search-no-poster">
                        No Image
                    </div>
                `;


        return `
            <a
                href="${link}"
                class="search-result"
            >

                ${posterHTML}

                <div class="search-result-info">

                    <div class="search-result-title">
                        ${escapeHTML(title)}
                    </div>

                    <div class="search-result-meta">

                        ${typeText}

                        ${
                            year
                                ? ` • ${year}`
                                : ""
                        }

                        ${rating}

                    </div>

                </div>

            </a>
        `;

    }


    /* =========================================================
       CLOSE MOBILE SEARCH
    ========================================================= */

    function closeMobileSearch() {

        if (mobileSearchPanel) {

            mobileSearchPanel.classList.remove(
                "active"
            );

        }


        if (mobileSearchInput) {

            mobileSearchInput.value = "";

        }


        if (mobileSearchResults) {

            mobileSearchResults.innerHTML = "";

            mobileSearchResults.style.display =
                "none";

        }

    }


    /* =========================================================
       HIDE RESULTS
    ========================================================= */

    function hideResults(container) {

        if (!container) {
            return;
        }


        container.innerHTML = "";

        container.style.display =
            "none";

    }


    /* =========================================================
       ESCAPE HTML
    ========================================================= */

    function escapeHTML(value) {

        return String(value)
            .replace(
                /&/g,
                "&amp;"
            )
            .replace(
                /</g,
                "&lt;"
            )
            .replace(
                />/g,
                "&gt;"
            )
            .replace(
                /"/g,
                "&quot;"
            )
            .replace(
                /'/g,
                "&#039;"
            );

    }


    /* =========================================================
       CLICK OUTSIDE
    ========================================================= */

    document.addEventListener(
        "click",
        function (event) {

            /*
            Desktop search
            */

            if (
                searchResults &&
                searchInput &&
                !event.target.closest(
                    ".desktop-search"
                )
            ) {

                hideResults(
                    searchResults
                );

            }


            /*
            Mobile search
            */

            if (
                mobileSearchPanel &&
                !event.target.closest(
                    ".mobile-search-panel"
                ) &&
                !event.target.closest(
                    "#mobileSearchToggle"
                )
            ) {

                closeMobileSearch();

            }


            /*
            Mobile menu
            */

            if (
                mobileMenu &&
                mobileMenuToggle &&
                !event.target.closest(
                    "#mobileMenu"
                ) &&
                !event.target.closest(
                    "#mobileMenuToggle"
                )
            ) {

                mobileMenu.classList.remove(
                    "active"
                );

                mobileMenuToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }

        }
    );


    /* =========================================================
       ESC KEY
    ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key !== "Escape") {
                return;
            }


            /*
            Close mobile search
            */

            closeMobileSearch();


            /*
            Close mobile menu
            */

            if (mobileMenu) {

                mobileMenu.classList.remove(
                    "active"
                );

            }


            if (mobileMenuToggle) {

                mobileMenuToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }


            /*
            Close desktop results
            */

            hideResults(
                searchResults
            );

        }
    );

});