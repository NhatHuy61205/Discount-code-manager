document.addEventListener("DOMContentLoaded", function () {
    let selectedCoupon = null;
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
function bindRequireLoginButtons(scope = document) {
    scope.querySelectorAll(".require-login").forEach(btn => {
        if (btn.dataset.loginBound === "true") return;

        btn.dataset.loginBound = "true";
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            const modalEl = document.getElementById("loginRequiredModal");
            if (!modalEl) return;

            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        });
    });
}

bindRequireLoginButtons();
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
if (buyNowBtn) {
    buyNowBtn.addEventListener("click", async function (e) {
        e.preventDefault();

        const qty = parseInt(document.getElementById("qty").value || 1);
        const productId = parseInt(window.location.pathname.split("/").pop());

        this.classList.add("disabled");
        this.setAttribute("aria-disabled", "true");
        this.style.pointerEvents = "none";
        this.style.opacity = "0.65";

        try {
            const res = await fetch("/api/carts", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    id: productId,
                    quantity: qty
                })
            });

            const contentType = res.headers.get("content-type") || "";

            if (!contentType.includes("application/json")) {
                throw new Error("Vui lòng đăng nhập để tiếp tục mua hàng.");
            }

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Không thể mua ngay");
            }

            window.location.href = `/cart?buy_now_product_id=${productId}`;
        } catch (err) {
            alert(err.message);
        } finally {
            this.classList.remove("disabled");
            this.removeAttribute("aria-disabled");
            this.style.pointerEvents = "";
            this.style.opacity = "";
        }
    });
}
function updateCartBadge(count) {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;

    const value = parseInt(count, 10) || 0;
    badge.innerText = value;

    if (value > 0) {
        badge.classList.remove("d-none");
    } else {
        badge.classList.add("d-none");
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
    if (data.max_quantity) {
        alert(data.error || "Số lượng vượt quá tồn kho");

        updateCartRowUI(row, data.max_quantity);
        updateCartBadge(data.total_items);

        await refreshSelectedCouponDiscount();
        updateCartSelectionState();

        return;
    }

    throw new Error(data.error || "Không thể cập nhật giỏ hàng");
}

            updateCartRowUI(row, newQty);
updateCartBadge(data.total_items);

await refreshSelectedCouponDiscount();

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
    if (qtyInput) {
    qtyInput.addEventListener("input", function () {
        this.value = this.value.replace(/[^\d]/g, "");
    });

    qtyInput.addEventListener("blur", function () {
        let newQty = parseInt(this.value, 10);

        if (isNaN(newQty) || newQty <= 0) {
            newQty = 1;
        }

        updateQuantity(newQty);
    });

    qtyInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            this.blur();
        }
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
async function refreshSelectedCouponDiscount() {
    if (!selectedCoupon || !selectedCoupon.coupon_id) return;

    const selectedProductIds = getSelectedCartProductIds();

    if (!selectedProductIds.length) {
        selectedCoupon = null;
        return;
    }

    try {
        const res = await fetch("/api/cart/apply-coupon", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                coupon_id: selectedCoupon.coupon_id,
                selected_product_ids: selectedProductIds
            })
        });

        const data = await res.json();

        if (!res.ok) {
            selectedCoupon = null;

            const actionText = document.querySelector(".cart-voucher-action");
            if (actionText) {
                actionText.textContent = "Chọn hoặc nhập mã";
            }

            return;
        }

        selectedCoupon = data.coupon;
        selectedCoupon.selected_product_ids = [...selectedProductIds];

    } catch (err) {
        selectedCoupon = null;
    }
}
function updateCartSelectionState() {
    const rows = getCartRows();
    const checkboxes = getCartCheckboxes();
    const currentSelectedProductIds = getSelectedCartProductIds();

function isSameArray(a, b) {
    if (a.length !== b.length) return false;
    return a.every(v => b.includes(v));
}

if (
    selectedCoupon &&
    (!currentSelectedProductIds.length ||
     !isSameArray(currentSelectedProductIds, selectedCoupon.selected_product_ids || []))
) {
    selectedCoupon = null;

    const actionText = document.querySelector(".cart-voucher-action");
    if (actionText) {
        actionText.textContent = "Chọn hoặc nhập mã";
    }
}

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

    let finalTotal = total;
let discount = 0;

if (selectedCoupon && selectedCoupon.discount_amount) {
    discount = selectedCoupon.discount_amount;
    finalTotal = Math.max(0, total - discount);
}
const summarySubtotal = document.getElementById("summarySubtotal");
const summaryDiscount = document.getElementById("summaryDiscount");
const summarySaving = document.getElementById("summarySaving");
const summaryFinal = document.getElementById("summaryFinal");
const cartSummaryHover = document.getElementById("cartSummaryHover");

if (summarySubtotal) {
    summarySubtotal.textContent = formatMoney(total);
}

if (summaryDiscount) {
    summaryDiscount.textContent = discount > 0 ? "-" + formatMoney(discount) : "0đ";
}

if (summarySaving) {
    summarySaving.textContent = discount > 0 ? "-" + formatMoney(discount) : "0đ";
}

if (summaryFinal) {
    summaryFinal.textContent = formatMoney(finalTotal);
}

// tổng tiền sau giảm
if (cartGrandTotal) {
    cartGrandTotal.textContent = formatMoney(finalTotal);
}

// hiển thị tiết kiệm
const cartDiscount = document.getElementById("cartDiscount");
if (cartDiscount) {
    if (discount > 0) {
        cartDiscount.textContent = "Tiết kiệm " + formatMoney(discount);
        cartDiscount.classList.remove("d-none");
    } else {
        cartDiscount.textContent = "Tiết kiệm 0đ";
        cartDiscount.classList.add("d-none");
    }
}

if (cartSummaryHover) {
    if (discount > 0) {
        cartSummaryHover.classList.remove("d-none");
    } else {
        cartSummaryHover.classList.add("d-none");
    }
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
(function handleBuyNowProductSelection() {
    const params = new URLSearchParams(window.location.search);
    const buyNowProductId = parseInt(params.get("buy_now_product_id"), 10);

    if (Number.isNaN(buyNowProductId)) {
        return;
    }

    const targetRow = document.querySelector(`.cart-item-row[data-product-id="${buyNowProductId}"]`);

    if (targetRow) {
        const checkbox = targetRow.querySelector(".cart-item-checkbox");

        if (checkbox) {
            getCartCheckboxes().forEach(cb => {
                cb.checked = false;
            });

            checkbox.checked = true;
            updateCartSelectionState();
        }
    }

    params.delete("buy_now_product_id");
    const newUrl = `${window.location.pathname}${params.toString() ? "?" + params.toString() : ""}${window.location.hash}`;
    window.history.replaceState({}, "", newUrl);
})();

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
// ===== CART BUY BUTTON + WARNING MODAL =====
const cartBuyBtn = document.getElementById("cartBuyBtn");
const cartCheckoutWarningModal = document.getElementById("cartCheckoutWarningModal");
const cartCheckoutWarningModalOk = document.getElementById("cartCheckoutWarningModalOk");

function getSelectedCartProductIds() {
    return getCartRows()
        .filter(row => {
            const checkbox = row.querySelector(".cart-item-checkbox");
            return checkbox && checkbox.checked;
        })
        .map(row => parseInt(row.dataset.productId, 10))
        .filter(id => !isNaN(id));
}

function openCartCheckoutWarningModal() {
    if (!cartCheckoutWarningModal) {
        alert("Bạn vẫn chưa chọn sản phẩm nào để mua.");
        return;
    }

    cartCheckoutWarningModal.classList.add("show");
    document.body.style.overflow = "hidden";
}

function closeCartCheckoutWarningModal() {
    if (!cartCheckoutWarningModal) return;

    cartCheckoutWarningModal.classList.remove("show");
    document.body.style.overflow = "";
}

if (cartCheckoutWarningModalOk) {
    cartCheckoutWarningModalOk.addEventListener("click", closeCartCheckoutWarningModal);
}

if (cartCheckoutWarningModal) {
    cartCheckoutWarningModal.addEventListener("click", function (e) {
        if (e.target.classList.contains("cart-delete-modal__backdrop")) {
            closeCartCheckoutWarningModal();
        }
    });
}

document.addEventListener("keydown", function (e) {
    if (
        e.key === "Escape" &&
        cartCheckoutWarningModal &&
        cartCheckoutWarningModal.classList.contains("show")
    ) {
        closeCartCheckoutWarningModal();
    }
});

if (cartBuyBtn) {
    cartBuyBtn.addEventListener("click", function (e) {
        e.preventDefault();

        const selectedProductIds = getSelectedCartProductIds();

        if (!selectedProductIds.length) {
            openCartCheckoutWarningModal();
            return;
        }

        const query = new URLSearchParams();
        selectedProductIds.forEach(id => query.append("selected_product_ids", id));

        if (selectedCoupon && selectedCoupon.coupon_id) {
            query.append("coupon_id", selectedCoupon.coupon_id);
            query.append("coupon_code", selectedCoupon.code || "");
            query.append("discount_amount", selectedCoupon.discount_amount || 0);
        }

        window.location.href = `/checkout?${query.toString()}`;
    });
}
// Test ÁP Mã
// ===== SHARED COUPON MODAL =====
const sharedCouponModal = document.getElementById("sharedCouponModal");
const sharedCouponModalClose = document.getElementById("sharedCouponModalClose");
const sharedCouponModalCancel = document.getElementById("sharedCouponModalCancel");
const sharedCouponModalConfirm = document.getElementById("sharedCouponModalConfirm");
const sharedCouponKeyword = document.getElementById("sharedCouponKeyword");
const sharedCouponList = document.getElementById("sharedCouponList");

const openCartCouponModalBtn = document.getElementById("openCartCouponModal");
const openCheckoutCouponModalBtn = document.getElementById("openCheckoutCouponModal");

let couponModalSource = null; // "cart" | "checkout"

function openSharedCouponModal() {
    if (!sharedCouponModal) return;
    sharedCouponModal.classList.add("show");
    document.body.style.overflow = "hidden";
}

function closeSharedCouponModal() {
    if (!sharedCouponModal) return;
    sharedCouponModal.classList.remove("show");
    document.body.style.overflow = "";
}

function showSharedCouponWarning(message) {
    if (!sharedCouponList) return;
    sharedCouponList.innerHTML = `
        <div class="cart-coupon-empty">${message}</div>
    `;
}

function getCheckoutSelectedProductIds() {
    const raw = document.getElementById("checkoutSelectedProductIds")?.value || "";
    return raw
        .split(",")
        .map(v => parseInt(v.trim(), 10))
        .filter(v => !isNaN(v));
}

function getCurrentSelectedProductIds() {
    if (couponModalSource === "checkout") {
        return getCheckoutSelectedProductIds();
    }
    return getSelectedCartProductIds();
}

function renderSharedCouponList(coupons) {
    if (!sharedCouponList) return;

    if (!coupons || !coupons.length) {
        sharedCouponList.innerHTML = `
            <div class="cart-coupon-empty">
                Bạn chưa sở hữu mã giảm giá nào.
            </div>
        `;
        return;
    }

    sharedCouponList.innerHTML = coupons.map(coupon => {
        const disabledClass = coupon.is_usable ? "" : " is-disabled";
        const checkedArea = coupon.is_usable
            ? `<input
                    type="radio"
                    name="selected_shared_coupon"
                    class="cart-coupon-radio"
                    value="${coupon.coupon_id}"
                    data-code="${coupon.code}"
               >`
            : "";

        const statusText = coupon.is_usable
            ? `<div class="cart-coupon-item__status text-success">Có thể áp dụng</div>`
            : `<div class="cart-coupon-item__status text-muted">${coupon.invalid_reason || "Không khả dụng"}</div>`;

        return `
            <label class="cart-coupon-item${disabledClass}">
                ${checkedArea}

                <div class="cart-coupon-item__left">
                    <div class="cart-coupon-item__badge">Đã lưu</div>

                    <div class="cart-coupon-item__value">
                        ${coupon.discount_kind === "percentage"
                            ? `Giảm ${parseInt(coupon.discount_value)}%`
                            : `Giảm ${Number(coupon.discount_value).toLocaleString("vi-VN")}đ`}
                    </div>

                    ${coupon.max_discount_value
                        ? `<div class="cart-coupon-item__sub">
                            Tối đa ${Number(coupon.max_discount_value).toLocaleString("vi-VN")}đ
                           </div>`
                        : ""}

                    <div class="cart-coupon-item__min-order">
                        Đơn tối thiểu ${Number(coupon.min_order_value || 0).toLocaleString("vi-VN")}đ
                    </div>
                </div>

                <div class="cart-coupon-item__right">
                    <div class="cart-coupon-item__name">${coupon.name}</div>
                    <div class="cart-coupon-item__code">${coupon.code}</div>
                    <div class="cart-coupon-item__meta">${coupon.apply_type_text}</div>
                    ${statusText}
                    <div class="cart-coupon-item__date">HSD: ${coupon.end_date || "Không giới hạn"}</div>
                </div>
            </label>
        `;
    }).join("");
}

async function handleOpenSharedCouponModal(e, source) {
    e.preventDefault();
    couponModalSource = source;

    const selectedProductIds = getCurrentSelectedProductIds();

    try {
        const res = await fetch("/api/cart/available-coupons", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                selected_product_ids: selectedProductIds
            })
        });

        const data = await res.json();

        if (!res.ok) {
            showSharedCouponWarning(data.message || "Vui lòng chọn sản phẩm trước khi chọn mã giảm giá");
            openSharedCouponModal();
            return;
        }

        renderSharedCouponList(data.coupons || []);
        openSharedCouponModal();
    } catch (err) {
        showSharedCouponWarning("Không thể tải mã giảm giá");
        openSharedCouponModal();
    }
}

