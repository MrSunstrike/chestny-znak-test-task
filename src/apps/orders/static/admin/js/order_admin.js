(function () {
    function getFieldRow(fieldName) {
        return document.querySelector(".form-row.field-" + fieldName + ", .field-" + fieldName);
    }

    function setVisible(row, isVisible) {
        if (!row) {
            return;
        }

        row.style.display = isVisible ? "" : "none";

        row.querySelectorAll("input, select, textarea").forEach(function (input) {
            input.disabled = !isVisible;
        });
    }

    function updateVolumeFields() {
        var volumeTypeElement = document.getElementById("id_volume_type");
        if (!volumeTypeElement) {
            return;
        }

        var volumeType = volumeTypeElement.value;
        var descriptionRow = getFieldRow("description");
        var documentRow = getFieldRow("document");
        var quantityRow = getFieldRow("quantity");

        setVisible(descriptionRow, false);
        setVisible(documentRow, false);
        setVisible(quantityRow, false);

        if (volumeType === "single") {
            setVisible(descriptionRow, true);
            return;
        }

        if (volumeType === "multiple") {
            setVisible(documentRow, true);
            setVisible(quantityRow, true);
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        var volumeTypeElement = document.getElementById("id_volume_type");
        if (!volumeTypeElement) {
            return;
        }

        updateVolumeFields();
        volumeTypeElement.addEventListener("change", updateVolumeFields);
    });
})();
