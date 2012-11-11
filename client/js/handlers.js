var handlers = {
  search: function search_handler (query, callback) {
    $.get(options.urls.search, {
      q: query,
      tags: tags
    }, callback);
  }
};