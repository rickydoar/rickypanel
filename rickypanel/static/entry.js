import { Component } from 'panel';

import reportTemplate from './report.jade';
import queryTemplate from './query.jade';
import chartTemplate from './chart.jade';

import dateTemplate from './date.jade'
// import chartTypeTemplate from './chart_type.jade'
import projectDropdownTemplate from './project_dropdown.jade'
import eventDropdownTemplate from './event_dropdown.jade'
import propertyDropdownTemplate from './property_dropdown.jade'

document.registerElement('report-app', class ReportApp extends Component {
  get config() {
    return {
      template:reportTemplate,
    };
  }
});

document.registerElement('query-builder', class queryBuilder extends Component {
  get config() {
    return {
      template:queryTemplate,
    };
  }
});

document.registerElement('chart-body', class chartBody extends Component {
  get config() {
    return {
      template:chartTemplate,
    };
  }
});

document.registerElement('project-dropdown', class projectDropdown extends Component {
  get config() {
    return {
      helpers: {
        project_change: () => this.change_project(),
      },

      template:projectDropdownTemplate,
    };
  }

  attachedCallback() {
    super.attachedCallback();
    $('#projectOptions').select2();
    $('#projectOptions').find('option').remove()
    _.each(projects, function(keys, project_name){
      $('<option api_key="'+ keys.api_key +'" api_secret="'+ keys.api_secret +'">'+project_name+'</option>').appendTo('#projectOptions');
    })
    this.update({api_key:$("#projectOptions option:selected").attr('api_key'), 
    api_secret:$("#projectOptions option:selected").attr('api_secret')})
    populate_events(this)
  }

  change_project() {
    var api_key = $( "#projectOptions option:selected" ).attr('api_key');
    var api_secret = $( "#projectOptions option:selected" ).attr('api_secret')
    this.update({api_key: api_key, api_secret:api_secret});
    populate_events(this)
  }
});

document.registerElement('event-dropdown', class eventDropdown extends Component {
  get config() {
    return {
      helpers: {
        eventChange: () => this.changeEvent(),
      },

      template:eventDropdownTemplate,
    };
  }

  attachedCallback() {
    super.attachedCallback();
    $('#eventOptions').select2();
  }

  changeEvent() {
    var event_name = $( "#eventOptions option:selected" ).val();
    this.update({event: event_name});
    updateChart(this.state)
  }
});

document.registerElement('property-dropdown', class propertyDropdown extends Component {
  get config() {
    return {
      helpers: {
        propChange: () => this.changeProperty(),
      },

      template:propertyDropdownTemplate,
    };
  }

  attachedCallback() {
    super.attachedCallback();
    $('#propOptions').select2();
  }

  changeProperty() {
    var prop_name = $( "#propOptions option:selected" ).val();
    this.update({on: prop_name});
    updateChart(this.state);
  }
});

document.registerElement('date-picker', class datePicker extends Component {
  get config() {
    return {
      helpers: {
        toDateChange: () => this.changeToDate(),
        fromDateChange: () => this.changeFromDate(),
      },

      template:dateTemplate,
    };
  }

  attachedCallback() {
    super.attachedCallback();
    $(".toDatePicker").datepicker({maxDate: "+0D"}).val(moment().format("MM/DD/YYYY"));
    $(".fromDatePicker").datepicker({maxDate: "+0D"}).val(moment().subtract(30, 'days').format("MM/DD/YYYY"));
    this.update({to_date:moment().format("YYYY-MM-DD"), from_date:moment().subtract(30, 'days').format("YYYY-MM-DD")})
  }

  changeFromDate() {
    var date = moment($('.fromDatePicker').val(), "MM/DD/YYYY").format("YYYY-MM-DD")
    this.update({from_date:date});
    if ($('.fromDatePicker').val() > $('.toDatePicker').val()){
      if (moment($('.fromDatePicker').val(), "MM/DD/YYYY").add(7, 'days') > moment()) {
        $('.toDatePicker').val(moment().format("MM/DD/YYYY"));
        this.update({to_date:moment().format("YYYY-MM-DD")});
      } else {
        $('.toDatePicker').val(moment($('.fromDatePicker').val(), "MM/DD/YYYY").add(7, "days").format("MM/DD/YYYY"));
        this.update({to_date:moment($('.fromDatePicker').val(), "MM/DD/YYYY").add(7, "days").format("YYYY-MM-DD")});
      }
    }
    updateChart(this.state)
  }

  changeToDate() {
    var date = moment($('.toDatePicker').val(), "MM/DD/YYYY").format("YYYY-MM-DD");
    this.update({to_date:date});
    if ($('.fromDatePicker').val() > $('.toDatePicker').val()){
      $('.fromDatePicker').val(moment($('.toDatePicker').val(), "MM/DD/YYYY").subtract(7, "days").format("MM/DD/YYYY"));
      this.update({from_date:moment(moment($('.toDatePicker').val(), "MM/DD/YYYY").subtract(7, "days").format("YYYY-MM-DD"))});
    }
    updateChart(this.state)
  }

});

