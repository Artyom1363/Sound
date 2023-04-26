let regionsCounts = 0;
var markersHistory = [];
var markersStore = new Map();

function initRegions(filePath) {
    fetch(fileServerAPI + filePath).then(async response => {
        var regs = JSON.parse(await response.text())
        regionsCounts = 0;
        markersHistory.length = 0;
        markersStore.length = 0;
        for (region of regs) {
            wavesurfer.addRegion({
                id: `${regionsCounts}`,
                start: region.Start,
                end: region.End,
                loop: false,
                color: getRegionColorByType(region.Type)
            });
            onRegionCreate(wavesurfer.regions.list[`${regionsCounts}`], false);
            regionsCounts++;
        }
    }).catch(err => {
        alert(err)
    })
}

var addBadMarkerBtn = document.getElementById('marker-add-bad')
var addParasiteMarkerBtn = document.getElementById('marker-add-parasite')
var trashcanBtn = document.getElementById('trashcan')
var cancelBtn = document.getElementById('cancel')

addParasiteMarkerBtn.onclick = function () {
    wavesurfer.addRegion({
        id: `${regionsCounts}`,
        start: 0,
        end: 0.5,
        loop: false,
        color: getRegionColorByType("parasite")
    });
    onRegionCreate(wavesurfer.regions.list[`${regionsCounts}`]);
    regionsCounts++;
}

addBadMarkerBtn.onclick = function () {
    wavesurfer.addRegion({
        id: `${regionsCounts}`,
        start: 0,
        end: 0.5,
        loop: false,
        color: getRegionColorByType("bad")
    });
    onRegionCreate(wavesurfer.regions.list[`${regionsCounts}`]);
    regionsCounts++;
}


function getRegionColorByType(type) {
    switch (type){
        case "bad":
            return 'hsla(0, 100%, 50%, 0.4)'
        case "parasite":
            return 'hsla(50, 100%, 50%, 0.4)'
        case "mezdo":
            return 'hsla(169, 0%, 50%, 0.4)'
    }
}

function getRegionTypeByColor(color) {
    switch (color){
        case "hsla(0, 100%, 50%, 0.4)":
            return "bad"
        case "hsla(50, 100%, 50%, 0.4)":
            return "parasite"
        case "hsla(169, 0%, 50%, 0.4)":
            return "mezdo"
    }
}

trashcanBtn.onclick = function () {
    if (trashcanBtn.classList.contains('active')) {
        trashcanBtn.classList.remove('active');
    } else {
        trashcanBtn.classList.add('active');
    }
}

wavesurfer.on('region-click', function (region, e) {
    // Play on click, loop on shift click
    // await new Promise(r => setTimeout(r, 100));
    if (trashcanBtn.classList.contains('active')){
        onRegionRemove(region);
        region.remove();
    } else {
        if (e.ctrlKey) {
            e.stopPropagation();
            region.play();
        }
    }
});



function markersHistoryAdd(region) {

}

cancelBtn.onclick = function () {
    let lastElement = markersHistory.pop()
    switch (lastElement.action) {
        case 'create':
            wavesurfer.regions.list[lastElement.region.id].remove();
            break;
        case 'remove':
            wavesurfer.addRegion({
                id: lastElement.region.id,
                start: lastElement.region.start,
                end: lastElement.region.end,
                loop: false,
                color: lastElement.region.color
            });
            break;
        case 'update':
            wavesurfer.regions.list[lastElement.region.id].start = lastElement.region.start
            wavesurfer.regions.list[lastElement.region.id].end = lastElement.region.end
            wavesurfer.regions.list[lastElement.region.id].onDrag(0);
            break;
    }
}

function onRegionCreate(region, isAction=true){
    if (isAction) {
        markersHistory.push({
            action: "create",
            region: region,
        })
    }
    markersStore.set(region.id, {
        id: region.id,
        start: region.start,
        end: region.end,
    })
}

function onRegionRemove(region){
    markersHistory.push({
        action: "remove",
        region: region,
    })
}

wavesurfer.on('region-update-end', function (region, e) {
    markersHistory.push({
        action: "update",
        region: markersStore.get(region.id),
    })
    markersStore.set(region.id, {
        id: region.id,
        start: region.start,
        end: region.end,
    })
});




