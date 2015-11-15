(function($)  {
  $.getJSON('/storyline')
  .then(function(data)  {
    var mapbox = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    maxZoom: 18,
    id: 'nguyensomniac.6e535727',
    accessToken: 'pk.eyJ1Ijoibmd1eWVuc29tbmlhYyIsImEiOiJjaWZhNjY4OXQxeHgyczRtNzZ4OTVnbHFuIn0.auDKPGYvamGNI0tCmG_6bw'
    });
    var map = L.map('map').addLayer(mapbox).setView([37.871929, -122.257794], 15);
    var drawPlace = function (place)  {
      var latLon = [place.location.lat, place.location.lon];
      L.circle(latLon, 10, {color: 'red'}).addTo(map);
    }
    var drawMovement = function(move) {
      var latLon = [];
      for (var i = 0; i < move.trackPoints.length; i++) {
        latLon.push([move.trackPoints[i].lat, move.trackPoints[i].lon]);
      }
      L.polyline(latLon, {color: 'red'}).addTo(map);
    }
    var drawLine = function(day) {
      _.each(day.segments, function(seg) {
        if (seg.type == 'place')  {
          drawPlace(seg.place);
        }
        else if (seg.type == 'move')  {
          drawMovement(seg.activities[0]);
        }
      })
    }
    for (var i = 0; i < Object.keys(data).length; i++)  {
      console.log(Object.keys(data))
      drawLine(data[Object.keys(data)[i]])
    }
  })
})(jQuery);