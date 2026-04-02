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
    // ===== TOGGLE MAX DISCOUNT WHEN PERCENTAGE =====
const discountRadios = document.querySelectorAll('input[name="discount_kind"]');
const maxDiscountGroup = document.getElementById("max-discount-group");
const maxDiscountInput = document.querySelector('input[name="max_discount_value"]');

function toggleMaxDiscount() {
    const selected = document.querySelector('input[name="discount_kind"]:checked');

    if (!maxDiscountGroup) return;

    if (selected && selected.value === "percentage") {
        maxDiscountGroup.style.display = "block";
    } else {
        maxDiscountGroup.style.display = "none";
        if (maxDiscountInput) {
            maxDiscountInput.value = "";
            maxDiscountInput.classList.remove("is-invalid");
        }
    }
}

if (discountRadios.length) {
    discountRadios.forEach(radio => {
        radio.addEventListener("change", toggleMaxDiscount);
    });
    toggleMaxDiscount();
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
// ===== EDIT FORM: TOGGLE MAX DISCOUNT =====
    const editDiscountKind = document.getElementById("edit_discount_kind");
    const editMaxDiscountGroup = document.getElementById("edit-max-discount-group");

    function toggleEditMaxDiscount() {
        if (!editDiscountKind || !editMaxDiscountGroup) return;

        if (editDiscountKind.value === "percentage") {
            editMaxDiscountGroup.style.display = "block";
        } else {
            editMaxDiscountGroup.style.display = "none";
            const input = editMaxDiscountGroup.querySelector('input[name="max_discount_value"]');
            if (input) input.value = "";
        }
    }

    if (editDiscountKind) {
        editDiscountKind.addEventListener("change", toggleEditMaxDiscount);
        toggleEditMaxDiscount();
    }
    const requireLoginButtons = document.querySelectorAll(".require-login");

if (requireLoginButtons.length) {
    requireLoginButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            const modal = new bootstrap.Modal(
                document.getElementById("loginRequiredModal")
            );
            modal.show();
        });
    });
}
// ===== PRODUCT DETAIL QUANTITY =====
const qtyInput = document.getElementById("qty");
const decreaseBtn = document.getElementById("qty-decrease");
const increaseBtn = document.getElementById("qty-increase");
const addToCartBtn = document.getElementById("add-to-cart-btn");
const buyNowBtn = document.getElementById("buy-now-btn");
const qtyError = document.getElementById("qty-error");

if (qtyInput && decreaseBtn && increaseBtn && addToCartBtn && buyNowBtn && qtyError) {
    const min = parseInt(qtyInput.min) || 1;
    const max = parseInt(qtyInput.max) || 0;

    function disableActionButton(btn, disabled) {
        if (!btn) return;

        if (disabled) {
            btn.classList.add("disabled");
            btn.setAttribute("aria-disabled", "true");
            btn.style.pointerEvents = "none";
            btn.style.opacity = "0.65";
        } else {
            btn.classList.remove("disabled");
            btn.removeAttribute("aria-disabled");
            btn.style.pointerEvents = "";
            btn.style.opacity = "";
        }
    }

    function syncQuantityState() {
        let value = parseInt(qtyInput.value);

        if (isNaN(value)) {
            value = min;
        }

        if (value < min) {
            value = min;
        }

        const isOverStock = value > max;
        const isOutOfStock = max <= 0;

        if (isOutOfStock) {
            qtyInput.value = 0;
            qtyInput.setAttribute("readonly", "readonly");
            decreaseBtn.disabled = true;
            increaseBtn.disabled = true;
            disableActionButton(addToCartBtn, true);
            disableActionButton(buyNowBtn, true);

            qtyError.classList.remove("d-none");
            qtyError.textContent = "Sản phẩm hiện đã hết hàng.";
            return;
        } else {
            qtyInput.removeAttribute("readonly");
        }

        if (isOverStock) {
            qtyInput.value = max;
            qtyError.classList.remove("d-none");
            qtyError.textContent = "Số lượng đặt không được vượt quá số lượng tồn kho.";
        } else {
            qtyInput.value = value;
            qtyError.classList.add("d-none");
        }

        const currentValue = parseInt(qtyInput.value) || min;

        decreaseBtn.disabled = currentValue <= min;
        increaseBtn.disabled = currentValue >= max;

        const shouldDisableAction = currentValue > max || currentValue < min;
        disableActionButton(addToCartBtn, shouldDisableAction);
        disableActionButton(buyNowBtn, shouldDisableAction);
    }

    decreaseBtn.addEventListener("click", function () {
        let current = parseInt(qtyInput.value) || min;
        if (current > min) {
            qtyInput.value = current - 1;
        }
        syncQuantityState();
    });

    increaseBtn.addEventListener("click", function () {
        let current = parseInt(qtyInput.value) || min;
        if (current < max) {
            qtyInput.value = current + 1;
        }
        syncQuantityState();
    });

    qtyInput.addEventListener("input", function () {
        this.value = this.value.replace(/[^\d]/g, "");
        syncQuantityState();
    });

    qtyInput.addEventListener("blur", function () {
        syncQuantityState();
    });

    syncQuantityState();
}
if (addToCartBtn) {
    addToCartBtn.addEventListener("click", function (e) {
        e.preventDefault();

        const qty = document.getElementById("qty").value;
        const productId = window.location.pathname.split("/").pop();

        fetch("/api/add-to-cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `product_id=${productId}&quantity=${qty}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateCartBadge(data.count);
                alert("Đã thêm vào giỏ hàng");
            } else {
                alert(data.error);
            }
        });
    });
}
function updateCartBadge(count) {
    const badge = document.getElementById("cart-badge");
    if (badge) {
        badge.innerText = count;
    }
}

});