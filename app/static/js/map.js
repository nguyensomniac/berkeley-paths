(function($)  {
  $.getJSON('/paths_data')
  .then(function(data)  {
    data = JSON.parse(data);
    var mapbox = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    maxZoom: 18,
    id: 'nguyensomniac.cifa666x81xqwrxknp3rqodwu',
    accessToken: 'pk.eyJ1Ijoibmd1eWVuc29tbmlhYyIsImEiOiJjaWZhNjY4OXQxeHgyczRtNzZ4OTVnbHFuIn0.auDKPGYvamGNI0tCmG_6bw'
    });
    var map = L.map('map').addLayer(mapbox).setView([37.872, -122.263], 16);
    var drawLine = function(day) {
      _.each(day.days, function(d) {    
        var latLon = [];
        console.log(d);
        for (var i = 0; i < d.segments.length; i++)  {
          latLon.push([d.segments[i].place.location["lat"], d.segments[i].place.location["lon"]]);
        }
        // _.each(latLon, function(l) {
        //   L.circle(l, 10, {color: 'red'}).addTo(map);
        // })
        var polyline = L.polyline(latLon, {color: 'red'}).addTo(map);
      })
    }
    _.each(data, drawLine);
  })
})(jQuery);