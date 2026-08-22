let allProducts = [];
let priceHistory = {};

const DROPS_API_URL = "http://127.0.0.1:5000/api/price-drops";
const API_URL = "http://127.0.0.1:5000/api/products";
const HISTORY_API_URL = "http://127.0.0.1:5000/api/price-history";


async function loadProducts() {

    const container = document.getElementById("products");
    const status = document.getElementById("scraperStatus");
    const health = document.getElementById("healthStatus");

    try {

        container.innerHTML = `
            <div class="loading">
                Loading products...
            </div>
        `;

        status.textContent = "Loading...";
        health.textContent = "Working";

        const [
    productsResponse,
    historyResponse,
    dropsResponse
] = await Promise.all([
    fetch(API_URL),
    fetch(HISTORY_API_URL),
    fetch(DROPS_API_URL)
]);

        if (!productsResponse.ok) {
            throw new Error(
                "Products API failed: " +
                productsResponse.status
            );
        }

        if (!historyResponse.ok) {
            throw new Error(
                "History API failed: " +
                historyResponse.status
            );
        }

        const productsData =
            await productsResponse.json();

        priceHistory =
            await historyResponse.json();

        const dropsData =
        await dropsResponse.json();

        updateDropStats(dropsData.count);

        allProducts =
            productsData.products || [];

        updateStats(allProducts);
        renderProducts(allProducts);

        status.textContent = "Scraper Live";
        health.textContent = "Healthy";

    } catch (error) {

        console.error(
            "Error loading products:",
            error
        );

        status.textContent = "Offline";
        health.textContent = "Failed";

        container.innerHTML = `
            <div class="loading">
                ❌ Unable to load products.
                <br>
                Make sure the Flask backend is running.
            </div>
        `;
    }
}


/* =========================
   RENDER PRODUCTS
========================= */

function renderProducts(products) {

    const container =
        document.getElementById("products");

    container.innerHTML = "";

    if (products.length === 0) {

        container.innerHTML = `
            <div class="loading">
                No products found.
            </div>
        `;

        return;
    }

    products.forEach(product => {

        const card =
            document.createElement("div");

        card.className = "product-card";

        const history =
            priceHistory[product.name] || [];

            let chartHTML = "";

if (history.length > 0) {

    const prices = history.map(item =>
        parseFloat(
            item.price.replace(/[^\d.]/g, "")
        )
    );

    const maxPrice = Math.max(...prices);

    chartHTML = `
        <div class="mini-chart">
            <strong>📊 Price Trend</strong>

            <div class="chart-bars">
                ${prices.map(price => {

                    const height =
                        Math.max(
                            20,
                            (price / maxPrice) * 100
                        );

                    return `
                        <div
                            class="chart-bar"
                            style="height: ${height}%"
                            title="£${price.toFixed(2)}"
                        ></div>
                    `;

                }).join("")}
            </div>
        </div>
    `;
} 

        let historyHTML = `
            <div class="price-history">
                📈 No price history yet
            </div>
        `;

        if (history.length > 0) {

            const latest =
                history[history.length - 1];

            const previous =
                history.length > 1
                    ? history[history.length - 2]
                    : null;

            let changeHTML = "";

            if (previous) {

                const currentPrice =
                    parseFloat(
                        latest.price.replace(/[^\d.]/g, "")
                    );

                const previousPrice =
                    parseFloat(
                        previous.price.replace(/[^\d.]/g, "")
                    );

                if (currentPrice < previousPrice) {

                    const saved =
    (previousPrice - currentPrice).toFixed(2);

changeHTML = `
    <div class="price-drop">
        📉 Price dropped!
        <strong>You save £${saved}</strong>
    </div>
`; 

                } else if (currentPrice > previousPrice) {

                    changeHTML = `
                        <span class="price-rise">
                            📈 Price increased
                        </span>
                    `;

                } else {

                    changeHTML = `
                        <span class="price-same">
                            → Price unchanged
                        </span>
                    `;
                }
            }

            const date =
                new Date(
                    latest.timestamp
                );

            historyHTML = `
                <div class="price-history">

                    <strong>📈 Price History</strong>

                    <div class="history-price">
                        ${latest.price}
                    </div>

                    <div class="history-time">
                        Updated:
                        ${date.toLocaleString()}
                    </div>

                    ${changeHTML}

                </div>
            `;
        }

        card.innerHTML = `

            <h3>${product.name}</h3>

            <p class="product-price">
                ${product.price}
            </p>

            <p>
                ${product.availability}
            </p>

            <p class="product-rating">
                ⭐ ${product.rating}
            </p>

            ${historyHTML}
            ${chartHTML} 

            <a
                class="product-link"
                href="${product.url}"
                target="_blank"
            >
                View Product →
            </a>

        `;

        container.appendChild(card);
    });
}


