/**
 * Shared front-end behaviour for CarePulse.
 * Kept dependency-free (vanilla JS) so it works without a build step.
 */
(function () {
    // -- Auto-dismiss alerts after a few seconds -----------------------
    document.querySelectorAll(".cp-alert").forEach(function (alertEl) {
        setTimeout(function () {
            const alertInstance = bootstrap.Alert.getOrCreateInstance(alertEl);
            alertInstance.close();
        }, 6000);
    });

    // -- Appointment booking: fetch live slots when doctor/date change --
    const doctorField = document.querySelector("#id_doctor");
    const dateField = document.querySelector("#id_scheduled_date");
    const timeField = document.querySelector("#id_scheduled_time");
    const slotsEndpoint = document.body.dataset.slotsUrl;

    function refreshSlots() {
        if (!doctorField || !dateField || !timeField || !slotsEndpoint) return;
        const doctorId = doctorField.value;
        const date = dateField.value;
        if (!doctorId || !date) return;

        timeField.innerHTML = '<option>Loading...</option>';
        fetch(`${slotsEndpoint}?doctor=${encodeURIComponent(doctorId)}&date=${encodeURIComponent(date)}`)
            .then((response) => response.json())
            .then((data) => {
                timeField.innerHTML = "";
                if (!data.slots || data.slots.length === 0) {
                    timeField.innerHTML = '<option value="">No slots available</option>';
                    return;
                }
                data.slots.forEach(function (slot) {
                    const option = document.createElement("option");
                    option.value = slot.value;
                    option.textContent = slot.label;
                    timeField.appendChild(option);
                });
            })
            .catch(() => {
                timeField.innerHTML = '<option value="">Could not load slots</option>';
            });
    }

    doctorField?.addEventListener("change", refreshSlots);
    dateField?.addEventListener("change", refreshSlots);
    if (doctorField && dateField && doctorField.value && dateField.value) {
        refreshSlots();
    }

    // -- Department filter narrows the doctor dropdown on the booking form --
    const departmentField = document.querySelector("#id_department");
    if (departmentField && doctorField) {
        const allOptions = Array.from(doctorField.options);
        function filterDoctorsByDepartment() {
            const departmentId = departmentField.value;
            doctorField.innerHTML = "";
            allOptions.forEach(function (option) {
                if (!departmentId || option.dataset.department === departmentId || !option.value) {
                    doctorField.appendChild(option.cloneNode(true));
                }
            });
        }
        departmentField.addEventListener("change", filterDoctorsByDepartment);
    }

    // -- Symptom chip visual toggle (checkbox styling fallback) --------
    document.querySelectorAll(".cp-symptom-chip input[type=checkbox]").forEach(function (box) {
        box.addEventListener("change", function () {
            box.closest(".cp-symptom-chip")?.classList.toggle("cp-symptom-chip-active", box.checked);
        });
    });
})();
