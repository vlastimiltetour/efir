
document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById("filter-panel");
    //const overlay = document.getElementById("overlay");
    const openButton = document.getElementById("open-filters");
    const closeButton = document.getElementById("close-filters");

    const category = document.getElementById("category");
    const sortBy = document.getElementById("sortBy");
    
    const products = [
        ...document.querySelectorAll("#product-card")
    ];

    const originalProducts = [
        ...document.querySelectorAll("product-card")
    ]
    const brandFilters = [
        ...document.querySelectorAll(".brand-filter")
    ];
    const cutOptions = [
        ...document.querySelectorAll(".cut-options") // 1. nabrat hodnoty z forms.py
    ]
    const sizeOptions = [
        ...document.querySelectorAll(".size-options")
    ]

    const resultCount = document.getElementById("result-count");
    const noResults = document.getElementById("no-results");
    const resetButton = document.getElementById("reset-filters");


    function setPanelOpen(open) {
        console.log('panel is open')

        panel.classList.toggle("is-open", open);
        //overlay.classList.toggle("is-open", open);
        
        panel.setAttribute("aria-hidden", String(!open));
        panel.inert = !open;
        openButton.setAttribute("aria-expanded", String(open));

        if (open) {
            closeButton.focus();
        } else {
            openButton.focus();
        }
    }

    openButton.addEventListener("click", () => setPanelOpen(true));
    closeButton.addEventListener("click", () => setPanelOpen(false));
    // overlay.addEventListener("click", () => setPanelOpen(false));

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            panel.classList.contains("is-open")
        ) {
            setPanelOpen(false);
            
        }
    });

    function sortProducts() {

        sortValue = sortBy.value;
        const container = products[0]?.parentElement;

        if (sortValue === "default") {
            // products.length = 0;
            products.push(...originalProducts);
        }
        
        else if (sortValue === "price-dsc" || sortValue === "price-asc") {
            products.sort((a,b) => {
                const txtA = a.querySelector("#product-price, .product-price")?.textContent || "0";
                const txtB = b.querySelector("#product-price, .product-price")?.textContent || "0";

                // 2. Očištění textu na čisté číslo (odstraní "Kč", mezery, atd.)
                const priceA = Number(txtA.replace(/[^0-9,-]/g, '').replace(',', '')) || 0;
                const priceB = Number(txtB.replace(/[^0-9,-]/g, '').replace(',', '')) || 0;
                console.log(priceA, priceB)

                if (sortValue === "price-dsc") { 
                return priceB - priceA} 
                if (sortValue === "price-asc") { 
                return priceA - priceB} 
            });
}
      
        else if (sortValue === "newest" ) {
            
            products.sort((a, b) => {
                const dateTextA = a.querySelector("#product-age")?.textContent.trim() || "";
                const dateTextB = b.querySelector("#product-age")?.textContent.trim() || "";
                console.log(dateTextA)
                // Převod textu data na milisekundy
                const timeA = new Date(dateTextA).getTime() || 0;
                const timeB = new Date(dateTextB).getTime() || 0;
              
                return timeB - timeA
            
                
            })};

        products.forEach(product => container.appendChild(product));
    };


    function filterProducts() {
        
        const selectedCategory = category.value;
    
        const selectedCuts = cutOptions // 2. mapovani ktere hodnoty jsou oznacene
            .filter(input => input.checked)
            .map(input => input.value);

        const selectedSizes = sizeOptions
            .filter(input => input.checked)
            .map(input => input.value);

        const selectedBrands = brandFilters
            .filter((input) => input.checked)
            .map((input) => input.value);

    
        let visibleCount = 0;

        products.forEach((product) => {

            
            const productCategory = product.querySelector("#product-category").textContent.trim().replace(/\u00A0/g, " ").toLocaleLowerCase("cs");
            
            const productCut = product.querySelector("#product-cut").textContent; // oznaceni vsech produktu v katalogu
            const productSize = product.querySelector("#product-size").textContent; 
            
            const productBrand = product.dataset.brand;
            const price = Number(product.querySelector("#product-price"));
            
            const matchesCut =
              selectedCuts.length === 0 ||
              selectedCuts.includes(productCut); // oznaceni shody

        

            const matchesCategory =
                !selectedCategory ||
                productCategory === selectedCategory;

            const matchesSize = 
                selectedSizes.length === 0 ||
                selectedSizes.some(size => productSize.includes(size));

            const matchesBrand =
                selectedBrands.length === 0 ||
                selectedBrands.includes(productBrand);


            console.log('selected siez', selectedSizes, 'rpdocut sizes', productSize)

            const visible =
                matchesCategory &&
                matchesBrand &&
                matchesCut && 
                matchesSize;

            product.hidden = !visible;

            if (visible) visibleCount++;
            
            sortProducts();
        });



        resultCount.textContent =
            `Nalezeno ${visibleCount} produktů`;

        noResults.hidden = visibleCount !== 0;
        
    }

    if (sortBy) {sortBy.addEventListener("change", filterProducts)};
    if (category) {category.addEventListener("change", filterProducts)};
    
    cutOptions.forEach(input => {
    input.addEventListener("change", filterProducts); // listener pro to ktere hodnoty jsou oznacene
});
    sizeOptions.forEach(input => {
        input.addEventListener("change", filterProducts); // listener pro to ktere hodnoty jsou oznacene
    });
   
    resetButton.addEventListener("click", () => {
        category.value = "";
        cutOptions.forEach((input) => {
            input.checked = false;
        })
        sizeOptions.forEach((input) => {
            input.checked = false;
        });
        
        if (sortBy) sortBy.value = "default";


        filterProducts();
    });

    filterProducts();
});