/* ==============================
   ACCOUNT DROPDOWN
============================== */

function toggleAccountMenu() {

    const dropdown = document.getElementById("accountDropdown");

    if (dropdown) {
        dropdown.classList.toggle("show");
    }
}


/* ==============================
   CLOSE DROPDOWN
   WHEN CLICKING OUTSIDE
============================== */

document.addEventListener("click", function (event) {

    const accountMenu = document.querySelector(".account-menu");
    const dropdown = document.getElementById("accountDropdown");

    if (!accountMenu || !dropdown) {
        return;
    }

    if (!accountMenu.contains(event.target)) {
        dropdown.classList.remove("show");
    }

});


/* ==============================
   APPLIANCE CHART
============================== */

document.addEventListener("DOMContentLoaded", function () {

    const chartCanvas = document.getElementById("applianceChart");

    if (!chartCanvas) {
        return;
    }


    /*
        Appliance data index.html se
        data attributes ke through milega.
    */

    const applianceDataElement =
        document.getElementById("applianceData");


    if (!applianceDataElement) {
        return;
    }


    let applianceData = [];


    try {

        applianceData =
            JSON.parse(
                applianceDataElement.textContent
            );

    } catch (error) {

        console.error(
            "Unable to read appliance data:",
            error
        );

        return;
    }


    /* ==============================
       NO APPLIANCES
    ============================== */

    if (applianceData.length === 0) {

        const parent = chartCanvas.parentElement;

        chartCanvas.style.display = "none";


        const message = document.createElement("p");

        message.textContent =
            "No appliances added yet. Add an appliance to see consumption.";


        message.style.color = "#aab8d0";

        message.style.textAlign = "center";

        message.style.padding = "40px 10px";


        parent.appendChild(message);

        return;
    }


    /* ==============================
       GET CHART DATA
    ============================== */

    const applianceNames =
        applianceData.map(function (appliance) {

            return appliance.name;

        });


    const applianceUsage =
        applianceData.map(function (appliance) {

            return appliance.usage;

        });


    /* ==============================
       CREATE CHART
    ============================== */

    new Chart(chartCanvas, {

        type: "bar",


        data: {

            labels: applianceNames,


            datasets: [

                {

                    label:
                        "Energy Consumption (kWh/day)",


                    data:
                        applianceUsage,


                    backgroundColor:
                        "rgba(0, 212, 255, 0.65)",


                    borderColor:
                        "#00d4ff",


                    borderWidth: 1,


                    borderRadius: 8

                }

            ]

        },


        options: {

            responsive: true,

            maintainAspectRatio: false,


            plugins: {

                legend: {

                    labels: {

                        color: "#ffffff"

                    }

                }

            },


            scales: {

                x: {

                    ticks: {

                        color: "#aab8d0"

                    },


                    grid: {

                        color:
                            "rgba(255,255,255,0.05)"

                    }

                },


                y: {

                    beginAtZero: true,


                    ticks: {

                        color: "#aab8d0"

                    },


                    grid: {

                        color:
                            "rgba(255,255,255,0.05)"

                    },


                    title: {

                        display: true,

                        text: "kWh/day",

                        color: "#aab8d0"

                    }

                }

            }

        }

    });

});


/* ==============================
   SMOOTH NAVIGATION
============================== */

document
    .querySelectorAll(".nav-links a")
    .forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                const target =
                    this.getAttribute("href");


                if (
                    target &&
                    target.startsWith("#")
                ) {

                    const section =
                        document.querySelector(target);


                    if (section) {

                        section.scrollIntoView({

                            behavior: "smooth"

                        });

                    }

                }

            }
        );

    });


/* ==============================
   SAVE ENERGY BUTTON
============================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const energyForm =
            document.querySelector(".energy-form");


        const saveButton =
            document.querySelector(".save-energy-btn");


        if (!energyForm || !saveButton) {
            return;
        }


        energyForm.addEventListener(
            "submit",
            function () {

                saveButton.textContent =
                    "Saving...";


                saveButton.disabled = true;

            }
        );

    }
);
/* =========================
   PASSWORD SHOW / HIDE
========================= */

function togglePassword(inputId, button) {

    const passwordInput = document.getElementById(inputId);

    if (!passwordInput) {
        return;
    }

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        button.textContent = "🙈";

    } else {

        passwordInput.type = "password";

        button.textContent = "👁";

    }
}