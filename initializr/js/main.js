
var $query;
var $form;
var $result;

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

  $query.focus();
  $form
    .on('submit.do_search', function _on_submit_do_search (event) {
      event.preventDefault();
      handlers.search($query.val(), function _on_search_reply (result) {
        var i;
        var expand_id;
        for (i=0; i<result.length; ++i) {
          $result.append(views.movie_result(result[i]));
        }
      });
    })
    .trigger('submit');
});

var views = {
  movie_result: function movie_result_view (data) {
    var $container = jq_element('li');
    var $title = views.movie_title(data);
    var $info = jq_element('div');
    var url = 'javascript:void(0)';

    $title.on('click.expand_info', function _on_click_expand_info () {
      $info.toggle();
    });

    $info.
      hide().
      addClass('movie-info').
      html('<div>to be added l8er</div>' +
        '<a href="'+url+'" class="btn btn-primary pull-right">go to movie</a>' +
        '<div class="clearfix"></div>'
      );

    $container.append(
      jq_element('a').
        attr({
          'class': 'movie-wrapper',
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
      var range = 1;
      for (i=3; i<arguments.length; ++i) {
        cls = arguments[i];
        range *= multiplier;
        if (value < range) {
          break;
        }
      }
    }
    var likes_cls = get_value_class(data.likes, 1000, 'normal', 'thousands', 'millions');
    var rating_cls = get_value_class(data.rating, 'bad', 'good', 'great', 'excellent');
    return jq_element('div').
      addClass('movie-title').
      html(
        '<span class="name">'+data.name+'</span>' +
        '<div class="pull-right">' +
          (data.likes ? '<span class="likes tag '+likes_cls+'">'+
            '<i class="icon-thumbs-up"></i>'+' '+format_likes(data.likes)+
            '</span>' : '') +
          (data.rating ? '<span class="rating tag '+rating_cls+'">'+
            '<i class="icon-star"></i>'+' '+data.rating+'</span>' : '') +
        '</div>'
    );
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

  FB.getLoginStatus(function(response) {
    if (response.status === 'connected') {
      console.log('Access token:', FB.getAuthResponse()['accessToken']);
      do_login();
    } else if (response.status === 'not_authorized') {
      console.log('not authorized');
    } else {
      console.log('not logged in');
    }
  });
};

var init_globals = function init_globals () {
  $query = $('#query');
  $form = $('#query-form');
  $result = $('#result');
}

var do_login = function do_login () {
  var fields = 'id,name,link,cover,about,picture';
                //',movies.fields(id,name,likes,genre,link)' +
                //',friends.fields(id,name,movies.fields(id,name,likes,genre,link))';
  FB.api('/me?fields='+fields, function on_response (response){ 
    if (response.error) {
      console.warn(response.error);
    }
    var $profile = jq_element('div');
    $profile
      .attr({
        'class': 'pull-right'
      })
      .html(
        '<a href="'+response.link+'" target="_blank">' +
          '<img src="'+response.picture.data.url+'" width="40" alt="fb_pic" />' +
          '<span class="user_name">'+response.name+'</span>' +
        '</a>'
      );
    $('#fb-login').replaceWith($profile);
  });
};

var jq_element = function jq_element (type) {
  return $(document.createElement(type));
};