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
function showAddToCartToast() {
    const toast = document.getElementById("cart-success-toast");
    if (!toast) return;

    toast.classList.add("show");

    clearTimeout(window.cartToastTimer);
    window.cartToastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 1400);
}

if (addToCartBtn) {
    addToCartBtn.addEventListener("click", function (e) {
        e.preventDefault();

        const qty = parseInt(document.getElementById("qty").value || 1);
        const productId = parseInt(window.location.pathname.split("/").pop());

        fetch("/api/carts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id: productId,
                quantity: qty
            })
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Có lỗi xảy ra");
            return data;
        })
        .then(data => {
            updateCartBadge(data.total_items);
            showAddToCartToast();
        })
        .catch(err => {
            alert(err.message);
        });
    });
}
function updateCartBadge(count) {
    const badge = document.getElementById("cart-badge");
    if (badge) {
        badge.innerText = count;
    }
}
function updateCartRowUI(row, quantity) {
    const qtyInput = row.querySelector(".qty-input");
    const priceValue = row.querySelector(".cart-price-value");
    const totalCell = row.querySelector(".cart-col-total");

    if (!qtyInput || !priceValue || !totalCell) return;

    qtyInput.value = quantity;

    const priceText = priceValue.textContent.replace(/\./g, "").replace("đ", "").trim();
    const price = parseInt(priceText, 10) || 0;
    const total = price * quantity;

    totalCell.textContent = total.toLocaleString("vi-VN") + "đ";
}
// ===== CART DELETE MODAL =====
const cartDeleteModal = document.getElementById("cartDeleteModal");
const cartDeleteModalProductName = document.getElementById("cartDeleteModalProductName");
const cartDeleteModalConfirm = document.getElementById("cartDeleteModalConfirm");
const cartDeleteModalCancel = document.getElementById("cartDeleteModalCancel");

let cartDeleteModalResolver = null;

function openCartDeleteModal(productName) {
    return new Promise((resolve) => {
        if (!cartDeleteModal) {
            resolve(window.confirm("Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng không?"));
            return;
        }

        cartDeleteModalProductName.textContent = productName || "";
        cartDeleteModal.classList.add("show");
        document.body.style.overflow = "hidden";
        cartDeleteModalResolver = resolve;
    });
}

function closeCartDeleteModal(result) {
    if (!cartDeleteModal) return;

    cartDeleteModal.classList.remove("show");
    document.body.style.overflow = "";

    if (cartDeleteModalResolver) {
        cartDeleteModalResolver(result);
        cartDeleteModalResolver = null;
    }
}

if (cartDeleteModalConfirm) {
    cartDeleteModalConfirm.addEventListener("click", function () {
        closeCartDeleteModal(true);
    });
}

if (cartDeleteModalCancel) {
    cartDeleteModalCancel.addEventListener("click", function () {
        closeCartDeleteModal(false);
    });
}

