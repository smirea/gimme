
var options = {
  urls: {
    search: 'http://localhost:8000/api/query',
    login: 'http://localhost:8000/api/login',
    friend_list: 'http://localhost:8000/api/friend_list',
    cinemas: 'http://localhost:8000/api/cinema'
  }
};

var $query;
var $form;
var $result;
var $single_view;
var $map;
var friends = {};
var friend_names = [];

var map;
var infowindow;
var markers = [];
var cinemas = {};

// all names ever tagged in the query field
var tags = [];

// load facebook JS SDK
(function() {
  if (!window.userData) {
    var e = document.createElement('script');
    e.type = 'text/javascript';
    e.src = document.location.protocol +
        '//connect.facebook.net/en_US/all.js';
    e.async = true;
    document.getElementById('fb-root').appendChild(e);
  }
}());

$(function _on_document_load () {
  init_globals();
  load_friends();
  setup_ui();
  setup_typeahead();

  $form
    .on('submit.do_search', function _on_submit_do_search (event) {
      event.preventDefault();
      $result.empty();
      handlers.search($query.val(), function _on_search_reply (result) {
        var i;
        var expand_id;
        if (result.length > 0) {
          result[0].guru = {
            name: 'Corneliu Prodescu',
            picture: 'http://graph.facebook.com/1068801676/picture',
            type: 'general'
          };
          /* hack not necessary anymore :)
          if (result.length > 1) {
            var index = 1 + Math.floor(Math.random() * result.length - 1);
            result[index].friends_recommended = Math.floor(Math.random() * 300);
          }
          */
        }
        for (i=0; i<result.length; ++i) {
          $result.append(views.movie_result(result[i]));
        }
      });
    });
});

var views = {
  search_view: function search_view () {
    $single_view.slideDown('normal', function () {
      $form.show().css({
        opacity: 1
      });
    });
  },
  single_view: function single_view (data) {
    var old = {
      marginTop: $form.css('margin-top')
    };
    $form.animate({
      marginTop: 0,
      opacity: 0
    }, 600, function () {
      $form.hide().css(old);
    });
    $single_view.
      fadeIn(400).
      append(
        '<table>'+
          '<tr><td colspan="2" style="font-size:20pt">'+data.name+'</td></tr>'+
          '<tr><td><b>rating</b></td><td>'+data.rating+'</td></tr>'+
          '<tr><td><b>friend likes</b></td><td>'+data.friends_recommended.length+'</td></tr>'+
          '<tr><td><b>rating</b></td><td>'+data.rating+'</td></tr>'+
        '</table>'+
        '<div>'+data.description+'</div>'+
        '<div>'+data.taglines.join('<br />')+'</div>'+
        '<img src="/static/img/netflix.jpg" />'+
        '<img src="/static/img/amazon.jpg" />',
        $map
    )
    setup_map(data);
  },
  movie_result: function movie_result_view (data) {
    var $container = jq_element('li');
    var $title = views.movie_title(data);
    var $info = jq_element('div');
    var $facepile = jq_element('div');
    var url = 'javascript:void(0)';
    var i;

    $title.on('click.expand_info', function _on_click_expand_info () {
      $('.search-result .movie-info').hide();
      $info.toggle();
    });

    var $movie_link = jq_element('a');
    $movie_link.
      attr({
        href: url,
        'class': 'btn btn-primary pull-right'
      }).
      html('go to movie').
      on('click.single_view', function _on_click_single_view () {
        views.single_view(data);
      });

    if (data.friends_recommended) {
      for (i=0; i<data.friends_recommended.length; ++i) {
        var fr = data.friends_recommended[i];
        $facepile.append(
          jq_element('a').attr({
            href: 'http://facebook.com/' + fr.fbid,
            target: '_blank',
            title: fr.name
          }).append(
            jq_element('img').
              attr('src', 'http://graph.facebook.com/'+fr.fbid+'/picture')
          )
        );
      }
    }

    $info.
      hide().
      addClass('movie-info').
      append('<div>'+(data.taglines.length > 0 ? data.taglines[0] : '')+'</div>',
        $movie_link,
        $facepile
      );

    $container.
      addClass('search-result').
      append(
        jq_element('a').
          attr({
            'class': 'movie-wrapper '+
              (data.guru ? 'guru-recommended ' : '') +
              (data.friends_recommended && data.friends_recommended.length > 0 ? 'friends-recommended' : ''),
            href: 'javascript:void(0)'
          }).append(
            $title,
            jq_element('div').addClass('clearfix'),
            $info
          )
      );
    return $container;
  },
  movie_title: function movie_title_view (data) {
    var format_likes = function format_likes (likes) {
      if (!likes) {
        return 0;
      } else if (likes < 1000) {
        return likes;
      } else if (likes < 1000 * 1000) {
        return (Math.floor(likes / 1000 * 10) / 10) + 'K';
      }
      return (Math.floor(likes / 1000 / 1000 * 10) / 10) + 'M';
    };
    var get_value_class = function get_value_class (value, multiplier) {
      var cls;
      var i;
      var range = multiplier;
      for (i=2; i<arguments.length; ++i) {
        cls = arguments[i];
        if (value < range) {
          break;
        }
        range *= multiplier;
      }
      return cls;
    }
    var likes_cls = get_value_class(data.likes, 1000, 'normal', 'thousands', 'millions');
    var $container = jq_element('div');
    var $wrapper = jq_element('div').addClass('pull-right');

    if (data.rating) {
      $container.append(
        jq_element('span').
          addClass('likes tag').
          append('<span class="rating">'+data.rating+'</span>')
      );
    }

    $container.append(
      jq_element('span').addClass('name').html(data.name)
    );

    if (data.friends_recommended && data.friends_recommended.length > 0) {
      $wrapper.append(
        data.friends_recommended.length,
        jq_element('i').
          addClass('icon-user has-tooltip').
          attr('title', data.friends_recommended.length +' friends recommended this')
      );
    }
    if (data.guru) {
     $wrapper.append(
        jq_element('img').
          addClass('has-tooltip').
          attr({
            src: data.guru.picture,
            width: 22,
            title: 'Recommended by you '+data.guru.type+' guru'
          })
      );
    }
    if (data.likes) {
      $wrapper.append(
        jq_element('span').
          addClass('likes tag '+likes_cls).
          append('<i class="icon-thumbs-up"></i>'+' '+format_likes(data.likes))
      );
    }
    $container.
      addClass('movie-title ').
      append($wrapper).
      find('.has-tooltip').tooltip();
    return $container;
  }
};

