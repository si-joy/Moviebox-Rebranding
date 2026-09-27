const searchInput =
    document.getElementById("searchInput");

const searchResults =
    document.getElementById("searchResults");


let searchTimer;


/* =========================================================
   SEARCH INPUT
========================================================= */

if (searchInput) {

    searchInput.addEventListener(
        "input",
        function () {

            const query =
                this.value.trim();


            clearTimeout(searchTimer);


            // Empty search

            if (!query) {

                searchResults.style.display =
                    "none";

                searchResults.innerHTML =
                    "";

                return;

            }


            // Wait 300ms before searching

            searchTimer = setTimeout(
                () => {

                    performSearch(query);

                },
                300
            );

        }
    );


    /* =====================================================
       SHOW RESULTS WHEN INPUT IS FOCUSED
    ===================================================== */

    searchInput.addEventListener(
        "focus",
        function () {

            if (
                this.value.trim() &&
                searchResults.innerHTML
            ) {

                searchResults.style.display =
                    "block";

            }

        }
    );

}


/* =========================================================
   SEARCH API
========================================================= */

async function performSearch(query) {

    searchResults.style.display =
        "block";


    searchResults.innerHTML = `

        <div class="search-message">

            Searching...

        </div>

    `;


    try {

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


        displayResults(
            data.results
        );


    } catch (error) {

        console.error(
            "Search error:",
            error
        );


        searchResults.innerHTML = `

            <div class="search-message">

                Something went wrong.

            </div>

        `;

    }

}


/* =========================================================
   DISPLAY RESULTS
========================================================= */

function displayResults(results) {

    searchResults.innerHTML =
        "";


    if (
        !results ||
        results.length === 0
    ) {

        searchResults.innerHTML = `

            <div class="search-message">

                No results found.

            </div>

        `;

        return;

    }


    results.forEach(
        item => {


            const result =
                document.createElement("a");


            /* -----------------------------------------
               DESTINATION
            ----------------------------------------- */

            if (
                item.media_type === "movie"
            ) {

                result.href =
                    `/movie/${item.id}`;

            } else {

                result.href =
                    `/tv/${item.id}`;

            }


            result.className =
                "search-result";


            /* -----------------------------------------
               POSTER
            ----------------------------------------- */

            const poster =
                item.poster_path
                    ? `https://image.tmdb.org/t/p/w185${item.poster_path}`
                    : null;


            /* -----------------------------------------
               YEAR
            ----------------------------------------- */

            const year =
                item.release_date
                    ? item.release_date.substring(0, 4)
                    : "N/A";


            /* -----------------------------------------
               TYPE
            ----------------------------------------- */

            const type =
                item.media_type === "movie"
                    ? "Movie"
                    : "TV Series";


            /* -----------------------------------------
               HTML
            ----------------------------------------- */

            result.innerHTML = `

                ${
                    poster

                    ? `
                        <img
                            src="${poster}"
                            alt="${item.title}"
                        >
                    `

                    : `
                        <div class="search-no-poster">
                        </div>
                    `
                }


                <div class="search-result-info">

                    <h3 class="search-result-title">

                        ${item.title}

                    </h3>


                    <p class="search-result-meta">

                        ${type} • ${year}

                    </p>

                </div>

            `;


            searchResults.appendChild(
                result
            );

        }
    );

}


/* =========================================================
   CLOSE SEARCH WHEN CLICKING OUTSIDE
========================================================= */

document.addEventListener(
    "click",
    function (event) {

        if (
            !event.target.closest(
                ".search-wrapper"
            )
        ) {

            if (searchResults) {

                searchResults.style.display =
                    "none";

            }

        }

    }
);