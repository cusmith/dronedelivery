var map = null;
var markers = [];

function initalizeMap() {
	map = new google.maps.Map(document.getElementById('map'),{
		backgroundColor: '#ffffff',
		mapTypeId: 'terrain',
		mapTypeControl: false,
		streetViewControl: false,
		center: {lat: 48.427580, lng: -123.364456},
		scrollwheel: true,
		zoom: 12,
		styles: [
			{
				featureType: 'all',
				stylers: [
					{ saturation: -100 }
				]
			},{
				featureType: 'water',
				stylers: [
					{ color: '#ffffff' }
				]
			},{
				featureType: 'poi.business',
				elementType: 'labels',
				stylers: [
					{ visibility: 'off' }
				]
			}
		]
	});

	update();
	setInterval(update,15000);
}

function strToLatLng(str) {
	var arr = str.split(',');
	return {'lat' : parseFloat(arr[0]),'lng' : parseFloat(arr[1])};
}

function update() {
	$.ajax({
		'url' : '',
		'dataType' : 'json',
		'data' : {
			'action' : 'update',
			'invoice' : invoice_id
		},
		'success' : function(drones) {

			drones.forEach(function(drone) {
				var hasMarker = false;
				markers.forEach(function(marker) {
					if (drone.id == marker.drone_id) {
						hasMarker = true;
						marker.position = strToLatLng(drone.location);
					}
				});
				if (!hasMarker) {
					markers.push(new google.maps.Marker({
						'map' : map,
						'position' : strToLatLng(drone.location),
						'title' : ('drone ' + drone.id)
					}));
				}
				$('#status').text(drone.status); // TODO: handle multiple drone statuses
			});
		}
	});
}

$(document).ready(function() {
	var url = 'http://maps.googleapis.com/maps/api/js?key=' +
			  getMapsAPIKey() +
			  '&callback=initalizeMap';

	var mapScript = document.createElement('script');
	$(mapScript).attr('type','text/javascript');
	$(mapScript).attr('src',url);
	$(document.body).append(mapScript);
});