// init facebook functions
window.fbAsyncInit = function() {
  // init the FB JS SDK
  FB.init({
    appId      : '249579318504154', // App ID from the App Dashboard
    status     : true, // check the login status upon init?
    cookie     : true, // set sessions cookies to allow your server to access the session?
    xfbml      : true  // parse XFBML tags on this page?
  });

  FB.Event.subscribe('auth.login', function(response) {
    if (response.status === 'connected') {
      console.log('Access token:', response.authResponse.accessToken);
      console.log('UserID:', response.authResponse.userID);
      do_login(response);
    } else if (response.status === 'not_authorized') {
      console.log('not authorized');
    } else {
      console.log('not logged in');
    }
  });

  FB.getLoginStatus(function(response) {
    if (response.status === 'connected') {
      console.log('Access token:', response.authResponse.accessToken);
      console.log('UserID:', response.authResponse.userID);
      if (!window.userData) {
        do_login(response);
      }
    } else if (response.status === 'not_authorized') {
      console.log('not authorized');
    } else {
      console.log('not logged in');
    }
  });
};

function createMarker(place) {
  var placeLoc = place.geometry.location;
  var marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location
  });

  google.maps.event.addListener(marker, 'click', function() {
    console.log(JSON.stringify(place, null, 2));
    infowindow.setContent(
      '<img src="' + place.icon + '" height="32" style="float:left; margin: 3px 5px 0 0" />' +
      '<b>' + place.name + '</b>' +
      '<div>' + place.vicinity + '</div>'
    );
    infowindow.open(map, this);
  });
}

