app.directive('pathsMap', function($http) {
  //November 2 is a Monday. The date itself doesn't matter, just the weekday.
  // Months in Moment.js are zero-indexed, so November = 10
  var currentTime = moment(new Date(2015, 10, 2));
  currentTime.tz('America/Los_Angeles');
  var WEEK = currentTime.week();
  var INTERVAL = 2;
  currentTime.hour(13);
  currentTime.minute(50);
  var days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  var RADIUS = 6;
  var WEEK_TO_MILLISECONDS = 604800000;

  //Returns an object where the keys are the number of minutes elapsed
  // and the values are a person's position.
  var createData = function(person) {
    var t = moment(new Date(2015, 10, 1));
    t.tz('America/Los_Angeles');
    var newData = {};
    var currentDay = t.day();
    var week = t.week();
    var currentSegment = 0;
    var incrementSegment = function() {
      if (currentSegment == person.days[days[currentDay]].segments.length - 1)  {
        currentDay += 1;
        currentSegment = 0;
      }
      else  {
        currentSegment += 1;
      }
    };
    if (person.days == undefined)  {
      return;
    }
    var incrementMinute = function()  {
      t.add(INTERVAL, 'minutes');
    }
    while (currentDay < 7 && t.week() == week) {
      // If no data for the current day, go to next day
      if (person.days[days[currentDay]] == undefined || person.days[days[currentDay]].segments.length == 0) {
        currentDay+= 1;
        t.day(t.day() + 1);
        continue;
      }
      var segs = person.days[days[currentDay]].segments;
      // Moves start times for move activities start at the day they're mapped to. If an activity starts
      // the week before, the seconds will wrap around, which is no bueno.
      var start = (segs[currentSegment].type == "move")
        ? segs[currentSegment].activities[0].startTime : segs[currentSegment].startTime;
      var end = (segs[currentSegment].type == "move")
        ? segs[currentSegment].activities[0].endTime : segs[currentSegment].endTime;
      // Place markers don't have the same granularity - they'll start the week before if they want.
      // I'm not dealing with that noise.
      if (segs[currentSegment].type == "place" && convertMovesTime(start).week() != convertMovesTime(end).week()) {
        incrementSegment();
        continue;
      }
      // Make sure that the specified time is in between the current segment's start time and end time.
      // If current time is before start time, add more time. If after end time, update segment.
      if (minsOfWeek(t) < minsOfWeek(convertMovesTime(start)))  {
        incrementMinute();
        continue;
      }
      else if (minsOfWeek(t) > minsOfWeek(convertMovesTime(end))) {
        incrementSegment();
        continue;
      }
      // If the current segment is a place segment, just copy the location
      else  {
        
        if (segs[currentSegment].type == "place") {
          newData[minsOfWeek(t)] = formatPlaceLocation(segs[currentSegment]);
          incrementMinute();
        }
        // If the current segment is a move segment, run through the track points,
        // approximating a position until the track points are exhausted.
        else if (segs[currentSegment].type == "move") {
          var tracked = 0;
          var trackPoints = segs[currentSegment].activities[0].trackPoints;
          while (tracked < trackPoints.length && t.week() == week) {
            if (minsOfWeek(convertMovesTime(trackPoints[tracked].time)) <= minsOfWeek(t)) {
              var beforePt = trackPoints[tracked];
              if (tracked != trackPoints.length - 1)  {
                var afterPt = trackPoints[tracked + 1];
                if (minsOfWeek(convertMovesTime(afterPt.time)) > minsOfWeek(t)) {
                  var interpolator = d3.interpolateObject(beforePt, afterPt);
                  newData[minsOfWeek(t)] = interpolator(
                    momentPercentage(convertMovesTime(beforePt.time), convertMovesTime(afterPt.time), t));
                  incrementMinute();
                } else  {
                  tracked++;
                }
              } else  {
                var entry = {
                  lat: beforePt.lat,
                  lon: beforePt.lon
                };
                newData[minsOfWeek(t)] = entry;
                tracked++;
              }
            } else  {
              t.minute(t.minute() + 2);
            }
          }
          incrementSegment();
        }
      }
    }
    return newData;
  }
  var convertMovesTime = function(d) {
    return moment(d, "YYYYMMDDTHHmmssZ");
  }

  var minsOfWeek = function(momnt)  {
    return momnt.day() * 1440 + minsOfDay(momnt);
  }

  var minsOfDay = function(momnt)  {
    return momnt.minutes() + momnt.hours() * 60;
  }

  var secsOfDay = function(momnt) {
    return momnt.seconds() + minsOfDay(momnt) * 60;
  }

  var momentPercentage = function(a, b, c)  {
    if (secsOfDay(a) == secsOfDay(b)) {
      return 0;
    }
    return (secsOfDay(b) - secsOfDay(c)) / (secsOfDay(b) - secsOfDay(a));
  }

  var formatPlaceLocation = function(p)  {
    return  {
      lat: p.place.location.lat,
      lon: p.place.location.lon
    }
  }

  return  {
    //templateUrl: '/static/partials/map.html',
    link: function(scope, element)  {
      var mapbox = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
          maxZoom: 18,
          id: 'nguyensomniac.6e535727',
          accessToken: 'pk.eyJ1Ijoibmd1eWVuc29tbmlhYyIsImEiOiJjaWZhNjY4OXQxeHgyczRtNzZ4OTVnbHFuIn0.auDKPGYvamGNI0tCmG_6bw'
        });
      var map = L.map(element[0], {
        dragging: false,
        touchZoom: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        boxZoom: false,
        tap: false,
        worldCopyJump: false,
        zoomControl: false,
        attributionControl: false
      }).addLayer(mapbox).setView([37.871929, -122.257794], 15);
      var svg = d3.select(map.getPanes().overlayPane).append('svg');
      var g = svg.append('g');
      var text = g.append('text');
      $http.get('/paths_all').then(function(res)  {
        scope.data = JSON.parse(res.data);
        for(var i = 0, l = scope.data.length; i < l; i++) {
          scope.data[i]["newData"] = createData(scope.data[i]);
        }
        var update = function() {
          var updateData = function() {
            var d = [];
              for (var i = 0, l = scope.data.length; i < l; i++)  {
                var dayData;
                if (scope.data[i].newData == null)  {
                  dayData = null;
                } else  {
                  dayData = scope.data[i]["newData"][minsOfWeek(currentTime)];
                }
                if (dayData != null)  {
                  person = map.latLngToLayerPoint(new L.LatLng(dayData.lat, dayData.lon));
                  person.id = scope.data[i]._id.$oid;
                  d.push(person);
                }
              }
              return d;
          }
          var data = updateData();
          currentTime.minute(currentTime.minute() + 2);
          var circle = g.selectAll('circle.dot')
            .data(data, function(d) {
              return d.id;
            });
          circle.enter()
            .append('circle')
            .attr('r', 0)
            .transition()
            .duration(200)
            .attr('r', RADIUS);
          circle.attr('class', 'dot')
            .attr('r', RADIUS)
            .transition(100)
            .attr('cx', function(d) {
              return d.x;
            })
            .attr('cy', function(d) {
              return d.y;
            });
          circle.exit()
            .transition()
            .duration(200)
            .attr('r', 0).remove();
          text.text(function()  {
              return currentTime.hour() + ':' + currentTime.minutes();
            })
            .attr('x', 300)
            .attr('y', 50);
        }
        setInterval(update, 100);
      });
    }
  }
})
