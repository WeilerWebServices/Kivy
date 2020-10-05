module.exports = {
  perform: !process.env.DRY_RUN,
  subscriptions: [
    {
      events: {labeled: 'mclabel'},
      issue: 1,
      comment:
        'This is a notification for [{issue-title}]({issue-url}), ' +
        'opened by @{issue-author}.'
    }
  ]
};
