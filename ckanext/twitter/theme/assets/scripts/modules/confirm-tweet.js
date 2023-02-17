ckan.module('confirm-tweet', function ($, _) {
  var self;

  return {
    initialize: function () {
      self = this;
      self.options.disable_edit = self.options.disable_edit === 'True';
      self.sandbox.client.getTemplate(
        'edit_tweet.html',
        self.options,
        self._onReceiveSnippet,
      );
    },

    _onReceiveSnippet: function (html) {
      var sendUrl = '/dataset/' + self.options.pkgid + '/tweet';
      var clearUrl = '/dataset/' + self.options.pkgid + '/tweet-clear';
      self.block = $(html);
      var form = self.block.find('#edit-tweet-form');
      form.submit(function (e) {
        e.preventDefault();

        $.post(
          sendUrl,
          form.serialize(),
          function (results) {
            let message;
            if (results === undefined || results === null) {
              message =
                '<i class="fas fa-times inline-icon-left"></i> Unknown error';
              self.flash_error('Tweet not posted due to unknown error.');
            } else if (!results.success) {
              message =
                '<i class="fas fa-times inline-icon-left"></i> Not posted: ' +
                results.reason;
              self.flash_error(
                'Tweet not posted! Error message: "' +
                  results.reason +
                  '".<br>Your tweet: "' +
                  results.tweet +
                  '".',
              );
            } else {
              message =
                '<i class="fas fa-check inline-icon-left"></i> Posted: ' +
                results.tweet;
              self.flash_success('Tweet posted!');
            }
            $('#edit-tweet-form').replaceWith(`<div>${message}</div>`);
          },
          'json',
        );
      });

      let cancelButton = self.block.find('#edit-tweet-cancel');
      cancelButton.click(function (e) {
        $.post(clearUrl, {}, function () {
          self.block.remove();
        });
      });

      $('#ckanext-twitter-placeholder').replaceWith(self.block);
    },

    flash: function (message, category) {
      $('.flash-messages').append(
        '<div class="alert ' + category + '">' + message + '</div>',
      );
    },

    flash_error: function (message) {
      this.flash(message, 'alert-error');
    },

    flash_success: function (message) {
      this.flash(message, 'alert-success');
    },
  };
});