// for bar vs. line
// document.registerElement('chart-type', class chartType extends Component {
//   get config() {
//     return {
//       chartTypeTemplate,
//     };
//   }
// });

function populate_events(app_element){
  top_events(app_element.state.api_key, app_element.state.api_secret).done(function(data){
    $('#eventOptions').find('option').remove()
    if (Object.keys(data).length === 0){
      $('<option>No Data</option>').appendTo('#eventOptions')
    } else {
      _.each(data, function(value, key){
        $('<option>'+ key + '</option>').appendTo('#eventOptions')
      })
    }
    app_element.update({event:$("#eventOptions option:selected").text(), on:$("#propOptions option:selected").val()})
    updateChart(app_element.state)
  })
}
function updateChart(state){
  rickypanel.track("Report Viewed", {"prop1":state.event, "prop2":state.on, "prop3":state.api_key})
  var params = {};
  $.extend(params, state);
  var api_secret = state.api_secret;
  delete params.api_secret;
  if (params.on == "Undefined"){
    delete params.on;
  }
  segmentQuery(api_secret, params).done(function(data){
    var chart_data = lineChartData(data)
    var chart = new Highcharts.Chart({
          colors: ["#53a3eb", "#32BBBD", "#a28ccb", "#da7b80", "#2bb5e2", "#e8bc66", "#d390b6"],
          chart: {
            type: "line",
            renderTo: "chart"
          },
          title:{
            text:"Results"
          },
          xAxis: {
            categories: chart_data.xAxis
          },
          series: chart_data.series,
          yAxis: {
            min: 0
          }
        })
  })
}

function lineChartData(data){
  var xAxis = Object.keys(data).sort();
  var series = [];
  _.each(data[xAxis[0]], function(amount, name){
    var current = {name:name, data:[]};
    _.each(xAxis, function(day){
      current.data.push(data[day][name])
    })
    series.push(current)
  })
  return {xAxis:xAxis, series:series}
}

//should make these a class
function segmentQuery(api_secret, params){
  var expire = moment().unix() + 600
  params.expire = expire
  var sorted_params = Object.keys(params).sort()
  var args_joined = ""
  var url_params = ""
  _.each(sorted_params,function(key){
    args_joined += key + "=" + params[key];
    url_params += "&" + key + "=" + params[key];
  });
  args_joined = args_joined + api_secret
  var sig = md5(args_joined)
  url_params = url_params.slice(1) + "&sig=" + sig
  return $.ajax({
    url: "http://127.0.0.1:8000/segmentation/?" + url_params,
    // beforeSend: function(xhr) { 
    //   xhr.setRequestHeader("Authorization", "Basic " + authHeader); 
    // },
    type: 'GET',
    dataType: 'json',
    contentType: 'application/json',
  })
}

function top_events(api_key, api_secret){
  var expire = moment().unix() + 600
  var params = {api_key:api_key, expire:expire}
  var args_joined = "api_key=" + params.api_key + "expire=" + params.expire + api_secret
  var sig = md5(args_joined)
  var url_params= "api_key=" + params.api_key + "&expire=" + params.expire + "&sig=" + sig
  return $.ajax({
    url: "http://127.0.0.1:8000/events/?" + url_params,
    // beforeSend: function(xhr) { 
    //   xhr.setRequestHeader("Authorization", "Basic " + authHeader); 
    // },
    type: 'GET',
    dataType: 'json',
    contentType: 'application/json',
  })
}