/* =========================
   STATS
========================= */

function updateStats(products) {

    const countElement =
        document.getElementById("productCount");

    const lowestPriceElement =
        document.getElementById("lowestPrice");

    if (countElement) {
        countElement.textContent =
            products.length;
    }

    if (products.length === 0) {

        if (lowestPriceElement) {
            lowestPriceElement.textContent = "—";
        }

        return;
    }

    const prices =
        products
            .map(product =>
                parseFloat(
                    product.price.replace(/[^\d.]/g, "")
                )
            )
            .filter(price => !isNaN(price));

    if (
        prices.length > 0 &&
        lowestPriceElement
    ) {

        const lowest =
            Math.min(...prices);

        lowestPriceElement.textContent =
            "£" + lowest.toFixed(2);
    }
}
function updateDropStats(count) {
    const dropElement =
        document.getElementById("priceDrops");

    if (dropElement) {
        dropElement.textContent = count;
    }
} 

/* =========================
   SEARCH
========================= */

function searchProducts() {

    const searchInput =
        document.getElementById("searchInput");

    const query =
        searchInput.value
            .toLowerCase()
            .trim();

    const filteredProducts =
        allProducts.filter(product =>
            product.name
                .toLowerCase()
                .includes(query)
        );

    renderProducts(filteredProducts);
    updateStats(filteredProducts);
}


/* =========================
   SORT
========================= */

function sortProducts() {

    const sortValue =
        document.getElementById("sortSelect").value;

    let sortedProducts =
        [...allProducts];

    if (sortValue === "low") {

        sortedProducts.sort((a, b) => {

            const priceA =
                parseFloat(
                    a.price.replace(/[^\d.]/g, "")
                );

            const priceB =
                parseFloat(
                    b.price.replace(/[^\d.]/g, "")
                );

            return priceA - priceB;
        });
    }

    if (sortValue === "high") {

        sortedProducts.sort((a, b) => {

            const priceA =
                parseFloat(
                    a.price.replace(/[^\d.]/g, "")
                );

            const priceB =
                parseFloat(
                    b.price.replace(/[^\d.]/g, "")
                );

            return priceB - priceA;
        });
    }

    if (sortValue === "rating") {

        const ratingValues = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        };

        sortedProducts.sort((a, b) =>
            ratingValues[b.rating] -
            ratingValues[a.rating]
        );
    }

    renderProducts(sortedProducts);
    updateStats(sortedProducts);
}


/* =========================
   EVENT LISTENERS
========================= */

const searchInput =
    document.getElementById("searchInput");

if (searchInput) {

    searchInput.addEventListener(
        "input",
        searchProducts
    );
}


const sortSelect =
    document.getElementById("sortSelect");

if (sortSelect) {

    sortSelect.addEventListener(
        "change",
        sortProducts
    );
}


const refreshBtn =
    document.getElementById("refreshBtn");

if (refreshBtn) {

    refreshBtn.addEventListener(
        "click",
        loadProducts
    );
}


/* =========================
   INITIAL LOAD
========================= */

loadProducts(); 