if (openCartCouponModalBtn) {
    openCartCouponModalBtn.addEventListener("click", (e) => handleOpenSharedCouponModal(e, "cart"));
}

if (openCheckoutCouponModalBtn) {
    openCheckoutCouponModalBtn.addEventListener("click", (e) => handleOpenSharedCouponModal(e, "checkout"));
}

if (sharedCouponModalClose) {
    sharedCouponModalClose.addEventListener("click", closeSharedCouponModal);
}

if (sharedCouponModalCancel) {
    sharedCouponModalCancel.addEventListener("click", closeSharedCouponModal);
}

if (sharedCouponModal) {
    sharedCouponModal.addEventListener("click", function (e) {
        if (e.target.classList.contains("cart-coupon-modal__backdrop")) {
            closeSharedCouponModal();
        }
    });
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && sharedCouponModal && sharedCouponModal.classList.contains("show")) {
        closeSharedCouponModal();
    }
});

if (sharedCouponKeyword) {
    sharedCouponKeyword.addEventListener("input", function () {
        const keyword = this.value.trim().toLowerCase();
        const items = sharedCouponModal.querySelectorAll(".cart-coupon-item");

        items.forEach(item => {
            const code = item.querySelector(".cart-coupon-item__code")?.textContent?.toLowerCase() || "";
            const name = item.querySelector(".cart-coupon-item__name")?.textContent?.toLowerCase() || "";
            item.style.display = (code.includes(keyword) || name.includes(keyword)) ? "" : "none";
        });
    });
}