var setup_typeahead = function setup_typeahead () {
  var last_start = -1;
  var last_end = -1;
  $query
    .focus()
    .typeahead({
      source: function _query_typehead_source () {
        return friend_names;
      },
      matcher: function (item) {
        var caret = $query.caret();
        var caret_end = Math.max(caret.start, caret.end);
        var str = $query.val();
        var name_start = str.lastIndexOf('@', caret_end);
        if (name_start > -1) {
          str = str.slice(name_start + 1, caret_end);
          last_start = name_start;
          if (str.length > 1) {
            last_end = caret_end;
            return (new RegExp(str, 'i')).test(item);
          }
        }
        return false;
      },
      updater: function (item) {
        tags.push(friends[item].id);
        var value = $query.val();
        return value.slice(0, last_start) + '@' + item + ' ' + value.slice(last_end);
      },
      highlighter: function (item) {
        return '<img src="https://graph.facebook.com/'+
                  friends[item].fb_id+
                '/picture" width="20"/> '+item;
      }
    });
}

var setup_ui = function setup_ui () {
  if (window.userData) {
    var $profile = jq_element('div');
    $profile
      .attr({
        'class': 'pull-right'
      })
      .html(
        '<a href="http://facebook.com/'+userData.fbid+'" target="_blank">' +
          '<span class="user_name">'+userData.first_name+' '+
              userData.last_name+' </span>' +
          '<img src="http://graph.facebook.com/'+userData.fbid+'/picture" width="40" alt="fb_pic" />' +
        '</a>'
      );
    $('#fb-login').replaceWith($profile);
  }
}

var load_friends = function load_friends () {
  $.get(options.urls.friend_list, function _get_friends (response) {
    var fr;
    var i;
    if (typeof response == 'string') {
      fr = JSON.parse(response);
    } else {
      fr = response;
    }
    for (i=0; i<fr.length; ++i) {
      friends[fr[i].name] = fr[i];
      friend_names.push(fr[i].name);
    }
  });
}

var init_globals = function init_globals () {
  $query = $('#query');
  $form = $('#query-form');
  $result = $('#result');
  $single_view = $('#single-view');
  $map = $('#map');
}

var do_login = function do_login (response) {
  $.post(options.urls.login, {
    fb_id: response.authResponse.userID,
    fb_token: response.authResponse.accessToken
  },
  function on_login (reply) {
    console.log(reply);
  });
};

var jq_element = function jq_element (type) {
  return $(document.createElement(type));
};

function setup_map (data) {
  
  map = new google.maps.Map(document.getElementById('map'), {
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    zoom: 10
  });

  set_location();
  
  $.get(options.urls.cinemas, {
    q: data.name
  }, function (response) {
    for (var day in response) {
      for (var name in response[day]) {
        if (cinemas[name]) {
          console.log('ok', name);
          (function (place) {
            google.maps.event.addListener(marker, 'click', function() {
              infowindow.setContent(
                
              );
              infowindow.open(map, this);
            });
          })(response[day][name]);
        } else {
          console.warn('fail', response[i].name);
        }
      }
    }
  });

  function set_location () {
    GeoMarker = new GeolocationMarker();
    GeoMarker.setCircleOptions({
      fillColor: '#808080'
    });

    google.maps.event.addListenerOnce(GeoMarker, 'position_changed', function(){
      map.setCenter(this.getPosition());
      get_nearby_cinemas(this.getPosition());
    });

    google.maps.event.addListener(GeoMarker, 'geolocation_error', function(e) {
      console.warn('Could not get geolocation: ' + e.message);
    });

    GeoMarker.setMap(map);
  }
}

function get_nearby_cinemas (position) {
  var request = {
    location: position,
    radius: 12 * 1000,
    types: ['movie_theater']
  };
  infowindow = new google.maps.InfoWindow();
  var service = new google.maps.places.PlacesService(map);
  service.nearbySearch(request, function callback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
      cinemas = {};
      for (var i = 0; i < results.length; i++) {
        cinemas[results[i].name] = results[i];
        createMarker(results[i]);
      }
      console.log(cinemas);
    }
  });
}

function createMarker(place) {
  var placeLoc = place.geometry.location;
  var marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location
  });

  markers.push(marker);

  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent(
      '<img src="' + place.icon + '" height="32" style="float:left; margin: 3px 5px 0 0" />' +
      '<b>' + place.name + '</b>' +
      '<div>' + place.vicinity + '</div>'
    );
    infowindow.open(map, this);
  });
}