if (cartDeleteModal) {
    cartDeleteModal.addEventListener("click", function (e) {
        if (e.target.classList.contains("cart-delete-modal__backdrop")) {
            closeCartDeleteModal(false);
        }
    });
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && cartDeleteModal && cartDeleteModal.classList.contains("show")) {
        closeCartDeleteModal(false);
    }
});
document.querySelectorAll(".cart-item-row").forEach(row => {
    const productId = row.dataset.productId;
    const decreaseBtn = row.querySelector(".qty-decrease");
    const increaseBtn = row.querySelector(".qty-increase");
    const qtyInput = row.querySelector(".qty-input");
    const deleteLink = row.querySelector(".cart-delete-link");
    const productName = row.querySelector(".cart-col-product h6")?.textContent?.trim() || "Sản phẩm này";
    async function removeCartItem() {
        const res = await fetch(`/api/carts/${productId}`, {
            method: "DELETE"
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || "Không thể xóa sản phẩm");
        }

        row.remove();
        updateCartBadge(data.total_items);
        updateCartSelectionState();

        if (document.querySelectorAll(".cart-item-row").length === 0) {
            window.location.reload();
        }
    }

    async function updateQuantity(newQty) {
        try {
            const res = await fetch(`/api/carts/${productId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    quantity: newQty
                })
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Không thể cập nhật giỏ hàng");
            }

            updateCartRowUI(row, newQty);
            updateCartBadge(data.total_items);
            updateCartSelectionState();
        } catch (err) {
            alert(err.message);
        }
    }

    if (decreaseBtn) {
        decreaseBtn.addEventListener("click", async function () {
            let currentQty = parseInt(qtyInput.value || 1);

            if (currentQty > 1) {
                updateQuantity(currentQty - 1);
                return;
            }

            const confirmed = await openCartDeleteModal(productName);
if (!confirmed) return;

            try {
                await removeCartItem();
            } catch (err) {
                alert(err.message);
            }
        });
    }

    if (increaseBtn) {
        increaseBtn.addEventListener("click", function () {
            let currentQty = parseInt(qtyInput.value || 1);
            updateQuantity(currentQty + 1);
        });
    }

    if (deleteLink) {
        deleteLink.addEventListener("click", async function (e) {
            e.preventDefault();

            const confirmed = await openCartDeleteModal(productName);
if (!confirmed) return;

            try {
                await removeCartItem();
            } catch (err) {
                alert(err.message);
            }
        });
    }
});
// ===== CART CHECKBOX + CHỌN TẤT CẢ + TỔNG TIỀN =====
const checkAllCart = document.getElementById("checkAllCart");
const checkAllCartLabel = document.getElementById("checkAllCartLabel");
const cartGrandTotal = document.getElementById("cartGrandTotal");
const deleteSelectedCart = document.getElementById("deleteSelectedCart");

function getCartRows() {
    return Array.from(document.querySelectorAll(".cart-item-row"));
}

function getCartCheckboxes() {
    return Array.from(document.querySelectorAll(".cart-item-checkbox"));
}

function parseMoney(text) {
    return parseInt(
        String(text || "")
            .replace(/\./g, "")
            .replace(/đ/g, "")
            .trim(),
        10
    ) || 0;
}

function formatMoney(value) {
    return (value || 0).toLocaleString("vi-VN") + "đ";
}

function updateCheckAllLabelCount() {
    if (!checkAllCartLabel) return;
    const totalProducts = getCartRows().length;
    checkAllCartLabel.textContent = `Chọn tất cả (${totalProducts})`;
}
function updateSelectedProductCount() {
    const selectedRows = getCartRows().filter(row => {
        const checkbox = row.querySelector(".cart-item-checkbox");
        return checkbox && checkbox.checked;
    });

    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = selectedRows.length;
    }
}
function updateCartSelectionState() {
    const rows = getCartRows();
    const checkboxes = getCartCheckboxes();

    if (!rows.length) {
    if (checkAllCart) {
        checkAllCart.checked = false;
        checkAllCart.disabled = true;
    }
    if (cartGrandTotal) {
        cartGrandTotal.textContent = "0đ";
    }

    const cartCount = document.getElementById("cart-count");
    if (cartCount) {
        cartCount.textContent = "0";
    }

    updateCheckAllLabelCount();
    return;
}

    if (checkAllCart) {
        checkAllCart.disabled = false;
        checkAllCart.checked = checkboxes.length > 0 && checkboxes.every(cb => cb.checked);
    }

    let total = 0;

    rows.forEach(row => {
        const checkbox = row.querySelector(".cart-item-checkbox");
        const totalCell = row.querySelector(".cart-col-total");

        if (checkbox && checkbox.checked && totalCell) {
            total += parseMoney(totalCell.textContent);
        }
    });

    if (cartGrandTotal) {
    cartGrandTotal.textContent = formatMoney(total);
}

updateCheckAllLabelCount();
updateSelectedProductCount();
}

if (checkAllCart) {
    checkAllCart.addEventListener("change", function () {
        const checked = this.checked;
        getCartCheckboxes().forEach(cb => {
            cb.checked = checked;
        });
        updateCartSelectionState();
    });
}

document.addEventListener("change", function (e) {
    if (e.target.classList.contains("cart-item-checkbox")) {
        updateCartSelectionState();
    }
});

if (deleteSelectedCart) {
    deleteSelectedCart.addEventListener("click", async function (e) {
        e.preventDefault();

        const selectedRows = getCartRows().filter(row => {
            const checkbox = row.querySelector(".cart-item-checkbox");
            return checkbox && checkbox.checked;
        });

        if (!selectedRows.length) {
            alert("Vui lòng chọn ít nhất 1 sản phẩm để xóa.");
            return;
        }

        const modalTitle = document.querySelector(".cart-delete-modal__title");
        if (modalTitle) {
            modalTitle.textContent = "Bạn chắc chắn muốn bỏ các sản phẩm này?";
        }

        const confirmed = await openCartDeleteModal(`${selectedRows.length} sản phẩm đã chọn`);
        if (!confirmed) return;

        try {
            for (const row of selectedRows) {
                const productId = row.dataset.productId;

                const res = await fetch(`/api/carts/${productId}`, {
                    method: "DELETE"
                });

                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.error || "Không thể xóa sản phẩm");
                }

                row.remove();
                updateCartBadge(data.total_items);
            }

            updateCartSelectionState();

            if (getCartRows().length === 0) {
                window.location.reload();
            }
        } catch (err) {
            alert(err.message);
        } finally {
            if (modalTitle) {
                modalTitle.textContent = "Bạn chắc chắn muốn bỏ sản phẩm này?";
            }
        }
    });
}
// ===== COUPON TABS =====
const couponTabButtons = document.querySelectorAll(".coupon-tab-btn");
const couponTabPanels = document.querySelectorAll(".coupon-tab-panel");

if (couponTabButtons.length && couponTabPanels.length) {
    couponTabButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const tab = this.dataset.couponTab;

            couponTabButtons.forEach(item => item.classList.remove("active"));
            couponTabPanels.forEach(panel => panel.classList.remove("active"));

            this.classList.add("active");

            const targetPanel = document.getElementById(`coupon-tab-${tab}`);
            if (targetPanel) {
                targetPanel.classList.add("active");
            }
        });
    });
}
// ===== COUPON DETAIL MODAL =====
const couponDetailModal = document.getElementById("couponDetailModal");
const couponModalCloseBtn = document.getElementById("couponModalCloseBtn");

function closeCouponModal() {
    if (!couponDetailModal) return;
    couponDetailModal.classList.remove("show");
    document.body.style.overflow = "";
}

function openCouponModal() {
    if (!couponDetailModal) return;
    couponDetailModal.classList.add("show");
    document.body.style.overflow = "hidden";
}

document.querySelectorAll(".coupon-detail-btn").forEach(btn => {
    btn.addEventListener("click", function () {
        const name = this.dataset.name;
        const code = this.dataset.code;
        const start = this.dataset.start;
        const end = this.dataset.end;
        const min = this.dataset.min;
        const apply = this.dataset.apply;
        const desc = this.dataset.desc;

        document.getElementById("cd-name").innerText = name;
        document.getElementById("cd-code").innerText = code;
        let dateText = "Không giới hạn";

if (start && end) {
    dateText = `${start} → ${end}`;
} else if (!start && end) {
    dateText = `Đến ${end}`;
} else if (start && !end) {
    dateText = `Từ ${start}`;
}

document.getElementById("cd-date").innerText = dateText;
        const minValue = Number(min || 0);
document.getElementById("cd-min").innerText = `Đơn tối thiểu ${minValue.toLocaleString("vi-VN")}đ`;
        document.getElementById("cd-apply").innerText = apply;
        document.getElementById("cd-desc").innerText = desc || "Không có mô tả";

        const endDate = end ? new Date(end.replace(" ", "T")) : null;
        const now = new Date();
        const warning = document.getElementById("cd-warning");

        if (endDate) {
            const diff = Math.ceil((endDate - now) / (1000 * 60 * 60 * 24));

            if (diff <= 5 && diff > 0) {
                warning.innerText = `${diff} ngày nữa hết hạn`;
            } else if (diff <= 0) {
                warning.innerText = "Đã hết hạn";
            } else {
                warning.innerText = "";
            }
        } else {
            warning.innerText = "";
        }

        openCouponModal();
    });
});

if (couponModalCloseBtn) {
    couponModalCloseBtn.addEventListener("click", closeCouponModal);
}

if (couponDetailModal) {
    couponDetailModal.addEventListener("click", function (e) {
        if (e.target === couponDetailModal) {
            closeCouponModal();
        }
    });
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && couponDetailModal && couponDetailModal.classList.contains("show")) {
        closeCouponModal();
    }
});
});