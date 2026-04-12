document.addEventListener("DOMContentLoaded", () => {
    const queryInput = document.getElementById("queryInput");
    const decodeBtn = document.getElementById("decodeBtn");
    const filterChips = document.querySelectorAll(".chip");
    
    const responseContainer = document.getElementById("responseContainer");
    const loadingState = document.getElementById("loadingState");
    const resultCard = document.getElementById("resultCard");
    
    // UI Output elements
    const eli5Output = document.getElementById("eli5Output");
    const originalOutput = document.getElementById("originalOutput");
    const sourceSection = document.getElementById("sourceSection");
    const sourceClause = document.getElementById("sourceClause");
    const sourcePage = document.getElementById("sourcePage");

    // Handle Search Call
    const handleDecode = async (query) => {
        if (!query.trim()) return;

        // Reset UI
        responseContainer.classList.remove("hidden");
        loadingState.classList.remove("hidden");
        resultCard.classList.add("hidden");

        try {
            const response = await fetch("/api/decode", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Something went wrong.");
                responseContainer.classList.add("hidden");
                return;
            }

            // Populate UI
            eli5Output.textContent = data.eli5;
            originalOutput.textContent = `"${data.original_text}"`;
            sourceSection.textContent = data.sources.section;
            sourceClause.textContent = data.sources.clause;
            sourcePage.textContent = `Found on ${data.sources.page}`;

            // Show Result
            loadingState.classList.add("hidden");
            resultCard.classList.remove("hidden");

        } catch (error) {
            console.error(error);
            alert("Failed to connect to the backend server.");
            responseContainer.classList.add("hidden");
        }
    };

    // Event Listeners
    decodeBtn.addEventListener("click", () => {
        handleDecode(queryInput.value);
    });

    queryInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            handleDecode(queryInput.value);
        }
    });

    filterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            queryInput.value = query;
            handleDecode(query);
        });
    });
});
