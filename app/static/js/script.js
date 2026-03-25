document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");
    const main = document.querySelector(".admin-main");

    if (btn && sidebar && main) {
        btn.addEventListener("click", function () {
            sidebar.classList.toggle("active");
            main.classList.toggle("shifted");
        });
    }

    const radios = document.querySelectorAll('input[name="apply_scope"]');
    const scopeAll = document.getElementById("scope-all");
    const scopeCategory = document.getElementById("scope-category");
    const scopeProduct = document.getElementById("scope-product");

    function updateScopePanel() {
        const selected = document.querySelector('input[name="apply_scope"]:checked')?.value;

        if (scopeAll) scopeAll.classList.remove("active");
        if (scopeCategory) scopeCategory.classList.remove("active");
        if (scopeProduct) scopeProduct.classList.remove("active");

        if (selected === "all_product" && scopeAll) {
            scopeAll.classList.add("active");
        } else if (selected === "selected_category" && scopeCategory) {
            scopeCategory.classList.add("active");
        } else if (selected === "selected_product" && scopeProduct) {
            scopeProduct.classList.add("active");
        }
    }

    if (radios.length) {
        radios.forEach(radio => {
            radio.addEventListener("change", updateScopePanel);
        });
        updateScopePanel();
    }

    const searchInput = document.getElementById("product-search");
    const productCards = document.querySelectorAll(".scope-product-card");

    if (searchInput && productCards.length) {
        searchInput.addEventListener("input", function () {
            const keyword = this.value.trim().toLowerCase();

            productCards.forEach(card => {
                const name = card.dataset.name || "";
                card.style.display = name.includes(keyword) ? "flex" : "none";
            });
        });
    }
    if (typeof flatpickr !== "undefined") {
    const startPicker = flatpickr("#start_date", {
        enableTime: true,
        time_24hr: true,
        dateFormat: "d/m/Y H:i",
        minDate: "today"
    });

    const endPicker = flatpickr("#end_date", {
        enableTime: true,
        time_24hr: true,
        dateFormat: "d/m/Y H:i"
    });

    if (startPicker && endPicker) {
        startPicker.config.onChange.push(function(selectedDates) {
            endPicker.set("minDate", selectedDates[0]);
        });
    }
}
// ===== VALIDATE FORM =====
const form = document.querySelector(".coupon-create-form");
const errorBox = document.getElementById("form-error");

if (form) {
    form.addEventListener("submit", function (e) {
        let isValid = true;
        let firstError = null;

        const requiredFields = document.querySelectorAll(".required-field");

        requiredFields.forEach(input => {
            input.classList.remove("is-invalid");

            if (!input.value || input.value.trim() === "") {
                isValid = false;
                input.classList.add("is-invalid");

                if (!firstError) {
                    firstError = input;
                }
            }
        });

        // validate category/product nếu chọn
        const scope = document.querySelector('input[name="apply_scope"]:checked')?.value;

        if (scope === "selected_category") {
            const checked = document.querySelectorAll('input[name="category_ids"]:checked');
            if (checked.length === 0) {
                isValid = false;
                document.getElementById("scope-category").classList.add("is-invalid-group");
                firstError = firstError || document.getElementById("scope-category");
            }
        }

        if (scope === "selected_product") {
            const checked = document.querySelectorAll('input[name="product_ids"]:checked');
            if (checked.length === 0) {
                isValid = false;
                document.getElementById("scope-product").classList.add("is-invalid-group");
                firstError = firstError || document.getElementById("scope-product");
            }
        }

        if (!isValid) {
            e.preventDefault();

            if (errorBox) {
                errorBox.classList.remove("d-none");
            }

            if (firstError) {
                firstError.scrollIntoView({ behavior: "smooth", block: "center" });
                if (firstError.focus) firstError.focus();
            }
        }
    });
}
});