if (sharedCouponModalConfirm) {
    sharedCouponModalConfirm.addEventListener("click", async function () {
        const selected = document.querySelector('input[name="selected_shared_coupon"]:checked');

        if (!selected) {
            alert("Vui lòng chọn 1 mã giảm giá khả dụng.");
            return;
        }

        const couponId = parseInt(selected.value, 10);
        const selectedProductIds = getCurrentSelectedProductIds();

        try {
            const res = await fetch("/api/cart/apply-coupon", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    coupon_id: couponId,
                    selected_product_ids: selectedProductIds
                })
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.message || "Không thể áp mã");
                return;
            }

            selectedCoupon = data.coupon;
            selectedCoupon.selected_product_ids = [...selectedProductIds];

            if (couponModalSource === "cart") {
                const actionText = document.querySelector(".cart-voucher-action");
                if (actionText) {
                    actionText.textContent = selectedCoupon.code;
                }
                updateCartSelectionState();
            }

            if (couponModalSource === "checkout") {
    const params = new URLSearchParams(window.location.search);

    const productIds = getCheckoutSelectedProductIds();
    params.delete("selected_product_ids");
    productIds.forEach(id => params.append("selected_product_ids", id));

    params.set("coupon_id", selectedCoupon.coupon_id);
    params.set("coupon_code", selectedCoupon.code);

    // 🔥 THÊM DÒNG NÀY
    params.set("discount_amount", selectedCoupon.discount_amount || 0);

    window.location.href = "/checkout?" + params.toString();
}

            closeSharedCouponModal();
        } catch (err) {
            alert("Không thể áp mã giảm giá");
    } finally {
        this.disabled = false;
    }
    });
}
// ===== CHECKOUT ADDRESS MODAL =====
const checkoutAddressModal = document.getElementById("checkoutAddressModal");
const openAddressModal = document.getElementById("openAddressModal");
const openAddressModalEmpty = document.getElementById("openAddressModalEmpty");
const checkoutAddressModalClose = document.getElementById("checkoutAddressModalClose");

