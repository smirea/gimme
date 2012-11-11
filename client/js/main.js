
var options = {
  urls: {
    search: 'http://localhost:8000/api/query',
    login: 'http://localhost:8000/api/login',
    friend_list: 'http://localhost:8000/api/friend_list'
  }
};

var $query;
var $form;
var $result;
var friends = {};
var friend_names = [];

// all names ever tagged in the query field
var tags = [];

// load facebook JS SDK
(function() {
  var e = document.createElement('script');
  e.type = 'text/javascript';
  e.src = document.location.protocol +
      '//connect.facebook.net/en_US/all.js';
  e.async = true;
  document.getElementById('fb-root').appendChild(e);
}());

$(function _on_document_load () {
  init_globals();
  load_friends();
  setup_ui();

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
          if (str.length > 2) {
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

  $form
    .on('submit.do_search', function _on_submit_do_search (event) {
      event.preventDefault();
      $result.empty();
      handlers.search($query.val(), function _on_search_reply (result) {
        var i;
        var expand_id;
        for (i=0; i<result.length; ++i) {
          $result.append(views.movie_result(result[i]));
        }
      });
    });
});

var views = {
  movie_result: function movie_result_view (data) {
    var $container = jq_element('li');
    var $title = views.movie_title(data);
    var $info = jq_element('div');
    var url = 'javascript:void(0)';

    $title.on('click.expand_info', function _on_click_expand_info () {
      $('.search-result .movie-info').hide();
      $info.toggle();
    });

    $info.
      hide().
      addClass('movie-info').
      html('<div>to be added l8er</div>' +
        '<a href="'+url+'" class="btn btn-primary pull-right">go to movie</a>' +
        '<div class="clearfix"></div>'
      );

    $container.
      addClass('search-result').
      append(
        jq_element('a').
          attr({
            'class': 'movie-wrapper '+
              (data.guru ? 'guru-recommended ' : '') +
              (data.friends_recommended ? 'friends-recommended' : ''),
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

    if (data.friends_recommended) {
      $wrapper.append(
        jq_element('i').
          addClass('icon-user has-tooltip').
          attr('title', data.friends_recommended+' friends recommended this')
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
    } else if (response.status === 'not_authorized') {
      console.log('not authorized');
    } else {
      console.log('not logged in');
    }
  });
};

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