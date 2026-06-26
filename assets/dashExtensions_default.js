window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const marker = L.circleMarker(latlng);

            const props = feature.properties;

            const content = `
        <b>${props.lb_nom}</b>
        <br>${props.observers}</br>
        <a href="https://atlas.mercantour.eu/espece/${props.cd_ref}" target='_blank'>Voir la fiche de l'espece</a>
    `;

            marker.bindPopup(content);
            return marker;
        }

    }
});