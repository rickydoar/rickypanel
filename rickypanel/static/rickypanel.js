//very very simplified js lib
var Rickypanel = function(token) {
  this.token = token;
}

Rickypanel.prototype.track = function(event, params) {
  console.log(params)
  var url_params = {
    "event":event
  }
  $.extend(url_params, {
    'token':this.token,
    'prop1':params.prop1,
    'prop2':params.prop2,
    'prop3':params.prop3,
    'os':get_os()
  })
  var url_string = ""
  _.each(url_params, function(value, name){
    url_string += "&" + name + "=" + value
  });
  return $.ajax({
    url: "http://127.0.0.1:8000/track/?" + url_string,
    type: 'GET',
    dataType: 'json',
    contentType: 'application/json',
  })
} 

function get_os(){
  var OSName = "Unknown"
  if (navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
  if (navigator.appVersion.indexOf("Mac")!=-1) OSName="MacOS";
  if (navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
  if (navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";
  return OSName
}

function initRickyPanel(token){
  rickypanel = new Rickypanel(token)
}