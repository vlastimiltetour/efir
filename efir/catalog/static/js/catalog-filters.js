
document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById("filter-panel");
    const openButton = document.getElementById("open-filters");
    const closeButton = document.getElementById("close-filters");

  
    const resetButton = document.getElementById("reset-filters");
    const productGridContainer = document.getElementById("product-grid-container");


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

    async function filterProducts() {
          //const category = document.getElementById("category");
        const sortBy = document.getElementById("sortBy");

        const categoryOptions = [
            ...document.querySelectorAll(".category-options")
        ]
            
        const cutOptions = [
            ...document.querySelectorAll(".cut-options") // 1. nabrat hodnoty z forms.py
        ]
        const sizeOptions = [
            ...document.querySelectorAll(".size-options")
        ]

        const params = new URLSearchParams();

        if (sortBy && sortBy.value) {
            params.append("sort", sortBy.value);
        }

        // Pro každý zaškrtnutý prvek přidáme hodnotu
        categoryOptions.filter(input => input.checked).forEach(input => params.append("category", input.value));
        cutOptions.filter(input => input.checked).forEach(input => params.append("cut", input.value));
        sizeOptions.filter(input => input.checked).forEach(input => params.append("size", input.value));
        

        // Sestavíme novou URL (např. /katalog/?category=Sety&cut=Brazilky)
        const newUrl = `${window.location.pathname}?${params.toString()}`;

        try {
                const response = await fetch(newUrl, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });

                if (!response.ok) throw new Error("Server vrátil chybu.");

                const htmlText = await response.text();

                // Převedeme text na DOM, abychom z něj mohli vytáhnout jen mřížku produktů
                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlText, "text/html");
                
                // Najdeme mřížku uvnitř té stáhnuté stránky
                const newGrid = doc.getElementById("product-grid-container");


                const newSizeGroup = doc.getElementById("size-group");
                const newCutGroup = doc.getElementById("cut-group");
                const newCategoryGroup = doc.getElementById("category-group");

                if (newGrid && productGridContainer) {
                    // Vyměníme obsah
                    productGridContainer.innerHTML = newGrid.innerHTML;
                }

                if (newSizeGroup) {
                    document.getElementById("size-group").innerHTML = newSizeGroup.innerHTML;
                }

                if (newCutGroup) {
                    document.getElementById("cut-group").innerHTML = newCutGroup.innerHTML;
                }

                if (newCategoryGroup) {
                    document.getElementById("category-group").innerHTML = newCategoryGroup.innerHTML;
                }

                window.history.pushState({}, "", newUrl);

        } catch (error) {
            console.error("Chyba při filtrování produktů:", error);
        }
    }

    // Příklad správného navázání – každý prvek musí volat filterProducts()
    document.addEventListener("change", (event) => {
        if (event.target.matches("#filter-panel select, #filter-panel input")) {
            filterProducts();
        }
    });

  
   
    document.addEventListener("click", (event) => {
    if (event.target.closest("#reset-filters")) {
        event.preventDefault();

        const sortBy = document.getElementById("sortBy");

        if (sortBy) sortBy.value = "default";

        document.querySelectorAll(".cut-options, .size-options, .category-options").forEach(input => {
            input.checked = false;
        });

        filterProducts();
    }
});
  filterProducts();

});