function showCheckoutAddressModal() {
    if (!checkoutAddressModal) return;
    checkoutAddressModal.classList.add("show");
    document.body.style.overflow = "hidden";
}

function hideCheckoutAddressModal() {
    if (!checkoutAddressModal) return;
    checkoutAddressModal.classList.remove("show");
    document.body.style.overflow = "";
}

if (openAddressModal) {
    openAddressModal.addEventListener("click", function (e) {
        e.preventDefault();
        showCheckoutAddressModal();
    });
}

if (openAddressModalEmpty) {
    openAddressModalEmpty.addEventListener("click", function (e) {
        e.preventDefault();
        showCheckoutAddressModal();
    });
}

if (checkoutAddressModalClose) {
    checkoutAddressModalClose.addEventListener("click", hideCheckoutAddressModal);
}

if (checkoutAddressModal) {
    checkoutAddressModal.addEventListener("click", function (e) {
        if (e.target.classList.contains("checkout-address-modal__backdrop")) {
            hideCheckoutAddressModal();
        }
    });
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && checkoutAddressModal && checkoutAddressModal.classList.contains("show")) {
        hideCheckoutAddressModal();
    }
});
// ===== CLICK ADDRESS -> UPDATE CHECKOUT =====
document.querySelectorAll(".checkout-address-option__radio").forEach(radio => {
    radio.addEventListener("change", function () {
        const label = this.closest(".checkout-address-option");

        const name = label.dataset.name || "";
        const phone = label.dataset.phone || "";
        const address = label.dataset.address || "";
        const isDefault = label.dataset.default === "True" || label.dataset.default === "true";

        // update UI ngoài checkout
        const userEl = document.getElementById("checkoutUser");
        const addressEl = document.getElementById("checkoutAddress");
        const defaultEl = document.getElementById("checkoutDefault");

        if (userEl) {
            userEl.innerText = `${name} ${phone ? "(+84) " + phone : ""}`;
        }

        if (addressEl) {
            addressEl.innerText = address;
        }

        if (defaultEl) {
            if (isDefault) {
                defaultEl.style.display = "inline-flex";
            } else {
                defaultEl.style.display = "none";
            }
        }

        // đóng modal
        hideCheckoutAddressModal();
    });
});
// ===== CHECKOUT ADDRESS EDIT MODAL =====
const checkoutAddressEditModal = document.getElementById("checkoutAddressEditModal");
const checkoutAddressEditModalClose = document.getElementById("checkoutAddressEditModalClose");
const checkoutAddressEditBack = document.getElementById("checkoutAddressEditBack");
const checkoutAddressEditSubmit = document.getElementById("checkoutAddressEditSubmit");

