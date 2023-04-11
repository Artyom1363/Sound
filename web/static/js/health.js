let healthCircleParasite = document.getElementById('health-api-parasite');
let healthCircleTranscribe = document.getElementById('health-api-transcribe');
let healthCircleMezdo = document.getElementById('health-api-mezdo');

let healthItems = [{
        indicator: healthCircleParasite,
        api: healthParasiteAPI,
    },
    {
        indicator: healthCircleTranscribe,
        api: healthTranscribeAPI,
    },
    {
        indicator: healthCircleMezdo,
        api: healthMezdoAPI,
    },
]

function healthChecker() {
    for (const item of healthItems) {
        fetch(item.api).then(async response => {
            let respText = await response.text()
            switch (respText) {
                case "success":
                    item.indicator.style.color = 'green';
                    break;
                case "not ready":
                    item.indicator.style.color = 'yellow';
                    break;
                case "unavailable":
                    item.indicator.style.color = 'red';
                    break;
            }
        }).catch(err => {
            item.indicator.style.color = 'black';
        })
    }
    setTimeout(healthChecker, 5000);
}
healthChecker();
