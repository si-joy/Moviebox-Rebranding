const searchInput =
    document.getElementById("searchInput");

const searchResults =
    document.getElementById("searchResults");

let searchTimer;


if (searchInput) {

    searchInput.addEventListener(
        "input",
        function () {

            const query =
                this.value.trim();

            clearTimeout(searchTimer);


            if (!query) {

                searchResults.style.display =
                    "none";

                searchResults.innerHTML =
                    "";

                return;

            }


            searchTimer = setTimeout(
                () => performSearch(query),
                300
            );

        }
    );


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


function displayResults(results) {

    searchResults.innerHTML = "";


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


    results.forEach(item => {

        const result =
            document.createElement("a");


        result.href =
            item.media_type === "movie"
                ? `/movie/${item.id}`
                : `/tv/${item.id}`;


        result.className =
            "search-result";


        const poster =
            item.poster_path
                ? `https://image.tmdb.org/t/p/w185${item.poster_path}`
                : null;


        const year =
            item.release_date
                ? item.release_date.substring(0, 4)
                : "N/A";


        const type =
            item.media_type === "movie"
                ? "Movie"
                : "TV Series";


        result.innerHTML = `

            ${
                poster
                    ? `
                        <img
                            src="${poster}"
                            alt=""
                            loading="lazy"
                        >
                    `
                    : `
                        <div
                            class="search-no-poster"
                        ></div>
                    `
            }


            <div class="search-result-info">

                <h3 class="search-result-title">
                    ${escapeHtml(item.title)}
                </h3>

                <p class="search-result-meta">
                    ${type} • ${year}
                </p>

            </div>

        `;


        searchResults.appendChild(
            result
        );

    });

}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value || "";

    return div.innerHTML;

}


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