const editAddressId = document.getElementById("editAddressId");
const editRecipientName = document.getElementById("editRecipientName");
const editPhone = document.getElementById("editPhone");
const editAddressLine = document.getElementById("editAddressLine");
const checkoutAddressEditError = document.getElementById("checkoutAddressEditError");
const editSetDefault = document.getElementById("editSetDefault");
const checkoutAddressEditDefaultLabel = document.getElementById("checkoutAddressEditDefaultLabel");

function showCheckoutAddressEditModal() {
    if (!checkoutAddressEditModal) return;
    checkoutAddressEditModal.classList.add("show");
    document.body.style.overflow = "hidden";
}

function hideCheckoutAddressEditModal() {
    if (!checkoutAddressEditModal) return;
    checkoutAddressEditModal.classList.remove("show");
    document.body.style.overflow = "";
    if (checkoutAddressEditError) {
        checkoutAddressEditError.classList.add("d-none");
        checkoutAddressEditError.textContent = "";
    }
}

document.querySelectorAll(".checkout-address-option__edit").forEach(btn => {
    btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        const isDefault = this.dataset.default === "True" || this.dataset.default === "true";

        if (editAddressId) editAddressId.value = this.dataset.id || "";
        if (editRecipientName) editRecipientName.value = this.dataset.name || "";
        if (editPhone) editPhone.value = this.dataset.phone || "";
        if (editAddressLine) editAddressLine.value = this.dataset.address || "";

        if (editSetDefault) {
            editSetDefault.checked = isDefault;
            editSetDefault.disabled = isDefault;
        }

        if (checkoutAddressEditDefaultLabel) {
            checkoutAddressEditDefaultLabel.classList.toggle("is-disabled", isDefault);

            if (isDefault) {
                checkoutAddressEditDefaultLabel.setAttribute(
                    "title",
                    "Bạn không thể đặt lại địa chỉ mặc định. Hãy đặt địa chỉ khác làm địa chỉ mặc định của bạn nhé."
                );
            } else {
                checkoutAddressEditDefaultLabel.removeAttribute("title");
            }
        }

        showCheckoutAddressEditModal();
    });
});

