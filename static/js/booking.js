// Loads available slots via AJAX when the user picks a date.
document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const slotsBox = document.getElementById('slots');
    if (!dateInput || !slotsBox) return;

    const apiUrl = slotsBox.dataset.apiUrl;
    const confirmUrl = slotsBox.dataset.confirmUrl;
    const loadingText = slotsBox.dataset.loadingText || 'Loading…';
    const noSlotsText = slotsBox.dataset.noSlotsText || 'No available slots on that day.';
    const errorText = slotsBox.dataset.errorText || 'Could not load slots. Try again.';

    async function loadSlots() {
        const date = dateInput.value;
        if (!date) return;
        slotsBox.innerHTML = `<p class="muted">${loadingText}</p>`;
        try {
            const url = `${apiUrl}&date=${encodeURIComponent(date)}`;
            const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
            if (!res.ok) throw new Error(`Status ${res.status}`);
            const data = await res.json();
            renderSlots(data.slots || [], date);
        } catch (err) {
            slotsBox.innerHTML = `<p class="error-text">${errorText}</p>`;
        }
    }

    function renderSlots(slots, date) {
        if (slots.length === 0) {
            slotsBox.innerHTML = `<p class="muted">${noSlotsText}</p>`;
            return;
        }
        slotsBox.innerHTML = '';
        for (const time of slots) {
            const link = document.createElement('a');
            link.className = 'slot-button';
            link.textContent = time;
            const qs = new URLSearchParams({ date, time }).toString();
            link.href = `${confirmUrl}?${qs}`;
            slotsBox.appendChild(link);
        }
    }

    dateInput.addEventListener('change', loadSlots);
    loadSlots();
});
