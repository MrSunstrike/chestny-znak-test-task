(function () {
    const volumeField = document.getElementById('id_volume_type');
    const quantityWrap = document.getElementById('field-quantity-wrap');
    const descriptionWrap = document.getElementById('field-description-wrap');
    const documentWrap = document.getElementById('field-document-wrap');

    if (!volumeField) return;

    function setVisible(element, visible) {
        if (!element) return;
        element.hidden = !visible;
    }

    function updateByVolumeType() {
        const value = volumeField.value;
        const isSingle = value === 'single';
        const isMultiple = value === 'multiple';

        setVisible(descriptionWrap, isSingle);
        setVisible(quantityWrap, isMultiple);
        setVisible(documentWrap, isMultiple);
    }

    volumeField.addEventListener('change', updateByVolumeType);
    updateByVolumeType();
})();