if (checkoutAddressEditModalClose) {
    checkoutAddressEditModalClose.addEventListener("click", hideCheckoutAddressEditModal);
}

if (checkoutAddressEditBack) {
    checkoutAddressEditBack.addEventListener("click", hideCheckoutAddressEditModal);
}

if (checkoutAddressEditModal) {
    checkoutAddressEditModal.addEventListener("click", function (e) {
        if (e.target.classList.contains("checkout-address-edit-modal__backdrop")) {
            hideCheckoutAddressEditModal();
        }
    });
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && checkoutAddressEditModal && checkoutAddressEditModal.classList.contains("show")) {
        hideCheckoutAddressEditModal();
    }
});

if (checkoutAddressEditSubmit) {
    checkoutAddressEditSubmit.addEventListener("click", async function () {
        const addressId = editAddressId?.value;
        const recipientName = editRecipientName?.value?.trim() || "";
        const phone = editPhone?.value?.trim() || "";
        const addressLine = editAddressLine?.value?.trim() || "";

        try {
            const res = await fetch(`/api/checkout/address/${addressId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
    recipient_name: recipientName,
    phone: phone,
    address_line: addressLine,
    set_as_default: editSetDefault ? editSetDefault.checked && !editSetDefault.disabled : false
})
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.message || "Không thể cập nhật địa chỉ");
            }

            const updated = data.address;

            const setAsDefaultNow = updated.is_default;

// reset toàn bộ default trong list nếu vừa đặt mặc định mới
if (setAsDefaultNow) {
    document.querySelectorAll(".checkout-address-option").forEach(option => {
        option.dataset.default = "false";

        const badge = option.querySelector(".checkout-address-option__badge");
        if (badge) {
            badge.remove();
        }
    });

    document.querySelectorAll(".checkout-address-option__edit").forEach(editBtn => {
        editBtn.dataset.default = "false";
    });
}

// update item tương ứng
document.querySelectorAll(".checkout-address-option").forEach(option => {
    const radio = option.querySelector(".checkout-address-option__radio");
    if (!radio) return;

    if (String(radio.value) === String(updated.id)) {
        option.dataset.name = updated.recipient_name;
        option.dataset.phone = updated.phone;
        option.dataset.address = updated.address_line;
        option.dataset.default = updated.is_default ? "true" : "false";

        const nameEl = option.querySelector(".checkout-address-option__name");
        const phoneEl = option.querySelector(".checkout-address-option__phone");
        const lineEl = option.querySelector(".checkout-address-option__line");

        if (nameEl) nameEl.textContent = updated.recipient_name;
        if (phoneEl) phoneEl.textContent = updated.phone ? `(+84) ${updated.phone}` : "";
        if (lineEl) lineEl.textContent = updated.address_line;

        if (setAsDefaultNow) {
            radio.checked = true;

            let badge = option.querySelector(".checkout-address-option__badge");
            if (!badge) {
                badge = document.createElement("span");
                badge.className = "checkout-address-option__badge";
                badge.textContent = "Mặc định";
                option.querySelector(".checkout-address-option__content")?.appendChild(badge);
            }
        }

        const editBtn = option.querySelector(".checkout-address-option__edit");
        if (editBtn) {
            editBtn.dataset.name = updated.recipient_name;
            editBtn.dataset.phone = updated.phone;
            editBtn.dataset.address = updated.address_line;
            editBtn.dataset.default = updated.is_default ? "true" : "false";
        }
    }
});

// update block ngoài nếu:
// 1) radio đang chọn sẵn
// 2) hoặc vừa đặt mặc định mới
document.querySelectorAll(".checkout-address-option").forEach(option => {
    const radio = option.querySelector(".checkout-address-option__radio");
    if (!radio) return;

    if (String(radio.value) === String(updated.id) && (radio.checked || setAsDefaultNow)) {
        const userEl = document.getElementById("checkoutUser");
        const addressEl = document.getElementById("checkoutAddress");
        const defaultEl = document.getElementById("checkoutDefault");

        if (userEl) {
            userEl.innerText = `${updated.recipient_name} ${updated.phone ? "(+84) " + updated.phone : ""}`;
        }

        if (addressEl) {
            addressEl.innerText = updated.address_line;
        }

        if (defaultEl) {
            defaultEl.style.display = "inline-flex";
        }
    }
});

            hideCheckoutAddressEditModal();
        } catch (err) {
            if (checkoutAddressEditError) {
                checkoutAddressEditError.textContent = err.message;
                checkoutAddressEditError.classList.remove("d-none");
            } else {
                alert(err.message);
            }
        }
    });
}
// ===== CHECKOUT PLACE ORDER =====
const checkoutPlaceOrderBtn = document.querySelector(".checkout-place-order-btn");

function getCheckoutCouponId() {
    const value = document.getElementById("checkoutCouponId")?.value || "";
    const couponId = parseInt(value, 10);
    return Number.isNaN(couponId) ? null : couponId;
}

function getCheckoutNotes() {
    const notes = {};

    document.querySelectorAll('input[id^="note_"]').forEach(input => {
        const productId = input.id.replace("note_", "").trim();
        if (productId) {
            notes[productId] = input.value.trim();
        }
    });

    return notes;
}

if (checkoutPlaceOrderBtn) {
    checkoutPlaceOrderBtn.addEventListener("click", async function () {
        const selectedProductIds = getCheckoutSelectedProductIds();
        const couponId = getCheckoutCouponId();
        const notes = getCheckoutNotes();

        if (!selectedProductIds.length) {
            alert("Không có sản phẩm nào để đặt hàng.");
            return;
        }

        this.disabled = true;

        try {
            const res = await fetch("/api/checkout/place-order", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    selected_product_ids: selectedProductIds,
                    coupon_id: couponId,
                    notes: notes
                })
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.message || "Không thể đặt hàng");
            }

            window.location.href = data.redirect_url || "/?order_success=1";
        } catch (err) {
            alert(err.message);
        } finally {
            this.disabled = false;
        }
    });
}
function showOrderSuccessToast() {
    const toast = document.getElementById("order-success-toast");
    if (!toast) return;

    toast.classList.add("show");

    clearTimeout(window.orderSuccessToastTimer);
    window.orderSuccessToastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 1600);
}

(function handleOrderSuccessFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const isSuccess = params.get("order_success");

    if (isSuccess === "1") {
        showOrderSuccessToast();

        params.delete("order_success");
        const newUrl = `${window.location.pathname}${params.toString() ? "?" + params.toString() : ""}${window.location.hash}`;
        window.history.replaceState({}, "", newUrl);
    }
})();
// ===== REBUY ORDER =====
document.querySelectorAll(".my-order-rebuy-btn").forEach(btn => {
    btn.addEventListener("click", async function (e) {
        e.preventDefault();

        const orderId = this.dataset.orderId;
        if (!orderId) return;

        this.classList.add("disabled");
        this.style.pointerEvents = "none";
        this.style.opacity = "0.65";

        try {
            const res = await fetch(`/api/orders/${orderId}/rebuy`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            const data = await res.json();

            if (!res.ok) {
                const warnings = Array.isArray(data.warning_messages)
                    ? data.warning_messages.filter(Boolean)
                    : [];

                const errorMessage = data.message || "Không thể mua lại đơn hàng";

                if (warnings.length) {
                    throw new Error(errorMessage + "\n- " + warnings.join("\n- "));
                }

                throw new Error(errorMessage);
            }

            const warnings = Array.isArray(data.warning_messages)
                ? data.warning_messages.filter(Boolean)
                : [];

            if (warnings.length) {
                alert(
                    (data.message || "Đã thêm sản phẩm vào giỏ hàng.") +
                    "\n\nLưu ý:\n- " + warnings.join("\n- ")
                );
            }

            window.location.href = data.redirect_url || "/cart";
        } catch (err) {
            alert(err.message);
        } finally {
            this.classList.remove("disabled");
            this.style.pointerEvents = "";
            this.style.opacity = "";
        }
    });
});
// ===== INDEX LOAD MORE PRODUCTS =====
const loadMoreBtn = document.getElementById("load-more-btn");
const productList = document.getElementById("product-list");
const loadMoreWrap = document.getElementById("load-more-wrap");

function bindRequireLoginButtons(scope = document) {
    scope.querySelectorAll(".require-login").forEach(btn => {
        if (btn.dataset.loginBound === "true") return;

        btn.dataset.loginBound = "true";
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            const modalEl = document.getElementById("loginRequiredModal");
            if (!modalEl) return;

            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        });
    });
}

function createProductCard(product) {
    const detailButton = product.requires_login
        ? `<a href="#" class="btn btn-outline-danger rounded-pill require-login">Xem chi tiết</a>`
        : `<a href="${product.detail_url}" class="btn btn-outline-danger rounded-pill">Xem chi tiết</a>`;

    return `
        <div class="col-sm-6 col-lg-4">
            <div class="card product-card h-100">
                <img
                    src="${product.image}"
                    class="product-image card-img-top"
                    alt="${product.name}"
                >

                <div class="card-body d-flex flex-column">
                    <h5 class="card-title fw-bold">${product.name}</h5>

                    <p class="card-text text-muted small">
                        ${product.description}
                    </p>

                    <div class="d-flex align-items-center gap-2 mb-3">
                        <span class="price-new">${product.price}</span>
                    </div>

                    <div class="d-grid mt-auto">
                        ${detailButton}
                    </div>
                </div>
            </div>
        </div>
    `;
}

if (loadMoreBtn && productList && loadMoreWrap) {
    let isLoadingMore = false;

    loadMoreBtn.addEventListener("click", async function () {
        if (isLoadingMore) return;

        const nextPage = parseInt(this.dataset.nextPage || "1", 10);
        if (!nextPage) return;

        isLoadingMore = true;
        this.disabled = true;
        this.textContent = "Đang tải...";

        try {
            const res = await fetch(`/api/products?page=${nextPage}`);
            const data = await res.json();

            if (!res.ok || !data.success) {
                throw new Error("Không thể tải thêm sản phẩm");
            }

            const html = (data.products || []).map(createProductCard).join("");
            productList.insertAdjacentHTML("beforeend", html);

            bindRequireLoginButtons(productList);

            if (data.has_next) {
                this.dataset.nextPage = data.current_page + 1;
                this.disabled = false;
                this.textContent = "Xem thêm";
            } else {
                loadMoreWrap.remove();
            }
        } catch (err) {
            this.disabled = false;
            this.textContent = "Xem thêm";
            alert(err.message || "Có lỗi xảy ra");
        } finally {
            isLoadingMore = false;
        }
    });
}
});