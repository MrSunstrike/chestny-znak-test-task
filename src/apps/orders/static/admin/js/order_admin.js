(function () {
    "use strict";

    function updateFieldsVisibility() {
        const volumeTypeField = document.getElementById("id_volume_type");
        const descriptionField = document.getElementById("id_description");
        const documentField = document.getElementById("id_document");
        const quantityField = document.getElementById("id_quantity");

        if (!volumeTypeField) {
            return;
        }

        const isSingle = volumeTypeField.value === "single";

        if (descriptionField) {
            const descriptionRow = descriptionField.closest(".form-row");
            if (descriptionRow) {
                descriptionRow.style.display = isSingle ? "" : "none";
            }
        }

        const isMultiple = volumeTypeField.value === "multiple";

        if (documentField) {
            const documentRow = documentField.closest(".form-row");
            if (documentRow) {
                documentRow.style.display = isMultiple ? "" : "none";
            }
        }

        if (quantityField) {
            const quantityRow = quantityField.closest(".form-row");
            if (quantityRow) {
                quantityRow.style.display = isMultiple ? "" : "none";
            }
        }
    }

    function init() {
        const volumeTypeField = document.getElementById("id_volume_type");
        if (!volumeTypeField) return;
        updateFieldsVisibility();
        volumeTypeField.addEventListener("change", updateFieldsVisibility);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();