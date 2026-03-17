(function () {
    const container = document.getElementById('orders-list-container');
    const userAutocompleteRoot = document.querySelector('[data-user-autocomplete]');

    function initUserAutocomplete(root) {
        if (!root) return;

        const input = root.querySelector('[data-user-autocomplete-input]');
        const hidden = root.querySelector('[data-user-autocomplete-hidden]');
        const token = root.querySelector('[data-user-autocomplete-token]');
        const tokenLabel = root.querySelector('[data-user-autocomplete-token-label]');
        const removeButton = root.querySelector('[data-user-autocomplete-remove]');
        const dropdown = root.querySelector('[data-user-autocomplete-dropdown]');
        const autocompleteUrl = root.dataset.autocompleteUrl;
        const defaultPlaceholder = input?.getAttribute('placeholder') || '';

        if (!input || !hidden || !token || !tokenLabel || !removeButton || !dropdown || !autocompleteUrl) return;

        let debounceTimer = null;
        let abortController = null;

        function closeDropdown() {
            dropdown.innerHTML = '';
            dropdown.hidden = true;
        }

        function hasSelectedUser() {
            return hidden.value.trim() !== '';
        }

        function renderSelectedState(label) {
            tokenLabel.textContent = label;
            token.hidden = false;
            input.value = '';
            input.placeholder = '';
            input.readOnly = true;
            input.setAttribute('aria-hidden', 'true');
            closeDropdown();
        }

        function renderEmptyState(keepFocus = false) {
            tokenLabel.textContent = '';
            token.hidden = true;
            input.readOnly = false;
            input.removeAttribute('aria-hidden');
            input.value = '';
            input.placeholder = defaultPlaceholder;
            closeDropdown();
            if (keepFocus) {
                input.focus();
            }
        }

        function clearSelection(keepFocus = false) {
            hidden.value = '';
            renderEmptyState(keepFocus);
        }

        function showResults(results) {
            dropdown.innerHTML = '';

            if (!results.length) {
                const empty = document.createElement('div');
                empty.className = 'user-autocomplete__empty';
                empty.textContent = 'Ничего не найдено';
                dropdown.appendChild(empty);
                dropdown.hidden = false;
                return;
            }

            const list = document.createElement('div');
            list.className = 'user-autocomplete__list';

            results.forEach((item) => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'user-autocomplete__item';
                button.textContent = item.label;
                button.addEventListener('click', () => {
                    hidden.value = String(item.id);
                    renderSelectedState(item.label);
                });
                list.appendChild(button);
            });

            dropdown.appendChild(list);
            dropdown.hidden = false;
        }

        async function fetchUsers(query) {
            if (abortController) {
                abortController.abort();
            }

            abortController = new AbortController();

            const url = new URL(autocompleteUrl, window.location.origin);
            url.searchParams.set('q', query);

            const response = await fetch(url.toString(), {
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                signal: abortController.signal,
            });

            if (!response.ok) {
                closeDropdown();
                return;
            }

            const payload = await response.json();
            showResults(Array.isArray(payload.results) ? payload.results : []);
        }

        input.addEventListener('input', () => {
            if (hasSelectedUser()) {
                return;
            }

            const query = input.value.trim();

            if (debounceTimer) {
                window.clearTimeout(debounceTimer);
            }

            if (query.length < 2) {
                closeDropdown();
                return;
            }

            debounceTimer = window.setTimeout(() => {
                fetchUsers(query).catch((error) => {
                    if (error?.name !== 'AbortError') {
                        closeDropdown();
                    }
                });
            }, 250);
        });

        input.addEventListener('focus', () => {
            if (hasSelectedUser()) {
                closeDropdown();
                return;
            }

            if (input.value.trim().length >= 2) {
                fetchUsers(input.value.trim()).catch(() => closeDropdown());
            }
        });

        removeButton.addEventListener('click', () => {
            clearSelection(true);
        });

        input.addEventListener('keydown', (event) => {
            if (event.key !== 'Backspace' || !hasSelectedUser()) {
                return;
            }

            if (input.selectionStart === 0 && input.selectionEnd === 0 && input.value.length === 0) {
                event.preventDefault();
                clearSelection(true);
            }
        });

        document.addEventListener('click', (event) => {
            if (!root.contains(event.target)) {
                closeDropdown();
            }
        });

        if (hasSelectedUser()) {
            renderSelectedState(tokenLabel.textContent.trim());
        } else {
            renderEmptyState();
        }
    }

    if (userAutocompleteRoot) {
        initUserAutocomplete(userAutocompleteRoot);
    }

    if (!container) return;

    let nextPage = container.querySelector('[data-next-page]')?.dataset.nextPage || '';
    let isLoading = false;

    async function loadNext() {
        if (!nextPage || isLoading) return;
        isLoading = true;

        try {
            const response = await fetch(nextPage, {headers: {'X-Requested-With': 'XMLHttpRequest'}});
            if (!response.ok) return;

            const html = await response.text();
            const tmp = document.createElement('div');
            tmp.innerHTML = html;

            const incomingList = tmp.querySelector('[data-order-items-root]');
            const currentList = container.querySelector('[data-order-items-root]');
            if (incomingList && currentList) {
                currentList.insertAdjacentHTML('beforeend', incomingList.innerHTML);
            }

            const incomingNext = tmp.querySelector('[data-next-page]');
            const currentNext = container.querySelector('[data-next-page]');
            if (currentNext) currentNext.remove();

            if (incomingNext) {
                container.appendChild(incomingNext);
                nextPage = incomingNext.dataset.nextPage || '';
            } else {
                nextPage = '';
            }
        } finally {
            isLoading = false;
        }
    }

    window.addEventListener('scroll', () => {
        if (!nextPage) return;
        const nearBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 300;
        if (nearBottom) {
            loadNext();
        }
    });
})();
