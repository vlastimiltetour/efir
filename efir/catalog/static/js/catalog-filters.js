
document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById("filter-panel");
    const openButton = document.getElementById("open-filters");
    const closeButton = document.getElementById("close-filters");

    const category = document.getElementById("category");
    const sortBy = document.getElementById("sortBy");

    const cutOptions = [
        ...document.querySelectorAll(".cut-options") // 1. nabrat hodnoty z forms.py
    ]
    const sizeOptions = [
        ...document.querySelectorAll(".size-options")
    ]

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
        const params = new URLSearchParams();

        if (category && category.value) {
            // Převede první písmeno na velké, zbytek nechá netknutý
            const formattedCategory = category.value.charAt(0).toUpperCase() + category.value.slice(1);
            params.append("category", formattedCategory);
        }
        if (sortBy && sortBy.value) {
            params.append("sort", sortBy.value);
        }

        // Pro každý zaškrtnutý prvek přidáme hodnotu
        cutOptions.filter(input => input.checked).forEach(input => params.append("cut", input.value));
        sizeOptions.filter(input => input.checked).forEach(input => params.append("size", input.value));
        

        // Sestavíme novou URL (např. /katalog/?category=Sety&cut=Brazilky)
        const newUrl = `${window.location.pathname}?${params.toString()}`;

        console.log('new url', newUrl)

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

                if (newGrid && productGridContainer) {
                    // Vyměníme obsah
                    productGridContainer.innerHTML = newGrid.innerHTML;
                }

                window.history.pushState({}, "", newUrl);

        } catch (error) {
            console.error("Chyba při filtrování produktů:", error);
        }
    }

    // Příklad správného navázání – každý prvek musí volat filterProducts()
    if (sortBy) {
        sortBy.addEventListener("change", () => {
            
            filterProducts(); // TADY SE TO SPUSTÍ
        });
    }

    if (category) {
        category.addEventListener("change", () => {
            filterProducts();
        });
    }

    cutOptions.forEach(input => {
        input.addEventListener("change", () => {
            console.log("Mění se strih...");
            filterProducts();
        });
    });

    sizeOptions.forEach(input => {
        input.addEventListener("change", () => {
            console.log("Mění se velikost...");
            filterProducts();
        });
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